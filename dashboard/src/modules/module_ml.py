# modules/module_transactions.py
import streamlit as st

# Cache
from utils.api_lib import get_health

# Tabs

def body():
    # ************************************************************************************************************
    # ========================================
    # CACHE SETUP
    # ========================================
    # Empty session_state cache of previous page
    # CACHE
    
    
    
    st.title("🦧 Machine Learning")
    st.markdown("Affiche la vue train")
    st.json(get_health())

    # ========================================
    # TABS
    # ========================================