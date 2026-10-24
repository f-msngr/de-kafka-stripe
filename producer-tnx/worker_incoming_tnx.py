# ============================================
# ENV + VAR CONF
# ============================================
import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

URL_API = os.environ["URL_API"]
URL_FEED = os.environ["URL_FEED"]
SETTINGS_FILE = Path(__file__).with_name("settings.json")   # modifié à la main, relu avant chaque lot
STATE_FILE = Path("/tmp/producer_state")                    # écrit par feedctl : "start" ou "halt"
MAX_CONCURRENCY = 20              # requêtes simultanées maximum
MAX_RETRIES = 3                   # essais par transaction
BATCH_WAIT = 2                    # secondes entre deux lots
POLL_WAIT = 1                     # secondes entre deux lectures de l'état pendant un halt
MAX_STREAM_RETRIES = 5            # reconnexions de suite autorisées sans lire une seule ligne
STREAM_RETRY_WAIT = 2             # secondes avant de se reconnecter
l_COL_DROP = ["column00", "unix_time"]        # colonnes retirées de chaque transaction
COL_MERCHANT = "merchant"         # colonne du nom du marchand : à comparer à l'en-tête de feed.csv
FRAUD_PREFIX = "fraud_"

# ============================================
# LOGGING
# ============================================
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================
# CONTROL (réglages et état, relus avant chaque lot)
# ============================================
import json
import asyncio

_last_settings = None   # dernières valeurs valides de settings.json

def load_settings() -> dict | None:
    """Relit settings.json. Absent ou invalide : garde les dernières valeurs valides (None si jamais lu)."""
    global _last_settings
    try:
        data = json.loads(SETTINGS_FILE.read_text())
        settings = {"batch_size": int(data["batch_size"]), "fraud_percent": float(data["fraud_percent"])}
        if settings["batch_size"] < 1 or not 0 <= settings["fraud_percent"] <= 100:
            raise ValueError("valeur hors limites")
        _last_settings = settings
    except (OSError, ValueError, KeyError, TypeError) as e:
        logger.warning(f"⚠️ settings.json inutilisable ({e}) : dernières valeurs conservées")
    return _last_settings

def read_state() -> str:
    """Tout ce qui n'est pas 'start' (fichier absent compris) est un halt."""
    try:
        return STATE_FILE.read_text().strip()
    except OSError:
        return "halt"

async def wait_until_start():
    """Attend que l'état soit 'start', relu toutes les POLL_WAIT secondes."""
    waiting = False
    while read_state() != "start":
        if not waiting:
            logger.info("⏸️ halt : en attente de 'start'")
            waiting = True
        await asyncio.sleep(POLL_WAIT)
    if waiting:
        logger.info("▶️ start")

# ============================================
# READ FEED (lots en mémoire)
# ============================================
import csv
import httpx

STREAM_ERRORS = (httpx.ReadError, httpx.RemoteProtocolError, httpx.ReadTimeout, httpx.ConnectError)

async def stream_lines(client: httpx.AsyncClient):
    """Renvoie les lignes de URL_FEED une par une. Si S3 coupe la connexion, se reconnecte et reprend là où on s'était arrêté."""
    offset = 0      # nombre d'octets des lignes complètes déjà renvoyées
    failures = 0    # coupures de suite sans progrès
    while True:
        headers = {"Range": f"bytes={offset}-"} if offset else {}   # reprise à l'octet offset
        try:
            async with client.stream("GET", URL_FEED, headers=headers) as resp:
                resp.raise_for_status()
                if offset and resp.status_code != 206:             # 206 = "contenu partiel", la reprise a marché
                    raise RuntimeError(f"reprise à l'octet {offset} refusée (HTTP {resp.status_code})")
                buffer = b""                                        # morceau de ligne pas encore terminé
                async for chunk in resp.aiter_bytes():
                    buffer += chunk
                    while (pos := buffer.find(b"\n")) != -1:
                        raw, buffer = buffer[:pos], buffer[pos + 1:]
                        offset += pos + 1                           # +1 = le "\n"
                        failures = 0
                        yield raw.decode("utf-8").rstrip("\r")
                if buffer.strip():                                  # dernière ligne sans "\n" final
                    offset += len(buffer)
                    yield buffer.decode("utf-8").rstrip("\r")
                return                                              # fichier lu en entier
        except STREAM_ERRORS as e:
            failures += 1
            if failures > MAX_STREAM_RETRIES:
                raise
            logger.warning(f"⚠️ flux coupé ({type(e).__name__}) : reprise à l'octet {offset} (essai {failures})")
            await asyncio.sleep(STREAM_RETRY_WAIT)

