import streamlit as st

# Cache
from utils.api_lib import ErrorGateway, get_dbt_last_run, get_dbt_run_status, post_dbt_run_to_gateway


# Tabs

def body():
    # ************************************************************************************************************
    # ========================================
    # CACHE SETUP
    # ========================================
    # CACHE
    
    st.title("🫏 Admin")
 
    # ========================================
    # TABS
    # ========================================
    import time

    waiting = st.empty()
    d_status = get_dbt_run_status()
    waited = d_status["status"] == "running"

    while d_status["status"] == "running":      # run en cours : la page reste grisée ici
        waiting.info("Vues en cours d'update…")
        time.sleep(5)
        d_status = get_dbt_run_status()

    waiting.empty()
    if waited:
        st.cache_data.clear()                   # les données ont changé

    st.write(f"DBT last run: {d_status['finished_at'] or 'aucun run'}")

    if st.button("DBT Run"):
        try:
            post_dbt_run_to_gateway()           # répond tout de suite (202) : le run continue en arrière-plan
        except ErrorGateway as e:               # à importer depuis utils.api_lib ; ex. 409 : un run est déjà en cours
            st.error(str(e))
        else:
            st.rerun()

        