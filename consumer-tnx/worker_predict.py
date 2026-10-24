# ============================================
# ENV + VAR CONF
# ============================================
import os
from dotenv import load_dotenv
load_dotenv()

BOOTSTRAP_SERVERS = os.environ["BOOTSTRAP_SERVERS"]
TOPIC_INCOMING_TNX = os.environ["TOPIC_INCOMING_TNX"]
GROUP_ID = os.environ["GROUP_ID"]

DB_SRC_HOST = os.environ["DB_SRC_HOST"]
DB_SRC_PORT = os.environ["DB_SRC_PORT"]
DB_SRC_USER = os.environ["DB_SRC_USER"]
DB_SRC_PASSWORD = os.environ["DB_SRC_PASSWORD"]
DB_SRC_NAME = os.environ["DB_SRC_NAME"]
DB_SRC_SCHEMA_1 = os.environ["DB_SRC_SCHEMA_1"]   # schéma des tables de référence et des transactions (payments)
DB_SRC_SCHEMA_2 = os.environ["DB_SRC_SCHEMA_2"]   # schéma du journal des rejets (frauds)

FRAUD_PREFIX = "fraud_"           # même valeur que dans producer-tnx/worker_incoming_tnx.py
FRAUD_THRESHOLD = float(os.environ["FRAUD_THRESHOLD"])             # fraud_score >= seuil : écriture dans frauds.rejects
MODEL_VERSION = "mock-v0"         # à remplacer par la version du vrai modèle
CURRENCY = "USD"                  # le feed n'a qu'un montant : devise de présentation = devise reçue (doit exister dans payments.currencies)
CURRENCY_RATE = 1
DB_RETRY_WAIT = 2                 # secondes entre deux tentatives de connexion à la base

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
# DATABASE (OLTP db-src)
# ============================================
import time
import psycopg
from psycopg import sql

def q(template: str) -> sql.Composed:
    """Remplace {s1} et {s2} par les schémas, entre guillemets d'identifiant."""
    return sql.SQL(template).format(s1=sql.Identifier(DB_SRC_SCHEMA_1), s2=sql.Identifier(DB_SRC_SCHEMA_2))

