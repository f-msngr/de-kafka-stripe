
# ============================================
# ENV + VAR CONF
# ============================================
import os
from dotenv import load_dotenv
load_dotenv()

URL_API = os.environ["URL_API"]
MAX_CONCURRENCY = 20              # requêtes simultanées maximum
MAX_RETRIES = 3                   # essais par transaction

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
# PRODUCE PAYLOAD
# ============================================
import uuid
from datetime import datetime, timezone

def build_tnx() -> dict:
    """Seule fonction à modifier quand le contenu de la transaction évolue."""
    #return {"uuid": str(uuid.uuid4()), "ts": datetime.now(timezone.utc).isoformat()}
    return {"uuid": str(uuid.uuid4()), "ts": "BOUM"}

# ============================================
# POST
# ============================================
import httpx
import asyncio

logger.info(f"URL_API : {URL_API}")

async def post_one_tnx(client: httpx.AsyncClient, sem: asyncio.Semaphore, tnx: dict) -> bool:
    """Envoie un dict à /ingest. True si l'API l'a accepté (202), sinon False."""
    async with sem:
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                resp = await client.post(f"{URL_API}/ingest", json=tnx)
                if resp.status_code == 202:
                    logger.info(f"🌠 POST /ingest → {resp.status_code}")
                    return True
                if resp.status_code < 500 and resp.status_code >= 400:   # 4xx : le dict est refusé, réessayer ne sert à rien
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
    async with httpx.AsyncClient(timeout=10) as client:   # créé une fois, fermé à la fin
        l_tnx = [build_tnx() for _ in range(30)]
        results = await post_many_tnx(client, l_tnx)
    logger.info(f"🌠 {sum(results)}/{len(results)} transactions acceptées")


if __name__ == "__main__":
    asyncio.run(main())   # démarre la boucle asynchrone et exécute main()