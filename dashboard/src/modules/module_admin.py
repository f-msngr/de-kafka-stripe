import streamlit as st

# Cache
from utils.api_lib import ErrorGateway, get_dbt_last_run, post_dbt_run_to_gateway


# Tabs

def body():
    # ************************************************************************************************************
    # ========================================
    # CACHE SETUP
    # ========================================
    # CACHE
    
    st.title("🫏 Admin")
    #st.markdown("Mise à jour manuelle des tables analytiques")
    
 
    # ========================================
    # TABS
    # ========================================
    import time

    dbt_last_run = get_dbt_last_run()
    waited = dbt_last_run is None

    while dbt_last_run is None:          # un run est en cours : le script reste ici, la page est grisée
        time.sleep(5)
        dbt_last_run = get_dbt_last_run()

    st.write(f"DBT last run: {dbt_last_run}")

    if "running" not in st.session_state:
        st.session_state.running = False

    def _clic():
        st.session_state.running = True

    st.button("DBT Run", disabled=st.session_state.running, on_click=_clic)

    if st.session_state.running:
        st.info("Updating tables analytics")
        try:
            post_dbt_run_to_gateway()
            st.cache_data.clear()
        finally:
            st.session_state.running = False
        st.rerun()

        