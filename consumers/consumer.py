import time
import psycopg2
from kafka import KafkaConsumer
import json
import logging

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
        conn = psycopg2.connect(
            host="kafka02-postgres-target",
            port=5432,      # rendu paramétrable
            dbname="target",
            user="postgres",
            password="postgres"
        )
        conn.autocommit = False
        cursor = conn.cursor()
        logger.info("Connecté à db-target")
        break
    except Exception as e:
        logger.error(f"db-target non disponible : {e}")
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

# Retry la connexion à Kafka jusqu'à ce que ça marche
# pour éviter que le consumer ne crash si Kafka n'est pas encore prêt au démarrage du container.
while True:
    try:
        consumer = KafkaConsumer(
            "kafka02-topic-inventory.inventory.customers",
            bootstrap_servers='kafka:9092',
            group_id='Golodorak',
            auto_offset_reset='earliest',
            enable_auto_commit=False,
            value_deserializer=lambda m: json.loads(m.decode('utf-8'))
            )
        break
    except Exception as e:
        logger.error(f"Error connecting to Kafka: {e}")
        time.sleep(5)



# ============================================
# PROCESS
# ============================================
for message in consumer:
    payload = message.value['payload']
    op = payload['op']
    logger.info(f"op={op}")