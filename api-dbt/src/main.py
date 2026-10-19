import os
import asyncio

from fastapi import FastAPI, HTTPException

# ================================================
# Logging
# ================================================
import logging

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# ================================================
# Main app
# ================================================
# Set root_path for nginx
app = FastAPI(
    # root_path="/api-dbt", # cible pour nginx - désactivée
    title="📬 DBT control API",
    description="API used for controlling dbt on dedicated endpoints",
    version="1.0.0"
    )

@app.get("/")
async def get_root():
    return {"message": "🦫 DBT service -> Working class hero"}

@app.get("/health")
async def get_health():
    return {"status": "ok"}


# ================================================
# DBT Control endpoints
# ================================================
import json
from pathlib import Path
from uuid import uuid4
import time
from datetime import datetime, timezone

STATUS = Path(os.environ["DBT_RUN_STATUS_FILE"])
PROJECT_DIR = os.environ["DBT_PROJECT_DIR"]       # Relative path to status.json

# IMPORTANT
# Conserver une référence des tâches créées
# pour éviter que Python supprime les subprocess
s_tasks = set()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _load_status() -> dict | None:
    """Lit status.json."""
    try:
        return json.loads(STATUS.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.warning(f"⚠️ status.json inutilisable ({e})")
        return None

# Eviter une éventuelle lecture du fichier
# pendant l'écriture par un autre processus
def _save_status(d_status: dict) -> None:           # écriture atomique : fichier temporaire, puis remplacement
    tmp = STATUS.with_suffix(".tmp")
    tmp.write_text(json.dumps(d_status), encoding="utf-8") # dict transformé en string 
    os.replace(tmp, STATUS)

# =====================
# API INIT
# =====================
# Au démarrage de fastapi, si un fichier status.json existe avec un status "running"
# c'est qu'il provient d'un processus qui est mort
# On modifie la valeur du status pour annuler ce status incohérent
def _set_status_for_dead_process():
    d_status = _load_status()
    if d_status is None:                                  # fichier absent ou illisible
        d_status = {"run_id": "1", "status": "init", "started_at": None, "finished_at": None, "duration_s": None}
        logger.warning("⚠️ status.json créé")
        _save_status(d_status)
    elif d_status.get("status") == "running":             # run mort avec l'ancien processus
        d_status["status"] = "interrupted"
        logger.warning(f"⚠️ run {d_status.get('run_id')} interrompu par un redémarrage")
        _save_status(d_status)
    else:
        return None                                           # état cohérent : rien à écrire

# Execution à l'import du module cad au démarrage d'uvicorn
_set_status_for_dead_process()



# _launch_task asynchrone car contient await
async def _launch_task(run_id: str, started_at: str) -> None:
    """ Lance une tâche non bloquante en subprocess :
    lance dbt run
    avec le répertoire où se trouve dbt_project.yml
    et redirige les logs du subprocess python sur dev/null car dbt a ses propres logs
    et update le statut du run à la fin de son exécution ()  
    """
    # status = failed par défaut
    status = "failed"
    start_time = time.monotonic()
    
    try:
        # Définir un processus non bloquant
        proc = await asyncio.create_subprocess_exec(
            "dbt", "run",
            "--project-dir", PROJECT_DIR,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL
            )
        # tester le résultat à la fin
        if await proc.wait() == 0:
            status = "success"
    finally:
        _save_status({
            "run_id": run_id,
            "status": status,
            "started_at": started_at,
            "finished_at": _now(),
            "duration_s": round(time.monotonic() - start_time, 1),
            })
    
    

@app.post("/run", status_code=202)
async def post_run():
    """
    Lance dbt run :
    teste s'il n'y pas déjà un autre run en cours
    crée une tâche en sous process asynchrone
    """
    d_status = _load_status()
    if d_status and d_status.get("status") == "running":
        raise HTTPException(status_code=409, detail="run en cours")
    run_id = uuid4().hex
    started_at = _now()
    
    # D'abord enregistrer le status de la tâche créée
    _save_status({
        "run_id": run_id,
        "status": "running",
        "started_at": started_at,
        "finished_at": None,
        "duration_s": None
        })
    
    # Lancer l'execution de dbt en tâche de fond, non bloquante
    # Associer le sous process à une tâche pour suivi
    # asyncio.create_task(TACHE)
    task = asyncio.create_task(_launch_task(run_id, started_at))
    s_tasks.add(task)
    # Supprimer la tâche une fois terminée
    task.add_done_callback(s_tasks.discard)
    
    return {"run_id": run_id}


@app.get("/runs/{run_id}")
async def get_run(run_id):
    """ Renvoie le json status.json"""
    d_status = _load_status()
    if d_status is None or d_status.get("run_id") != run_id:
        raise HTTPException(status_code=404, detail="run inconnu")
    return d_status          # {"run_id": ..., "status": "running" | "success" | "failed" | "interrupted" | "init"}