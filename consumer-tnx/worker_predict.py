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

{"trans_date_trans_time": "2020-12-12 08:01:43", "cc_num": "630423337322", "merchant": "Olson, Becker and Koch", "category": "gas_transport", "amt": "60.98", "first": "Stephanie", "last": "Gill", "gender": "F", "street": "43039 Riley Greens Suite 393", "city": "Orient", "state": "WA", "zip": "99160", "lat": "48.8878", "long": "-118.2105", "city_pop": "149", "job": "Special educational needs teacher", "dob": "1978-06-21", "trans_num": "9b39b9c1525e76bc4400b2cc180717d4", "merch_lat": "49.846216", "merch_long": "-117.570743", "uuid": "9ffdbd9f-d43f-429c-891a-7ffd84f11520"}



for elt in consumer:
    tnx = elt.value
    # Reconstruction du json à partir de l'elt du topic
    payload = {
        "uuid": tnx["uuid"],
        "trans_date_trans_time": tnx["trans_date_trans_time"],
        "cc_num": tnx["cc_num"],
        "merchant": tnx["merchant"],
        "category": tnx["category"],
        "amt": float(tnx["amt"]),
        "first": tnx["first"],
        "last": tnx["last"],
        "gender": tnx["gender"],
        "street": tnx["street"],
        "city": tnx["city"],
        "state": tnx["state"],
        "zip": tnx["zip"],
        "lat": float(tnx["lat"]),
        "long": float(tnx["long"]),
        "city_pop": int(tnx["city_pop"]),
        "job": tnx["job"],
        "dob": tnx["dob"],
        "trans_num": tnx["trans_num"],
        "merch_lat": float(tnx["merch_lat"]),
        "merch_long": float(tnx["merch_long"]),
        "fraud_score": 0,
    }
    
    # =========================================
    # PREDICT
    # =========================================
    # Infère le score par appel au modèle en prod avec les traitements nécessaires
    # Pour l'instant on se contente d'une lecture du label du merchant
    if ("fraud_" in payload["merchant"]):
        payload["fraud_score"] = 1
        
    logger.info(f"🟢 Elt courant : {payload}")
    
    # =========================================
    # PROCESS TNX /W INSERT IN ADEQUATE SCHEMA
    # =========================================
    
    # Commit à la fin du traitement de la transaction
    consumer.commit()