# modules/module_transactions.py
import streamlit as st
import time

# Cache
from utils.api_lib import get_dbt_last_run, get_cached_count_view

# Tabs

def body():
    # ************************************************************************************************************
    st.title("🦧 Machine Learning")
    #st.markdown("Affiche la vue train")
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

    #st.markdown("Affiche les tables de faits")
    st.write(f"DBT last run: {last_run}")
    
    
    count = get_cached_count_view("train").iloc[0, 0]
    st.write(f"Nombre de lignes dans la base d'entraînement: {count}")

    # ========================================
    # TABS
    # ========================================