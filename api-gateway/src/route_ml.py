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



# ===============================
# ML entry point
# ===============================
from fastapi import HTTPException, Request, Response

d_VIEWS = {"train": "view_train"}  # nom réel des vues dbt autorisées à l'appel


def _get_clickhouse_client(request: Request):
    """ Retourne le client ClickHouse stocké dans app.state.clickhouse. """
    return request.app.state.clickhouse


@ml_router.get(
    "/views/{view}",
    response_class=Response,
    responses={200: {"content": {"application/vnd.apache.parquet": {}}, "description": "Fichier Parquet"}},
    include_in_schema=False)
async def get_view(view: str, request: Request):
    
    if view not in d_VIEWS:
        raise HTTPException(status_code=404, detail="Vue inconnue")
    
    client = _get_clickhouse_client(request)
    
    data = await client.raw_query(
        f"SELECT * FROM {d_VIEWS[view]}",
        fmt="Parquet",   # produit par Clickhouse
        #settings={"output_format_parquet_string_as_string": 1},  # texte écrit comme texte, et non comme binaire
        )
    
    # Parquet est de type bytes, il faut éviter que fastapi essaie de le convertir en json
    return Response(content=data, media_type="application/vnd.apache.parquet")