import os

from fastapi import FastAPI, Request, HTTPException, Form, Response, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.openapi.docs import get_swagger_ui_html

from pydantic import BaseModel

# ================================================
# Logging
# ================================================
import logging

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# ================================================
# Environment
# ================================================
from dotenv import load_dotenv
load_dotenv()

# Give access to env variables
# project_root_path = os.getenv("PROJECT_ROOT")
project_dir_name = os.getenv("PROJECT_NAME")
BOOTSTRAP_SERVERS = os.environ["BOOTSTRAP_SERVERS"]

# ================================================
# kafka producer creation at API startup
# ================================================
from contextlib import asynccontextmanager
from kafka import KafkaProducer
import json
import clickhouse_connect

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.producer = KafkaProducer(
        bootstrap_servers=BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        acks="all", # recommandé pour l'idempotence
        retries=10,
        retry_backoff_ms=500,
        # paramètre enable_idempotence est configuré sur True par défaut.
    )
    try:       # si la connexion clickhouse plante, alors il faut libérer la ressource : le Producer étant créé, il faut le fermer -> finally producer.close
        app.state.clickhouse = await clickhouse_connect.get_async_client(
            autogenerate_session_id=False,  # évite l'erreur « session verrouillée » si deux requêtes arrivent en même temps
            host=os.environ["CLICKHOUSE_HOST"],
            port=int(os.environ["CLICKHOUSE_PORT"]),
            username=os.environ["CLICKHOUSE_USER"],
            password=os.environ["CLICKHOUSE_PASSWORD"],
            database=os.environ["CLICKHOUSE_DB"],
        )
        try:   # si l'API plante, alors il faut libérer la ressource : fermer la connexion à Clickhouse -> finally clickhouse.close
            yield
        finally:
            app.state.clickhouse.close()
    finally:
        # Arrêt : envoie les messages restants puis ferme
        app.state.producer.close()


# ================================================
# Main app
# ================================================
# Set root_path for nginx
app = FastAPI(
    root_path="/api",
    lifespan=lifespan,
    title="⚠️ Stripe Fraud detection",
    description="Fraud Detection Gateway API",
    version="1.0.0"
    )

@app.get("/")
def read_root():
    return {"message": "👻 Gateway service -> Zuul is opening the path for Gozer"}

# ================================================
# Health
# ================================================
# Include router
from .route_health import health_router
app.include_router(health_router)


# ================================================
# Ingest
# ================================================
# Include router
from .route_ingest import ingest_router
app.include_router(ingest_router)


# ================================================
# DBT
# ================================================
# Include router
from .route_dbt import dbt_router
app.include_router(dbt_router, prefix="/dbt")


# ================================================
# ML
# ================================================
# Include router
from .route_ml import ml_router
app.include_router(ml_router, prefix="/ml")