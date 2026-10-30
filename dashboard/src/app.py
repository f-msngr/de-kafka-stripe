import streamlit as st
from pathlib import Path
import importlib
 
# ========================================
# GENERAL CONFIG
# ========================================
# Configure the Streamlit app
st.set_page_config(
    page_title="Stripe Dashboard",
    page_icon="🦣",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ========================================
# LOAD EXTERNAL CSS
# ========================================
def load_css(file_path):
    """Load external CSS file"""
    with open(file_path) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Load custom CSS
css_file = Path(__file__).parent / "assets" / "css" / "style.css"
load_css(css_file)

st.sidebar.markdown("---")

# Navigation with buttons
st.sidebar.markdown("### 🛺 Navigation")

# Dictionary of pages modules
d_modules = {
#    "Login": ("🔐", "modules.module_login"),
    "Machine Learning": ("🦧", "modules.module_ml"),
    "Analytics": ("🐎", "modules.module_analytics"),
    "Predict": ("🔮", "modules.module_predict"),
    "Admin": ("🗃️", "modules.module_admin")
}
# Initialize default page
if "page" not in st.session_state:
    st.session_state.page = list(d_modules.keys())[0]

for label, (emoji, module_page) in d_modules.items():
    if label == "Login":    # Login button is not displayed here
        continue
    btn_label = f"{emoji}  {label}"
    is_active = st.session_state.page == label
    
    if st.sidebar.button(
        btn_label,
        key=f"nav_{label}",
        use_container_width=True,
        type="primary" if is_active else "secondary"
    ):
        if not is_active:
            st.session_state.page = label
            st.rerun()

st.sidebar.markdown("---")

from utils.api_lib import get_health

try:
    health_status = get_health()
except Exception:
    health_status = None

if health_status and health_status.get("status") == "ok":
    st.sidebar.markdown("✅ API Gateway healthy")
else:
    st.sidebar.markdown("❌ API Gateway error")


# =========================
# LOAD AND RUN PAGE
# =========================
module = d_modules[st.session_state.page][1]
page = importlib.import_module(module)
page.body()


# ========================================
# FOOTER
# ========================================
# Footer
FOOTER_HTML = """
    <hr style="margin-top: 50px; border: none; border-top: 1px solid #ccc;" />
    <div style="text-align: center; color: gray; font-size: 14px; margin-top: 10px;">
        Made with 🦣 using 
        <a href="https://streamlit.io" target="_blank" style="text-decoration: none; color: #4CAF50;">
            Streamlit
        </a>
    </div>
"""
st.markdown(FOOTER_HTML, unsafe_allow_html=True)