async def read_batches(client: httpx.AsyncClient):
    """Lit feed.csv en flux et renvoie des lots (dicts). Avant chaque lot : attend 'start', relit batch_size."""
    header = None
    batch = []
    size = None
    async for line in stream_lines(client):
        if not line:
            continue
        values = next(csv.reader([line]))   # une ligne = une transaction (pas de retour à la ligne dans un champ)
        if header is None:
            header = values
            continue
        if size is None:                    # début d'un nouveau lot
            await wait_until_start()
            size = load_settings()["batch_size"]
        batch.append(dict(zip(header, values)))
        if len(batch) >= size:
            yield batch
            batch = []
            size = None
    if batch:
        yield batch

# ============================================
# PRODUCE PAYLOAD
# ============================================
import random
import uuid

def build_tnx(row: dict) -> dict:
    """Ligne du CSV -> transaction à envoyer : retire les colonnes de l_COL_DROP, ajoute un uuid."""
    tnx = {k: v for k, v in row.items() if k not in l_COL_DROP}
    tnx["uuid"] = str(uuid.uuid4())
    return tnx

def make_fraudulent(tnx: dict) -> dict:
    """Masque de fraude synthétique. Préfixe sur le nom du marchand + autres colonnes."""
    tnx[COL_MERCHANT] = FRAUD_PREFIX + tnx[COL_MERCHANT]
    tnx["amt"] = float(tnx["amt"]) *10000
    return tnx

def inject_fraud(batch: list[dict], fraud_percent: float) -> int:
    """Rend frauduleuses fraud_percent % des transactions du lot, tirées au hasard. Renvoie leur nombre."""
    n = round(len(batch) * fraud_percent / 100)
    for i in random.sample(range(len(batch)), n):
        make_fraudulent(batch[i])
    return n

# ============================================
# POST
# ============================================
async def post_one_tnx(client: httpx.AsyncClient, sem: asyncio.Semaphore, tnx: dict) -> bool:
    """Envoie un dict à /ingest. True si l'API l'a accepté (202), sinon False."""
    async with sem:
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                resp = await client.post(f"{URL_API}/ingest", json=tnx)
                if resp.status_code == 202:
                    return True
                if 400 <= resp.status_code < 500:   # 4xx : le dict est refusé, réessayer ne sert à rien
                    logger.error(f"❌ Refusé {resp.status_code} : {resp.text}")
                    return False
                logger.warning(f"⚠️ Erreur serveur {resp.status_code} (essai {attempt})")
            except httpx.HTTPError as e:     # réseau coupé, timeout...
                logger.warning(f"⚠️ {type(e).__name__} (essai {attempt})")
            await asyncio.sleep(0.5 * 2 ** (attempt - 1))   # pauses : 0,5 s, 1 s, 2 s
        return False

async def post_many_tnx(client: httpx.AsyncClient, l_tnx: list[dict]) -> list[bool]:
    sem = asyncio.Semaphore(MAX_CONCURRENCY)
    return await asyncio.gather(*(post_one_tnx(client, sem, tnx) for tnx in l_tnx))


async def main():
    STATE_FILE.write_text("halt")                    # état initial à chaque démarrage
    if load_settings() is None:
        raise SystemExit("settings.json absent ou invalide au démarrage")
    n_read = n_ok = n_fraud = 0
    async with httpx.AsyncClient(timeout=10) as client:   # créé une fois, fermé à la fin
        async for batch in read_batches(client):
            l_tnx = [build_tnx(row) for row in batch]
            n_fraud_batch = inject_fraud(l_tnx, load_settings()["fraud_percent"])
            results = await post_many_tnx(client, l_tnx)
            n_read += len(l_tnx)
            n_ok += sum(results)
            n_fraud += n_fraud_batch
            logger.info(f"🌠 lot : {sum(results)}/{len(results)} acceptées, dont {n_fraud_batch} frauduleuses")
            await asyncio.sleep(BATCH_WAIT)
    logger.info(f"🏁 fin du fichier : {n_ok}/{n_read} acceptées, {n_fraud} frauduleuses")


if __name__ == "__main__":
    asyncio.run(main())   # démarre la boucle asynchrone, s'arrête à la fin du fichier