import json
import logging
import time
import os
import psycopg2
from kafka import KafkaConsumer
from dotenv import load_dotenv

load_dotenv()

# ============================================
# LOGGING
# ============================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================
# CONNEXION DB TARGET
# ============================================
while True:
    try:
        SINK_HOST = os.getenv("SINK_HOST")
        SINK_PORT = os.getenv("SINK_PORT")
        SINK_DB = os.getenv("SINK_DB")
        SINK_USER = os.getenv("SINK_USER")
        SINK_PASSWORD = os.getenv("SINK_PASSWORD")
        conn = psycopg2.connect(
            host=SINK_HOST,
            port=SINK_PORT,
            dbname=SINK_DB,
            user=SINK_USER,
            password=SINK_PASSWORD
        )
        conn.autocommit = False
        cursor = conn.cursor()
        logger.info(f"🟢 Connecté à {SINK_HOST}:{SINK_PORT}/{SINK_DB} en tant que {SINK_USER}")
        break
    except Exception as e:
        logger.error(f"{SINK_HOST}:{SINK_PORT}/{SINK_DB} non disponible : {e}")
        time.sleep(5)



# ============================================
# KAFKA CONSUMER
# ============================================
# PARAMS CONSUMER
# - bootstrap_servers : adresse du broker Kafka
# - group_id : Kafka retient l'offset par groupe — si le consumer redémarre, il reprend où il s'est arrêté.
#   un topic est divisé en partitions. Plusieurs consumers peuvent lire le même topic en parallèle
#   chaque consumer d'un groupe prend en charge une ou plusieurs partitions.
#   2 consumers avec le même group_id se partagent les partitions,
#   2 consumers avec un group_id différent lisent indépendamment, chacun reçoit tous les messages — pattern broadcast
# - auto_offset_reset : comportement quand il n'y a pas d'offset sauvegardé pour ce groupe
# - enable_auto_commit : commit manuel après que l'écriture en base est confirmée pour éviter de perdre un événement si crash lecture et écriture.
# - value_deserializer : fonction pour convertir les messages en objets Python

prefix = os.environ["TOPIC_PREFIX"]
topics = [f"{prefix}.{t.strip()}" for t in os.environ["SRC_TABLES"].split(",") if t.strip()]
logger.info(f"Topics suivis : {topics}")

consumer = None
while consumer is None:
    try:
        consumer = KafkaConsumer(
            *topics,
            bootstrap_servers=os.environ["BOOTSTRAP_SERVERS"],
            group_id=os.environ["KAFKA_GROUP_ID"],
            auto_offset_reset='earliest',
            enable_auto_commit=False,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')) if m is not None else None
        )
        logger.info("🟢 Connecté à Kafka")
    except Exception as e:
        logger.error(f"Kafka non disponible : {e}")
        time.sleep(5)

# ============================================
# PROCESS
# ============================================
for message in consumer:
    if message.value is None:
        consumer.commit()          # on acquitte la tombstone et on passe
        continue
    
    print(f"MESSAGE RECU op={message.value['payload']['op']}", flush=True)
    
    payload = message.value['payload']
    op = payload['op']
    logger.info(f"op={op}")
    
    before = payload.get('before')
    after = payload.get('after')

    try:
        if op in ('c', 'r'):
            cursor.execute(
                "INSERT INTO target.customers (id, first_name, last_name, email) VALUES (%s, %s, %s, %s)",
                (after['id'], after['first_name'], after['last_name'], after['email'])
            )
            logger.info(f"INSERT id={after['id']}")

        elif op == 'u':
            cursor.execute(
                "UPDATE target.customers SET first_name=%s, last_name=%s, email=%s WHERE id=%s",
                (after['first_name'], after['last_name'], after['email'], after['id'])
            )
            logger.info(f"UPDATE id={after['id']}")

        elif op == 'd':
            cursor.execute(
                "DELETE FROM target.customers WHERE id=%s",
                (before['id'],)
            )
            logger.info(f"DELETE id={before['id']}")

        conn.commit()
        consumer.commit()

    except Exception as e:
        logger.error(f"Erreur op={op} : {e}")
        conn.rollback()