# Chaque INSERT retrouve la ligne par sa clé unique (ON CONFLICT) et renvoie son identifiant.
SQL_STATE = q("""INSERT INTO {s1}.states (state) VALUES (%s)
ON CONFLICT (state) DO UPDATE SET state = EXCLUDED.state RETURNING state_id""")
SQL_CITY = q("""INSERT INTO {s1}.cities (city, zip, city_pop, state_id) VALUES (%s, %s, %s, %s)
ON CONFLICT (city, state_id, zip) DO UPDATE SET city = EXCLUDED.city RETURNING city_id""")
SQL_ADDRESS = q("""INSERT INTO {s1}.addresses (street, lat, "long", city_id) VALUES (%s, %s, %s, %s)
ON CONFLICT (street, lat, "long", city_id) DO UPDATE SET street = EXCLUDED.street RETURNING address_id""")
SQL_JOB = q("""INSERT INTO {s1}.jobs (job) VALUES (%s)
ON CONFLICT (job) DO UPDATE SET job = EXCLUDED.job RETURNING job_id""")
SQL_CUSTOMER = q("""INSERT INTO {s1}.customers (first_name, last_name, gender, dob, job_id, address_id)
VALUES (%s, %s, %s, %s, %s, %s)
ON CONFLICT (first_name, last_name, dob) DO UPDATE SET first_name = EXCLUDED.first_name RETURNING customer_id""")
SQL_ACTIVITY = q("""INSERT INTO {s1}.activities (category) VALUES (%s)
ON CONFLICT (category) DO UPDATE SET category = EXCLUDED.category RETURNING activity_id""")
SQL_MERCHANT = q("""INSERT INTO {s1}.merchants (merchant) VALUES (%s)
ON CONFLICT (merchant) DO UPDATE SET merchant = EXCLUDED.merchant RETURNING merchant_id""")
SQL_TRANSACTION = q(
    "INSERT INTO {s1}.transactions ("
    "trans_num, "                   # 1  <- p["trans_num"]
    "transdate_transtime, "         # 2  <- p["trans_date_trans_time"]
    "cc_num, "                      # 3  <- p["cc_num"]
    "amount_presentation, "         # 4  <- amt
    "amt, "                         # 5  <- amt
    "currency_rate, "               # 6  <- CURRENCY_RATE
    "currency_id_presentation, "    # 7  <- CURRENCY
    "currency_id_received, "        # 8  <- CURRENCY
    "fraud_score, "                 # 9  <- p["fraud_score"]
    "model_version, "               # 10 <- MODEL_VERSION
    "status, "                      # 11 valeur fixe 'successful'
    "review_status, "               # 12 valeur fixe 'cleared'
    "is_fraud, "                    # 13 valeur fixe false
    "merch_lat, "                   # 14 <- p["merch_lat"]
    "merch_long, "                  # 15 <- p["merch_long"]
    "customer_id, "                 # 16 <- customer_id
    "merchant_id, "                 # 17 <- merchant_id
    "activity_id"                   # 18 <- activity_id
    ") VALUES ("
    "%s, "                          # 1  trans_num
    "%s, "                          # 2  transdate_transtime
    "%s, "                          # 3  cc_num
    "%s, "                          # 4  amount_presentation
    "%s, "                          # 5  amt
    "%s, "                          # 6  currency_rate
    "%s, "                          # 7  currency_id_presentation
    "%s, "                          # 8  currency_id_received
    "%s, "                          # 9  fraud_score
    "%s, "                          # 10 model_version
    "'successful', "                # 11 status
    #"'cleared', "                   # 12 review_status
    "%s, "                          # 12 review_status
    "false, "                       # 13 is_fraud
    "%s, "                          # 14 merch_lat
    "%s, "                          # 15 merch_long
    "%s, "                          # 16 customer_id
    "%s, "                          # 17 merchant_id
    "%s"                            # 18 activity_id
    ") ON CONFLICT (trans_num) DO NOTHING"   # rowcount = 0 si trans_num existe déjà -> 'duplicate'
)
SQL_REJECT = q("""INSERT INTO {s2}.rejects
(trans_num, customer_id, first_name, last_name, dob, merchant_id, merchant, activity_id,
 transdate_transtime, cc_num, amount_presentation, currency_id_presentation, amt,
 merch_lat, merch_long, fraud_score, model_version)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
ON CONFLICT (trans_num) DO NOTHING""")

def connect() -> psycopg.Connection:
    """Se connecte à db-src ; réessaie tant que la base est injoignable."""
    while True:
        try:
            return psycopg.connect(host=DB_SRC_HOST, port=DB_SRC_PORT, dbname=DB_SRC_NAME,
                                   user=DB_SRC_USER, password=DB_SRC_PASSWORD, autocommit=True)
        except psycopg.OperationalError as e:
            logger.warning(f"⚠️ base injoignable ({e}) : nouvel essai dans {DB_RETRY_WAIT} s")
            time.sleep(DB_RETRY_WAIT)

def one(cur, sql: str, params: tuple):
    """Execute une instruction de la transaction SQL complète """
    cur.execute(sql, params)
    return cur.fetchone()[0]

