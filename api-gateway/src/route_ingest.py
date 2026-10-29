from fastapi import APIRouter, HTTPException, Request
from pydantic import ValidationError

import json
import httpx



#from pipeline.core.src.pydantic_schemas import TransactionData

from fastapi import FastAPI

from datetime import datetime, timezone

import asyncio
from kafka.errors import KafkaError

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
ingest_router = APIRouter()
# Context

# ===============================
# ENV
# ===============================

TOPIC_INCOMING_TNX = os.environ["TOPIC_INCOMING_TNX"]

# ===============================
# Ingest endpoints
# ===============================
@ingest_router.post("/ingest", status_code=202)
async def ep_ingest(raw: dict, request: Request):
    
    # Validation Pydantic
    # ici
    # try/except
    # transformer raw en payload
    payload = raw

    # Récupération du Producer Kafka défini au démarrage de app
    producer = request.app.state.producer
    
    try:
        # send + attente de confirmation, exécutés dans un thread
        meta = await asyncio.to_thread(
            lambda: producer.send(TOPIC_INCOMING_TNX, value=payload).get(timeout=15)
        )
        
    except KafkaError as e:
        logger.error(f"🔴 Data NOT written: {e}")
        raise HTTPException(status_code=503, detail="Kafka unavailable")

    logger.info(f"🟢 Data {payload} written in {meta.topic} partition={meta.partition} offset={meta.offset}")
    return {"status": "accepted", "partition": meta.partition, "offset": meta.offset}
  