import streamlit as st
import requests
import os
import pandas as pd

URL_APIGATEWAY = f"{os.environ['URL_APIGATEWAY']}"

def get_health():
    return requests.get(f"{URL_APIGATEWAY}/health").json()

# Classe d'erreur personnalisée pour intercepter :
# exceptions.ConnectionError
# exceptions.Timeout
# exceptions.HTTPError
# exceptions.JSONDecodeError
class ErrorGateway(Exception):
    """Error during access to API Gateway."""


# Fonction d'accès factorisée
def _get_from_gateway(path: str) -> pd.DataFrame:
    try:
        r = requests.get(f"{URL_APIGATEWAY}{path}", timeout=10)
        r.raise_for_status()
        resp = r.json()
        cols = [c["name"] for c in resp["meta"]]
        return pd.DataFrame(resp["data"], columns=cols)
    except (requests.RequestException, ValueError, KeyError) as e:
        raise ErrorGateway(f"Gateway : {e}") from e

# ===============================
# DBT Run
# ===============================
def post_dbt_run_to_gateway():
    try:
        r = requests.post(f"{URL_APIGATEWAY}/dbt/run", timeout=10)
        r.raise_for_status()
        resp = r.json()
        return resp
    except (requests.RequestException, ValueError, KeyError) as e:
        raise ErrorGateway(f"Gateway : {e}") from e

def get_dbt_run_status():
    try:
        r = requests.get(f"{URL_APIGATEWAY}/dbt/run-status", timeout=10)
        r.raise_for_status()
        resp = r.json()
        return resp
    except (requests.RequestException, ValueError, KeyError) as e:
        raise ErrorGateway(f"Gateway : {e}") from e

def get_dbt_last_run():
    status = get_dbt_run_status()
    return status["finished_at"]




# ===============================
# Transactions
# ===============================
#1. Transaction : merchants, date (mois)	-> somme de amt
@st.cache_data(ttl=3600)
def get_cached_transactions_amt_by_merchant_monthly() -> pd.DataFrame:
    return _get_from_gateway("/analytics/studies/transactions_amt_by_merchant_monthly")

#2. Transaction : customers (state) -> nombre de clients distincts
@st.cache_data(ttl=3600)
def get_cached_customers_count_by_state_monthly() -> pd.DataFrame:
    return _get_from_gateway("/analytics/studies/customers_count_by_state_monthly")

#3. Transaction : date -> nombre des lignes
@st.cache_data(ttl=3600)
def get_cached_transactions_count_monthly() -> pd.DataFrame:
    return _get_from_gateway("/analytics/studies/transactions_count_monthly")
 

# ===============================
# Frauds cf. questions OLAP
# ===============================
@st.cache_data(ttl=3600)
def get_cached_frauds() -> pd.DataFrame:
    return _get_from_gateway("/analytics/facts/frauds")

#4. Fraude : date (jour, mois) -> nombre de lignes
@st.cache_data(ttl=3600)
def get_cached_frauds_count_daily() -> pd.DataFrame:
    return _get_from_gateway("/analytics/studies/frauds_count_daily")

@st.cache_data(ttl=3600)
def get_cached_frauds_count_monthly() -> pd.DataFrame:
    return _get_from_gateway("/analytics/studies/frauds_count_monthly")

#5. Fraude : montant de fraude, évitée ou subie, par marchand par mois -> somme de amt
@st.cache_data(ttl=3600)
def get_cached_frauds_amt_by_merchant_monthly() -> pd.DataFrame:
    return _get_from_gateway("/analytics/studies/frauds_amt_by_merchant_monthly")

#8. Fraude -> origine (rejet inline ou review)
@st.cache_data(ttl=3600)
def get_cached_frauds_count_by_merchant_monthly() -> pd.DataFrame:
    return _get_from_gateway("/analytics/studies/frauds_count_by_merchant_monthly")

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
@st.cache_data(ttl=3600)
def get_cached_reviews() -> pd.DataFrame:
    return _get_from_gateway("/analytics/facts/reviews")