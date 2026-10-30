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
    
    st.title("🐎 Admin")
    st.markdown("Mise à jour manuelle des tables analytiques")


    # ========================================
    # TABS
    # ========================================
    st.write(f"DBT last run: {get_dbt_last_run()}")
    if st.button("DBT Run"):
        st.cache_data.clear()
        st.json(post_dbt_run_to_gateway())