from fastapi import APIRouter, HTTPException
from pydantic import ValidationError

import json
import httpx



#from pipeline.core.src.pydantic_schemas import TransactionData

from confluent_kafka import Producer
import threading

from fastapi import FastAPI, HTTPException

from datetime import datetime, timezone

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
N_PER_CALL = 5  # nombre d'entiers publiés à chaque appel de /ingest (modifier ici puis relancer)
BOOTSTRAP_SERVERS = os.environ["BOOTSTRAP_SERVERS"]
INGEST_TOPIC = os.environ["INGEST_TOPIC"]


# ===============================
# Producer
# ===============================
producer = Producer({"bootstrap.servers": BOOTSTRAP_SERVERS})
lock = threading.Lock()  # deux appels simultanés ne doivent pas se partager les mêmes entiers
counter = 0

# ===============================
# Predict entry point
# ===============================
@ingest_router.post("/ingest", status_code=202)
def ingest():
    global counter
    errors = []

    def on_delivery(err, msg):
        if err is not None:
            errors.append(str(err))

    with lock:
        first = counter + 1
        for _ in range(N_PER_CALL):
            counter += 1
            payload = {"n": counter, "ts": datetime.now(timezone.utc).isoformat()}
            producer.produce(INGEST_TOPIC, json.dumps(payload).encode(), callback=on_delivery)
        pending = producer.flush(10)  # attend jusqu'à 10 s la confirmation de Kafka

    if errors or pending > 0:
        raise HTTPException(status_code=502, detail="Kafka n'a pas confirmé tous les messages")
    return {"topic": INGEST_TOPIC, "first": first, "last": counter, "count": N_PER_CALL}
  