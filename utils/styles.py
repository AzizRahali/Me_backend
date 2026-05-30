import streamlit as st

GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --bg-primary: #f5f6fa;
    --bg-card: #ffffff;
    --bg-card-hover: #f8f9ff;
    --border-subtle: rgba(0, 0, 0, 0.07);
    --border-accent: rgba(108, 92, 231, 0.25);
    --text-primary: #1e293b;
    --text-secondary: #64748b;
    --text-muted: #94a3b8;
    --accent-purple: #6C5CE7;
    --accent-blue: #0EA5E9;
    --accent-emerald: #10B981;
    --accent-orange: #F59E0B;
    --accent-rose: #F43F5E;
    --gradient-1: linear-gradient(135deg, #6C5CE7, #0EA5E9);
    --gradient-2: linear-gradient(135deg, #F43F5E, #F59E0B);
    --gradient-3: linear-gradient(135deg, #10B981, #0EA5E9);
    --gradient-4: linear-gradient(135deg, #6C5CE7, #F43F5E);
    --shadow-sm: 0 1px 3px rgba(0,0,0,0.06);
    --shadow-md: 0 4px 16px rgba(0,0,0,0.06);
    --shadow-lg: 0 8px 30px rgba(0,0,0,0.08);
}

/* ── Global Reset ── */
.stApp {
    font-family: 'Outfit', sans-serif !important;
    background: var(--bg-primary) !important;
}

.stApp > header { display: none; }

h1, h2, h3, h4, h5, h6, p, span, div, label, .stMarkdown {
    font-family: 'Outfit', sans-serif !important;
}

code, pre, .stCode {
    font-family: 'JetBrains Mono', monospace !important;
}

/* ── Hide Streamlit defaults ── */
#MainMenu, footer, .stDeployButton { display: none !important; }
div[data-testid="stSidebarNav"] { display: none !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--bg-primary); }
::-webkit-scrollbar-thumb { background: #c4b5fd; border-radius: 3px; }

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: #ffffff !important;
    border-right: 1px solid var(--border-subtle) !important;
    box-shadow: 2px 0 12px rgba(0,0,0,0.03);
}

section[data-testid="stSidebar"] .stMarkdown p {
    color: var(--text-secondary);
    font-size: 0.9rem;
}

/* ── Buttons ── */
.stButton > button {
    font-family: 'Outfit', sans-serif !important;
    font-weight: 600;
    border: 1px solid var(--border-subtle);
    border-radius: 12px;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    background: var(--bg-card);
    color: var(--text-primary);
    box-shadow: var(--shadow-sm);
}

.stButton > button:hover {
    border-color: var(--accent-purple);
    box-shadow: 0 4px 16px rgba(108, 92, 231, 0.12);
    transform: translateY(-1px);
}

/* ── Form inputs ── */
.stTextInput > div > div > input {
    font-family: 'Outfit', sans-serif !important;
    background: #ffffff !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: 12px !important;
    color: var(--text-primary) !important;
    padding: 12px 16px !important;
    transition: all 0.3s ease;
}

.stTextInput > div > div > input:focus {
    border-color: var(--accent-purple) !important;
    box-shadow: 0 0 0 3px rgba(108, 92, 231, 0.1) !important;
}

/* ── Form submit ── */
.stFormSubmitButton > button {
    font-family: 'Outfit', sans-serif !important;
    font-weight: 700;
    background: var(--gradient-1) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 12px 32px !important;
    font-size: 1rem !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.stFormSubmitButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 30px rgba(108, 92, 231, 0.2);
}

/* ── Animations ── */
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes fadeInScale {
    from { opacity: 0; transform: scale(0.96); }
    to { opacity: 1; transform: scale(1); }
}

@keyframes shimmer {
    0% { background-position: -200% center; }
    100% { background-position: 200% center; }
}

@keyframes pulseGlow {
    0%, 100% { box-shadow: 0 0 12px rgba(108, 92, 231, 0.08); }
    50% { box-shadow: 0 0 24px rgba(108, 92, 231, 0.15); }
}

.animate-in {
    animation: fadeInUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    opacity: 0;
}

.delay-1 { animation-delay: 0.1s; }
.delay-2 { animation-delay: 0.15s; }
.delay-3 { animation-delay: 0.2s; }
.delay-4 { animation-delay: 0.25s; }
.delay-5 { animation-delay: 0.3s; }
.delay-6 { animation-delay: 0.35s; }

/* ── Glass card (light) ── */
.glass-card {
    background: var(--bg-card);
    border: 1px solid var(--border-subtle);
    border-radius: 20px;
    padding: 28px;
    box-shadow: var(--shadow-md);
    transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
}

.glass-card:hover {
    background: var(--bg-card-hover);
    border-color: var(--border-accent);
    transform: translateY(-4px);
    box-shadow: var(--shadow-lg);
}

/* ── Nav card ── */
.nav-card {
    background: var(--bg-card);
    border: 1px solid var(--border-subtle);
    border-radius: 20px;
    padding: 32px 28px;
    text-align: center;
    box-shadow: var(--shadow-sm);
    transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
    cursor: pointer;
    position: relative;
    overflow: hidden;
}

.nav-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 100%; height: 3px;
    border-radius: 20px 20px 0 0;
    opacity: 0;
    transition: opacity 0.35s ease;
}

.nav-card:hover::before { opacity: 1; }
.nav-card:hover {
    transform: translateY(-6px);
    box-shadow: var(--shadow-lg);
}

.nav-card.purple::before { background: var(--gradient-1); }
.nav-card.purple:hover { border-color: rgba(108, 92, 231, 0.25); }
.nav-card.blue::before { background: var(--gradient-3); }
.nav-card.blue:hover { border-color: rgba(14, 165, 233, 0.25); }
.nav-card.orange::before { background: var(--gradient-2); }
.nav-card.orange:hover { border-color: rgba(245, 158, 11, 0.25); }
.nav-card.emerald::before { background: var(--gradient-3); }
.nav-card.emerald:hover { border-color: rgba(16, 185, 129, 0.25); }

.nav-icon {
    font-size: 2.8rem;
    margin-bottom: 16px;
    display: block;
}

.nav-title {
    font-size: 1.15rem;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 8px;
}

.nav-desc {
    font-size: 0.85rem;
    color: var(--text-secondary);
    line-height: 1.5;
}

/* ── KPI metric ── */
.kpi-card {
    background: var(--bg-card);
    border: 1px solid var(--border-subtle);
    border-radius: 16px;
    padding: 24px;
    text-align: center;
    box-shadow: var(--shadow-sm);
}

.kpi-value {
    font-size: 2.2rem;
    font-weight: 800;
    letter-spacing: -1px;
    background: var(--gradient-1);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.kpi-label {
    font-size: 0.8rem;
    font-weight: 500;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-top: 6px;
}

/* ── Login page ── */
.login-container {
    max-width: 420px;
    margin: 0 auto;
    padding-top: 60px;
}

.login-logo {
    text-align: center;
    margin-bottom: 40px;
}

.login-logo-icon {
    font-size: 3.5rem;
    display: block;
    margin-bottom: 16px;
    animation: fadeInScale 1s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

.login-title {
    font-size: 1.8rem;
    font-weight: 800;
    color: var(--text-primary);
    margin-bottom: 4px;
}

.login-subtitle {
    font-size: 0.95rem;
    color: var(--text-secondary);
}

.login-box {
    background: var(--bg-card);
    border: 1px solid var(--border-subtle);
    border-radius: 24px;
    padding: 36px 32px;
    box-shadow: var(--shadow-md);
    animation: fadeInUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) 0.2s forwards;
    opacity: 0;
}

.demo-accounts {
    margin-top: 32px;
    padding: 20px;
    background: rgba(108, 92, 231, 0.04);
    border: 1px solid rgba(108, 92, 231, 0.1);
    border-radius: 16px;
    animation: fadeInUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) 0.4s forwards;
    opacity: 0;
}

.demo-title {
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 2px;
    color: var(--accent-purple);
    margin-bottom: 14px;
}

.demo-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px 14px;
    border-radius: 10px;
    margin-bottom: 6px;
    transition: background 0.2s ease;
}

