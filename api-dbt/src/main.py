import os

from fastapi import FastAPI

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
    root_path="/api-dbt",
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
import subprocess

