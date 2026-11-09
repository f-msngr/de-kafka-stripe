from fastapi import APIRouter


# ===============================
# Logging
# ================================
import os
import logging

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# ===============================
# Router
# ===============================
ml_router = APIRouter()
# Context

# ===============================
# ENV
# ===============================
DBT_MARTS = os.environ["DBT_MARTS"]


# ===============================
# ML endpoints
# ===============================
from fastapi import HTTPException, Request, Response
from .libs import get_clickhouse_client

d_VIEWS = {"train": "view_train"}  # nom réel des vues dbt autorisées à l'appel

@ml_router.get(
    "/views/{view}",
    response_class=Response,
    responses={200: {"content": {"application/vnd.apache.parquet": {}}, "description": "Fichier Parquet"}},
    include_in_schema=False)
async def get_view(view: str, request: Request):
    """Renvoie en Parquet le contenu d'une vue dbt autorisée.
    - `view` : clé de la vue dans `d_VIEWS` (liste blanche), sinon 404.
    - vues autorisées : `train`
    - Le client ClickHouse est celui créé au démarrage (lifespan) et stocké
      dans `app.state`; il est récupéré via `request`.
    - Exécute `SELECT * FROM <vue>` ; ClickHouse produit le Parquet, renvoyé tel quel.
    """
    if view not in d_VIEWS:
        raise HTTPException(status_code=404, detail="Vue inconnue")
    
    client = get_clickhouse_client(request)
    
    data = await client.raw_query(
        f"SELECT * FROM {DBT_MARTS}.{d_VIEWS[view]}",
        fmt="Parquet",   # produit par Clickhouse
        #settings={"output_format_parquet_string_as_string": 1},  # texte écrit comme texte, et non comme binaire
        )
    
    # Parquet est de type bytes, il faut éviter que fastapi essaie de le convertir en json
    return Response(content=data, media_type="application/vnd.apache.parquet")


@ml_router.get(
    "/info/views/{view}",
    response_class=Response,
    responses={200: {"content": {"application/json": {}}, "description": "Query response in json"}},
    include_in_schema=True)
async def get_count_view(view: str, request: Request):
    """Renvoie le nombre de lignes d'une vue autorisée
    - `view` : clé de la vue dans `d_VIEWS` (liste blanche), sinon 404.
    - vues autorisées : `train`
    - Le client ClickHouse est celui créé au démarrage (lifespan) et stocké
      dans `app.state`; il est récupéré via `request`.
    - Exécute `SELECT * FROM <vue>` ;
    """
    if view not in d_VIEWS:
        raise HTTPException(status_code=404, detail="Vue inconnue")
    
    client = get_clickhouse_client(request)

    data = await client.raw_query(
        f"SELECT count(*) FROM {DBT_MARTS}.{d_VIEWS[view]}",
        fmt="JSON",
        )

    return Response(content=data, media_type="application/json")