.demo-row:hover { background: rgba(0, 0, 0, 0.02); }

.demo-email {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.78rem;
    color: var(--text-secondary);
}

.demo-role {
    font-size: 0.75rem;
    font-weight: 600;
    padding: 3px 10px;
    border-radius: 6px;
    color: white;
}

.role-admin { background: var(--accent-purple); }
.role-recruiter { background: var(--accent-blue); }
.role-candidate { background: var(--accent-emerald); }

/* ── Welcome header ── */
.welcome-header {
    padding: 20px 0 30px 0;
}

.welcome-greeting {
    font-size: 0.85rem;
    font-weight: 500;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 2px;
    margin-bottom: 8px;
}

.welcome-name {
    font-size: 2.4rem;
    font-weight: 800;
    color: var(--text-primary);
    line-height: 1.2;
}

.role-badge {
    display: inline-block;
    font-size: 0.8rem;
    font-weight: 600;
    padding: 5px 14px;
    border-radius: 8px;
    margin-top: 12px;
    color: white;
}

.role-badge.admin { background: var(--gradient-4); }
.role-badge.recruiter { background: var(--gradient-1); }
.role-badge.candidate { background: var(--gradient-3); }

/* ── Section divider ── */
.section-label {
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 3px;
    color: var(--text-muted);
    margin: 40px 0 20px 0;
    padding-bottom: 12px;
    border-bottom: 1px solid var(--border-subtle);
}