def write_tnx(conn: psycopg.Connection, p: dict) -> str:
    """Résoud les dépendances puis écrit la transaction ou le rejet, dans une seule transaction SQL.
    Renvoie 'transaction', 'reject' ou 'duplicate'."""
    with conn.transaction(), conn.cursor() as cur:    # BEGIN ... COMMIT, ROLLBACK si exception
        state_id = one(cur, SQL_STATE, (p["state"],))
        city_id = one(cur, SQL_CITY, (p["city"], p["zip"], p["city_pop"], state_id))
        address_id = one(cur, SQL_ADDRESS, (p["street"], p["lat"], p["long"], city_id))
        job_id = one(cur, SQL_JOB, (p["job"],))
        customer_id = one(cur, SQL_CUSTOMER, (p["first"], p["last"], p["gender"], p["dob"], job_id, address_id))
        activity_id = one(cur, SQL_ACTIVITY, (p["category"],))
        merchant_id = one(cur, SQL_MERCHANT, (p["merchant"],))
        
        amt = round(p["amt"], 4)
        
        # Si fraud_score >= seuil alors transaction rejetée
        if p["fraud_score"] >= FRAUD_THRESHOLD:       # jamais dans payments.transactions (ADR_001-003)
            cur.execute(SQL_REJECT, 
                        (p["trans_num"],
                        customer_id,
                        p["first"],
                        p["last"],
                        p["dob"],
                        merchant_id,
                        p["merchant"],
                        activity_id,
                        p["trans_date_trans_time"],
                        p["cc_num"],
                        amt,
                        CURRENCY,
                        amt,
                        p["merch_lat"],
                        p["merch_long"],
                        p["fraud_score"],
                        MODEL_VERSION
                        ))
            return "reject" if cur.rowcount == 1 else "duplicate"
        
        # Sinon si fraud_score >= seuil - 0.10
        if payload["fraud_score"] >= (FRAUD_THRESHOLD - 0.10):
            payload["review_status"] = 'pending'
        else:
            payload["review_status"] = 'cleared'
        
        cur.execute(SQL_TRANSACTION,
                    (p["trans_num"],
                    p["trans_date_trans_time"],
                    p["cc_num"],
                    amt,
                    amt,
                    CURRENCY_RATE,
                    CURRENCY,
                    CURRENCY,
                    p["fraud_score"],
                    MODEL_VERSION,
                    p["review_status"],
                    p["merch_lat"],
                    p["merch_long"],
                    customer_id,
                    merchant_id,
                    activity_id
                    ))
        return "transaction" if cur.rowcount == 1 else "duplicate"



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

from kafka import KafkaConsumer
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

# Set connection
conn = connect()

for elt in consumer:
    tnx = elt.value
    # Reconstruction du json à partir de l'elt du topic
    try:
        is_synth = tnx["merchant"].startswith(FRAUD_PREFIX)                 # étiquette de transport, jamais écrite en base
        
        payload = {
            "uuid": tnx["uuid"],
            "trans_date_trans_time": tnx["trans_date_trans_time"],
            "cc_num": tnx["cc_num"],
            "merchant": tnx["merchant"].removeprefix(FRAUD_PREFIX),         # retrait du préfixe
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
            "fraud_score": 0.0,                                             # devra contenir le score prédit cf. PREDICT 
        }
    except (KeyError, ValueError, TypeError, AttributeError) as e:
        logger.error(f"❌ Message invalide, ignoré : {e!r}")
        consumer.commit()                # un message illisible reviendrait en boucle sinon
        continue
    
    # =========================================
    # PREDICT
    # =========================================
    # Infère le score par appel au modèle en prod avec les traitements nécessaires
    # Pour l'instant : score 1 si le marchand portait l'étiquette de fraude synthétique
    import random
    
    if is_synth:
        payload["fraud_score"] = 1.0
    else:
        # Simule une prediction avec score
        SCORE_MIN = 0.70                  # borne basse du score simulé
        SCORE_MAX = 0.90                  # borne haute du score simulé
        FRAUD_SCORE = round(random.uniform(SCORE_MIN, SCORE_MAX), 3)
        payload["fraud_score"] = FRAUD_SCORE

    # =========================================
    # PROCESS TNX /W INSERT IN ADEQUATE SCHEMA
    # =========================================
    while True:
        try:
            dest = write_tnx(conn, payload)
            break
        except psycopg.OperationalError as e:       # connexion perdue : on se reconnecte, le message sera retraité
            logger.warning(f"⚠️ base perdue ({e}) : reconnexion")
            conn.close()
            conn = connect()
        except (psycopg.DataError, psycopg.IntegrityError) as e:   # donnée refusée : rollback, sans rejet (ADR_001-003)
            logger.error(f"❌ Donnée refusée par la base, ignorée : {e}")
            dest = "ignored"
            break
    logger.info(f"🟢 {dest} : {payload['trans_num']} score={payload['fraud_score']}")

    # Commit à la fin du traitement de la transaction
    consumer.commit()