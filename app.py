import streamlit as st
from utils.styles import inject_styles, svg
from utils.auth import login_form, show_sidebar_info

st.set_page_config(
    page_title="JobLens",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

inject_styles()

if not login_form():
    st.stop()

show_sidebar_info()

role = st.session_state.role
role_lower = role.lower()
name = st.session_state.full_name.split()[0]

# ── Welcome header ──
st.markdown(f"""
<div class="welcome-header animate-in">
    <div class="welcome-greeting">Welcome back</div>
    <div class="welcome-name">{name}</div>
    <span class="role-badge {role_lower}">{role}</span>
</div>
""", unsafe_allow_html=True)

# ── Navigation cards ──
st.markdown('<div class="section-label animate-in delay-2">Explore Modules</div>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(
        '<div class="nav-card purple animate-in delay-3">'
        f'<span class="nav-icon">{svg("dashboard", 28, "#a78bfa")}</span>'
        '<div class="nav-title">Market Overview</div>'
        '<div class="nav-desc">Interactive Power BI analytics and job market data exploration</div>'
        '</div>',
        unsafe_allow_html=True,
    )
    st.page_link("pages/1_Dashboard.py", label="Open Market Overview", use_container_width=True)

with col2:
    st.markdown(
        '<div class="nav-card blue animate-in delay-4">'
        f'<span class="nav-icon">{svg("salary", 28, "#38bdf8")}</span>'
        '<div class="nav-title">Salary Predictor</div>'
        '<div class="nav-desc">Predict salary &amp; degree requirements using machine learning models</div>'
        '</div>',
        unsafe_allow_html=True,
    )
    st.page_link("pages/2_ML_Prediction.py", label="Open Salary Predictor", use_container_width=True)

with col3:
    st.markdown(
        '<div class="nav-card orange animate-in delay-5">'
        f'<span class="nav-icon">{svg("forecast", 28, "#fbbf24")}</span>'
        '<div class="nav-title">Market Forecasting</div>'
        '<div class="nav-desc">6-month job demand forecast powered by deep learning ensembles</div>'
        '</div>',
        unsafe_allow_html=True,
    )
    st.page_link("pages/3_DL_Model.py", label="Open Forecasting", use_container_width=True)

with col4:
    st.markdown(
        '<div class="nav-card emerald animate-in delay-6">'
        f'<span class="nav-icon">{svg("advisor", 28, "#34d399")}</span>'
        '<div class="nav-title">Career Advisor</div>'
        '<div class="nav-desc">AI-powered job recommendations and personalized career guidance</div>'
        '</div>',
        unsafe_allow_html=True,
    )
    st.page_link("pages/4_NLP_Analysis.py", label="Open Career Advisor", use_container_width=True)

# ── Platform info ──
st.markdown('<div class="section-label animate-in delay-6">Platform Overview</div>', unsafe_allow_html=True)

col_a, col_b, col_c = st.columns(3)

with col_a:
    st.markdown("""
    <div class="glass-card animate-in delay-6">
        <div style="font-size: 0.7rem; font-weight: 700; text-transform: uppercase;
                    letter-spacing: 2px; color: #6C5CE7; margin-bottom: 12px;">Data Source</div>
        <div style="font-size: 1rem; font-weight: 600; color: #1e293b; margin-bottom: 6px;">
            785K+ Job Postings
        </div>
        <div style="font-size: 0.85rem; color: #cbd5e1;">
            Aggregated from multiple job platforms with 130K+ companies across 250+ skills
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_b:
    st.markdown("""
    <div class="glass-card animate-in delay-6">
        <div style="font-size: 0.7rem; font-weight: 700; text-transform: uppercase;
                    letter-spacing: 2px; color: #0EA5E9; margin-bottom: 12px;">Technology Stack</div>
        <div style="font-size: 1rem; font-weight: 600; color: #1e293b; margin-bottom: 6px;">
            Full-Stack AI Pipeline
        </div>
        <div style="font-size: 0.85rem; color: #cbd5e1;">
            PostgreSQL &middot; Streamlit &middot; Plotly &middot; Scikit-learn &middot; TensorFlow &middot; Transformers
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_c:
    st.markdown("""
    <div class="glass-card animate-in delay-6">
        <div style="font-size: 0.7rem; font-weight: 700; text-transform: uppercase;
                    letter-spacing: 2px; color: #10B981; margin-bottom: 12px;">Access Control</div>
        <div style="font-size: 1rem; font-weight: 600; color: #1e293b; margin-bottom: 6px;">
            Role-Based Security
        </div>
        <div style="font-size: 0.85rem; color: #cbd5e1;">
            Three-tier access: Admin (full), Recruiter (company), Candidate (public listings)
        </div>
    </div>
    """, unsafe_allow_html=True)
