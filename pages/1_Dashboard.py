import os
import streamlit as st
from dotenv import load_dotenv
from utils.styles import inject_styles, page_header, back_to_home, show_loading
from utils.auth import require_auth, show_sidebar_info

load_dotenv()

st.set_page_config(page_title="Market Overview | JobLens", page_icon="◈", layout="wide")
inject_styles()
require_auth()
show_sidebar_info()

back_to_home()
page_header("dashboard", "Market Overview", "Power BI interactive analytics and data exploration")

POWERBI_URL = os.getenv("POWERBI_EMBED_URL", "")

if not POWERBI_URL or "YOUR_EMBED_ID" in POWERBI_URL:
    st.warning("Power BI embed URL not configured. Update POWERBI_EMBED_URL in your .env file.")
else:
    # One-time loading animation when the dashboard first opens
    if not st.session_state.get("dashboard_loaded", False):
        show_loading("Loading market analytics", 3.0)
        st.session_state["dashboard_loaded"] = True

    st.markdown("""
    <div style="font-size: 0.78rem; color: #cbd5e1; margin-bottom: 16px; padding: 12px 16px;
                background: rgba(108, 92, 231, 0.04); border: 1px solid rgba(108, 92, 231, 0.1);
                border-radius: 12px;">
        Ensure you are signed into your Microsoft account in this browser for the dashboard to load.
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="glass-card animate-in" style="padding: 0; overflow: hidden;">
        <iframe src="{POWERBI_URL}" width="100%" height="700"
                frameborder="0" allowFullScreen="true"
                style="border-radius: 20px; display: block;">
        </iframe>
    </div>
    """, unsafe_allow_html=True)
