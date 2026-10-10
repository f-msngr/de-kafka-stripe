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

# ================================================
# Main app
# ================================================
# Set root_path for nginx
app = FastAPI(
    root_path="/api",
    title="🛡️ Stripe Fraud detection",
    description="Fraud Detection Management Tool",
    version="1.0.0"
    )

@app.get("/")
def read_root():
    return {"message": "Zuul the Gatekeeper -> Opening the path for Gozer 👻"}

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