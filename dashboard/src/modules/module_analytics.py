import streamlit as st
import time

# Cache
from utils.api_lib import (
    ErrorGateway,
    get_dbt_last_run,
    get_cached_transactions_amt_by_merchant_monthly,
    get_cached_customers_count_by_state_monthly,
    get_cached_transactions_count_monthly,
    get_cached_frauds_count_daily,
    get_cached_frauds_count_monthly,
    get_cached_frauds_amt_by_merchant_monthly,
    get_cached_frauds_count_by_merchant_monthly,
    get_cached_reviews,
)



# Tabs

def body():
    # ************************************************************************************************************
    st.title("🐎 Analytics")
    # ========================================
    # Test dbt run en cours
    # ========================================
    waiting = st.empty()          # emplacement unique, remplacé à chaque tour
    last_run = get_dbt_last_run()
    waited = last_run is None

    while last_run is None:
        waiting.info("Vues en cours d'update…")
        time.sleep(5)             # pause entre deux vérifications
        last_run = get_dbt_last_run()

    waiting.empty()               # efface le message
    if waited:
        st.cache_data.clear()     # les données ont changé : on repart d'un cache vide

    st.markdown("Affiche les tables de faits")
    st.write(f"DBT last run: {last_run}")
    
    # ========================================
    # TABS
    # ========================================
    # Tabs for different sections
    tab_transactions, tab_frauds, tab_predictions, tab_reviews = st.tabs([
        "Transactions",
        "Frauds",
        "Predictions",
        "Reviews"
    ])
    
    # Tab contents
    with tab_transactions:
        # transactions par marchand, par mois
        st.subheader("Revenu mensuel par marchand")
        try:
            df = get_cached_transactions_amt_by_merchant_monthly()
            st.dataframe(df, height=200)
        except ErrorGateway as e:
            st.error(str(e))
        
        st.subheader("Nombre de clients différents par état par mois")
        try:
            df = get_cached_customers_count_by_state_monthly()
            st.dataframe(df, height=200)
        except ErrorGateway as e:
            st.error(str(e))
        
        st.subheader("Volume de transactions par mois")
        try:
            df = get_cached_transactions_count_monthly()
            st.dataframe(df, height=200)
        except ErrorGateway as e:
            st.error(str(e))
        
    
    with tab_frauds:
        # frauds par jour
        st.subheader("Nombre de fraudes par jour")
        try:
            df = get_cached_frauds_count_daily()
            st.dataframe(df, height=200)
        except ErrorGateway as e:
            st.error(str(e))
        
        # frauds par mois
        st.subheader("Nombre de fraudes par mois")
        try:
            df = get_cached_frauds_count_monthly()
            st.dataframe(df, height=210)
        except ErrorGateway as e:
            st.error(str(e))
        
        # Montant de la fraude, évitée ou subie, par marchand par mois
        st.subheader("Montant de la fraude (subie + évitée) par marchand par mois")
        try:
            df = get_cached_frauds_amt_by_merchant_monthly()
            st.dataframe(df, height=200)
        except ErrorGateway as e:
            st.error(str(e))
        
        # Ratio de fraude évitée/subie par marchand par mois
        st.subheader("Ratio de fraude évitée/subie par marchand par mois")
        try:
            df = get_cached_frauds_count_by_merchant_monthly()
            st.dataframe(df, height=200)
        except ErrorGateway as e:
            st.error(str(e))
        
    with tab_reviews:
        try:
            df = get_cached_reviews()
            st.dataframe(df)
        except ErrorGateway as e:
            st.error(str(e))        
        