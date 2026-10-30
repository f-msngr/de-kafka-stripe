from fastapi import APIRouter


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
analytics_router = APIRouter()
# Context

# ===============================
# ENV
# ===============================
DBT_MARTS = os.environ["DBT_MARTS"]     # On utilise les faits produits par DBT dans marts


# ===============================
# analytics endpoints
# ===============================
from fastapi import HTTPException, Request, Response
from .libs import get_clickhouse_client

d_FACTS = {
    "frauds": "fct_frauds",
    "predictions": "fct_predictions",
    "reviews": "fct_reviews",
    "transactions": "fct_transactions",
    }  # nom réel des vues/tables dbt autorisées à l'appel

@analytics_router.get(
    "/facts/{fact}",
    response_class=Response,
    responses={200: {"content": {"application/json": {}}, "description": "Query response in json"}},
    include_in_schema=False)
async def get_fct(fact: str, request: Request):
    """Renvoie en json le contenu d'une vue/table dbt autorisée.

    - `fact` : clé de la vue/table dans `d_FACTS` (liste blanche), sinon 404.
    - Le client ClickHouse est celui créé au démarrage (lifespan) et stocké
      dans `app.state`; il est récupéré via `request`.
    - Exécute `SELECT * FROM <fact>` ; ClickHouse produit le json, renvoyé tel quel.
    """
    if fact not in d_FACTS:
        raise HTTPException(status_code=404, detail="Fait inconnu")
    
    client = get_clickhouse_client(request)
    
    data = await client.raw_query(
        f"SELECT * FROM  {DBT_MARTS}.{d_FACTS[fact]}",
        fmt="JSONCompact",   # produit par Clickhouse
        )
    
    # Réponse à la requête au format json
    return Response(content=data, media_type="application/json")


# ===============================
# Transactions
# ===============================
# Montant des transactions valides, par marchand par mois
@analytics_router.get(
    "/studies/transactions_amt_by_merchant_monthly",
    response_class=Response,
    responses={200: {"content": {"application/json": {}}, "description": "Query response in json"}},
    include_in_schema=False)
async def get_transactions_amt_by_merchant_monthly(request: Request):
    """Renvoie en json le montant des transactions, valides par marchand par mois."""
    client = get_clickhouse_client(request)    
    data = await client.raw_query(
        f"SELECT \
            merchant, \
            transaction_month, \
            sum(amt) AS total_transaction \
        FROM {DBT_MARTS}.fct_transactions \
        INNER JOIN {DBT_MARTS}.dim_merchants USING (merchant_id) \
        WHERE status = 'successful' \
        GROUP BY \
            merchant_id, \
            merchant, \
            transaction_month \
        ORDER BY \
            merchant_id ASC, \
            transaction_month DESC",
        fmt="JSONCompact"
        )    
    # Réponse à la requête au format json
    return Response(content=data, media_type="application/json")

# Nombre de clients distincts par état par mois
@analytics_router.get(
    "/studies/customers_count_by_state_monthly",
    response_class=Response,
    responses={200: {"content": {"application/json": {}}, "description": "Query response in json"}},
    include_in_schema=False)
async def get_customers_count_by_state_monthly(request: Request):
    """Renvoie en json le nombre de clients différents par état par mois."""
    client = get_clickhouse_client(request)    
    data = await client.raw_query(
        f"SELECT \
            state, \
            transaction_month, \
            uniqExact(customer_id) AS nb_customers \
        FROM {DBT_MARTS}.fct_transactions \
        INNER JOIN {DBT_MARTS}.dim_customers USING (customer_id) \
        WHERE status = 'successful' \
        GROUP BY \
            state, \
            transaction_month \
        ORDER BY \
            transaction_month DESC, \
            state ASC",
        fmt="JSONCompact"
        )    
    # Réponse à la requête au format json
    return Response(content=data, media_type="application/json")


# Volume de transactions par mois
@analytics_router.get(
    "/studies/transactions_count_monthly",
    response_class=Response,
    responses={200: {"content": {"application/json": {}}, "description": "Query response in json"}},
    include_in_schema=False)