/* ── Page header ── */
.page-header {
    padding: 10px 0 30px 0;
    border-bottom: 1px solid var(--border-subtle);
    margin-bottom: 30px;
}

.page-header-icon { font-size: 2rem; margin-bottom: 10px; display: block; }

.page-header-title {
    font-size: 2rem;
    font-weight: 800;
    color: var(--text-primary);
}

.page-header-sub {
    font-size: 0.95rem;
    color: var(--text-secondary);
    margin-top: 4px;
}

/* ── Back link ── */
.back-link {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-size: 0.82rem;
    font-weight: 600;
    color: var(--accent-purple);
    margin-bottom: 8px;
    cursor: pointer;
    transition: all 0.2s ease;
}
.back-link:hover { opacity: 0.7; }

/* ── Plotly chart containers ── */
.chart-container {
    background: var(--bg-card);
    border: 1px solid var(--border-subtle);
    border-radius: 20px;
    padding: 24px;
    margin-bottom: 20px;
    box-shadow: var(--shadow-sm);
}

.chart-title {
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 2px;
    color: var(--text-muted);
    margin-bottom: 16px;
}

/* ── Streamlit overrides ── */
div[data-testid="stMetric"] {
    background: var(--bg-card);
    border: 1px solid var(--border-subtle);
    border-radius: 16px;
    padding: 20px;
    box-shadow: var(--shadow-sm);
}

div[data-testid="stMetric"] label {
    color: var(--text-secondary) !important;
    font-size: 0.8rem !important;
    text-transform: uppercase;
    letter-spacing: 1px;
}

div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
    font-size: 2rem !important;
    font-weight: 800 !important;
}

.stSelectbox label, .stMultiSelect label {
    font-size: 0.8rem !important;
    font-weight: 600 !important;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: var(--text-secondary) !important;
}

/* ── Hide fullscreen buttons on charts ── */
button[title="View fullscreen"] { display: none !important; }

/* ── Info/Warning boxes ── */
.stAlert {
    border-radius: 16px !important;
    border: none !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    border-bottom: 1px solid var(--border-subtle);
}
.stTabs [data-baseweb="tab"] {
    border-radius: 10px 10px 0 0;
    padding: 10px 20px;
    font-weight: 600;
    color: var(--text-secondary);
}
.stTabs [aria-selected="true"] {
    background: rgba(108,92,231,0.06) !important;
    color: #6C5CE7 !important;
    border-bottom: 2px solid #6C5CE7;
}
</style>
"""


def inject_styles():
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


def page_header(icon: str, title: str, subtitle: str):
    st.markdown(f"""
    <div class="page-header animate-in">
        <span class="page-header-icon">{icon}</span>
        <div class="page-header-title">{title}</div>
        <div class="page-header-sub">{subtitle}</div>
    </div>
    """, unsafe_allow_html=True)


def back_to_home():
    st.page_link("app.py", label="< Back to Home", icon="🏠")


def section_label(text: str):
    st.markdown(f'<div class="section-label">{text}</div>', unsafe_allow_html=True)


PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="#ffffff",
    font=dict(family="Outfit, sans-serif", color="#64748b", size=12),
    margin=dict(l=40, r=20, t=40, b=40),
    xaxis=dict(gridcolor="rgba(0,0,0,0.05)", zerolinecolor="rgba(0,0,0,0.05)"),
    yaxis=dict(gridcolor="rgba(0,0,0,0.05)", zerolinecolor="rgba(0,0,0,0.05)"),
    legend=dict(bgcolor="rgba(255,255,255,0.8)", font=dict(size=11, color="#1e293b")),
    hoverlabel=dict(bgcolor="#ffffff", font_size=13, font_family="Outfit", bordercolor="#e2e8f0"),
)

COLORS = ["#6C5CE7", "#0EA5E9", "#10B981", "#F59E0B", "#F43F5E", "#8B5CF6", "#06B6D4", "#34D399", "#FBBF24", "#FB7185"]
