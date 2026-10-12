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

async def read_batches(client: httpx.AsyncClient):
    """Lit feed.csv en flux et renvoie des lots (dicts). Avant chaque lot : attend 'start', relit batch_size."""
    header = None
    batch = []
    size = None
    async with client.stream("GET", URL_FEED) as resp:
        resp.raise_for_status()
        async for line in resp.aiter_lines():
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