async def get_transactions_count_monthly(request: Request):
    """Renvoie en json le volume de transactions par mois."""
    client = get_clickhouse_client(request)    
    data = await client.raw_query(
        f"SELECT \
            transaction_month, \
            count(*) AS nb_transactions \
        FROM {DBT_MARTS}.fct_transactions \
        WHERE status = 'successful' \
        GROUP BY \
            transaction_month \
        ORDER BY \
            transaction_month DESC",
        fmt="JSONCompact"
        )    
    # Réponse à la requête au format json
    return Response(content=data, media_type="application/json")


# =================================
# Frauds
# =================================
# Frauds par jour
@analytics_router.get(
    "/studies/frauds_count_daily",
    response_class=Response,
    responses={200: {"content": {"application/json": {}}, "description": "Query response in json"}},
    include_in_schema=False)
async def get_frauds_count_daily(request: Request):
    """Renvoie en json les fraudes journalières."""
    client = get_clickhouse_client(request)    
    data = await client.raw_query(
        f"SELECT \
            fraud_date,\
            count(*) AS nb_transactions \
        FROM {DBT_MARTS}.fct_frauds \
        GROUP BY fraud_date \
        ORDER BY fraud_date DESC",
        fmt="JSONCompact",
        )
    # Réponse à la requête au format json
    return Response(content=data, media_type="application/json")


# Frauds par mois
@analytics_router.get(
    "/studies/frauds_count_monthly",
    response_class=Response,
    responses={200: {"content": {"application/json": {}}, "description": "Query response in json"}},
    include_in_schema=False)
async def get_frauds_count_monthly(request: Request):
    """Renvoie en json les fraudes mensuelles."""
    client = get_clickhouse_client(request)
    data = await client.raw_query(
        f"SELECT \
            fraud_month, \
            count() AS nb_transactions \
        FROM {DBT_MARTS}.fct_frauds \
        GROUP BY fraud_month \
        ORDER BY fraud_month DESC",
        fmt="JSONCompact",
        )    
    # Réponse à la requête au format json
    return Response(content=data, media_type="application/json")


# Montant de la fraude, évitée ou subie, par marchand par mois
@analytics_router.get(
    "/studies/frauds_amt_by_merchant_monthly",
    response_class=Response,
    responses={200: {"content": {"application/json": {}}, "description": "Query response in json"}},
    include_in_schema=False)
async def get_frauds_amt_by_merchant_monthly(request: Request):
    """Renvoie en json le montant de la fraude, évitée ou subie, par marchand par mois."""
    client = get_clickhouse_client(request)    
    data = await client.raw_query(
        f"SELECT \
            merchant, \
            fraud_month, \
            sum(amt) AS total_fraude \
        FROM {DBT_MARTS}.fct_frauds \
        INNER JOIN {DBT_MARTS}.dim_merchants USING (merchant_id) \
        GROUP BY \
            merchant_id, \
            merchant, \
            fraud_month \
        ORDER BY \
            merchant_id ASC, \
            fraud_month DESC",
        fmt="JSONCompact",
        )    
    # Réponse à la requête au format json
    return Response(content=data, media_type="application/json")


# Ratio des fraudes évitées / subies, par marchand par mois
@analytics_router.get(
    "/studies/frauds_count_by_merchant_monthly",
    response_class=Response,
    responses={200: {"content": {"application/json": {}}, "description": "Query response in json"}},
    include_in_schema=False)
async def get_frauds_count_by_merchant_monthly(request: Request):
    """Renvoie en json les comptes des fraudes évitées / subies, par marchand par mois"""
    client = get_clickhouse_client(request)    
    data = await client.raw_query(
        f"SELECT \
            merchant, \
            fraud_month, \
            origin, \
            count(*) \
        FROM {DBT_MARTS}.fct_frauds \
        INNER JOIN {DBT_MARTS}.dim_merchants USING (merchant_id) \
        WHERE origin != 'init' \
        GROUP BY \
            merchant_id, \
            merchant, \
            fraud_month, \
            origin \
        ORDER BY \
            merchant_id ASC, \
            fraud_month DESC",
        fmt="JSONCompact",
        )    
    # Réponse à la requête au format json
    return Response(content=data, media_type="application/json")


# ===============================
# Predictions
# ===============================
#7. Prédiction : date -> résultat (rejet, cleared, pending, reviewed), fraud_score
#9. Prédiction -> review_status, is_fraud


# ===============================
# Reviews
# ===============================
#10. Revue : analysts, date (période) -> nombre de lignes
#11. Revue : analysts, date (période) -> délai entre transdate_transtime et verdict_at