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
analytics_router = APIRouter()
# Context

# ===============================
# ENV
# ===============================
DBT_MARTS = os.environ["DBT_MARTS"]


# ===============================
# analytics endpoints
# ===============================
from fastapi import HTTPException, Request, Response
from .libs import get_clickhouse_client

d_FACTS = {
    "frauds": "fct_frauds",
    "predictions": "fct_predictions",
    "reviews": "fct_reviews",
    "transactions": "fct_transactions",
    }  # nom réel des vues/tables dbt autorisées à l'appel

@analytics_router.get(
    "/facts/{fact}",
    response_class=Response,
    responses={200: {"content": {"application/json": {}}, "description": "Query response in json"}},
    include_in_schema=False)
async def get_fct(fact: str, request: Request):
    """Renvoie en json le contenu d'une vue/table dbt autorisée.

    - `fact` : clé de la vue/table dans `d_FACTS` (liste blanche), sinon 404.
    - Le client ClickHouse est celui créé au démarrage (lifespan) et stocké
      dans `app.state`; il est récupéré via `request`.
    - Exécute `SELECT * FROM <fact>` ; ClickHouse produit le json, renvoyé tel quel.
    """
    if fact not in d_FACTS:
        raise HTTPException(status_code=404, detail="Fait inconnu")
    
    client = get_clickhouse_client(request)
    
    data = await client.raw_query(
        f"SELECT * FROM  {DBT_MARTS}.{d_FACTS[fact]}",
        fmt="JSONCompact",   # produit par Clickhouse
        #settings={"output_format_parquet_string_as_string": 1},  # texte écrit comme texte, et non comme binaire
        )
    
    # Réponse à la requête au format json
    return Response(content=data, media_type="application/json")