# ============================================
# ENV + VAR CONF
# ============================================
import os
from dotenv import load_dotenv
load_dotenv()

BOOTSTRAP_SERVERS = os.environ["BOOTSTRAP_SERVERS"]
TOPIC_INCOMING_TNX = os.environ["TOPIC_INCOMING_TNX"]
GROUP_ID = os.environ["GROUP_ID"]

# ============================================
# LOGGING
# ============================================
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)
logger = logging.getLogger(__name__)


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

from kafka import KafkaConsumer, KafkaProducer
import json

logger.info(f"Topic suivi : {TOPIC_INCOMING_TNX}")

consumer = KafkaConsumer(
    TOPIC_INCOMING_TNX,
    bootstrap_servers=BOOTSTRAP_SERVERS,
    group_id=GROUP_ID,
    enable_auto_commit=False,           # On valide la position nous-mêmes, après traitement
    auto_offset_reset="earliest",       # Un redémarrage du consumer relit tout le topic depuis le début
    value_deserializer=lambda b: json.loads(b.decode("utf-8")),
)



for elt in consumer:
    tnx = elt.value
    # Reconstruction du json à partir de l'elt du topic
    payload = {"uuid": tnx["uuid"], "ts": tnx["ts"]}
    logger.info(f"🟢 Elt courant : {payload}")

    consumer.commit()