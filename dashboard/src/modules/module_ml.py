# modules/module_transactions.py
import streamlit as st
import time

# Cache
from utils.api_lib import get_dbt_last_run, get_dbt_run_status, get_cached_count_view

# Tabs

def body():
    # ************************************************************************************************************
    st.title("🦧 Machine Learning")
    #st.markdown("Affiche la vue train")
    # ========================================
    # Test dbt run en cours
    # ========================================
    waiting = st.empty()          # emplacement unique, remplacé à chaque tour
    d_status = get_dbt_run_status()
    waited = d_status["status"] == "running"

    while d_status["status"] == "running":
        waiting.info("Vues en cours d'update…")
        time.sleep(5)
        d_status = get_dbt_run_status()

    waiting.empty()               # efface le message
    if waited:
        st.cache_data.clear()     # les données ont changé : on repart d'un cache vide

    last_run = get_dbt_last_run()
    st.write(f"DBT last run: {last_run}")
    
    # Pas de données transformées produites par dbt
    # Il faut arrêter la page
    if d_status["status"] == "init":
        st.info("Aucune donnée : lancer un premier dbt run depuis la page Admin.")
        st.stop() 
    
    count = get_cached_count_view("train").iloc[0, 0]
    st.write(f"Nombre de lignes dans la base d'entraînement: {count}")

    # ========================================
    # TABS
    # ========================================