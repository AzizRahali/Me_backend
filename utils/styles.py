import time
import base64
import streamlit as st

# ── Professional inline SVG icon set (Lucide-style, stroke-based) ──
_ICON_PATHS = {
    "home": '<path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/>',
    "dashboard": '<rect width="7" height="9" x="3" y="3" rx="1.5"/><rect width="7" height="5" x="14" y="3" rx="1.5"/><rect width="7" height="9" x="14" y="12" rx="1.5"/><rect width="7" height="5" x="3" y="16" rx="1.5"/>',
    "salary": '<circle cx="12" cy="12" r="10"/><path d="M16 8h-6a2 2 0 1 0 0 4h4a2 2 0 1 1 0 4H8"/><path d="M12 18V6"/>',
    "forecast": '<path d="M3 3v18h18"/><path d="m19 9-5 5-4-4-3 3"/>',
    "advisor": '<path d="M9.937 15.5A2 2 0 0 0 8.5 14.063l-6.135-1.582a.5.5 0 0 1 0-.962L8.5 9.936A2 2 0 0 0 9.937 8.5l1.582-6.135a.5.5 0 0 1 .962 0L14.063 8.5A2 2 0 0 0 15.5 9.937l6.135 1.581a.5.5 0 0 1 0 .964L15.5 14.063a2 2 0 0 0-1.437 1.437l-1.582 6.135a.5.5 0 0 1-.962 0z"/><path d="M20 3v4"/><path d="M22 5h-4"/><path d="M4 17v2"/><path d="M5 18H3"/>',
}


def svg(name: str, size: int = 24, color: str = "#a78bfa", stroke_width: float = 2.0) -> str:
    """Return an icon as a base64 data-URI <img> (renders reliably in st.markdown)."""
    inner = _ICON_PATHS.get(name, "")
    raw = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
        f'viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="{stroke_width}" '
        f'stroke-linecap="round" stroke-linejoin="round">{inner}</svg>'
    )
    b64 = base64.b64encode(raw.encode("utf-8")).decode("ascii")
    return (
        f'<img src="data:image/svg+xml;base64,{b64}" width="{size}" height="{size}" '
        f'style="display:block;" alt="{name}"/>'
    )


GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --bg-primary: #0f0f1a;
    --bg-card: #1a1a2e;
    --bg-card-hover: #1e1e35;
    --border-subtle: rgba(255, 255, 255, 0.07);
    --border-accent: rgba(108, 92, 231, 0.35);
    --text-primary: #e2e8f0;
    --text-secondary: #cbd5e1;
    --text-muted: #cbd5e1;
    --accent-purple: #6C5CE7;
    --accent-blue: #0EA5E9;
    --accent-emerald: #10B981;
    --accent-orange: #F59E0B;
    --accent-rose: #F43F5E;
    --gradient-1: linear-gradient(135deg, #6C5CE7, #0EA5E9);
    --gradient-2: linear-gradient(135deg, #F43F5E, #F59E0B);
    --gradient-3: linear-gradient(135deg, #10B981, #0EA5E9);
    --gradient-4: linear-gradient(135deg, #6C5CE7, #F43F5E);
    --shadow-sm: 0 1px 3px rgba(0,0,0,0.3);
    --shadow-md: 0 4px 16px rgba(0,0,0,0.3);
    --shadow-lg: 0 8px 30px rgba(0,0,0,0.4);
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
    background: var(--bg-card) !important;
    border-right: 1px solid var(--border-subtle) !important;
    box-shadow: 2px 0 12px rgba(0,0,0,0.3);
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
    width: 58px; height: 58px;
    border-radius: 18px;
    display: flex; align-items: center; justify-content: center;
    margin: 0 auto 20px;
    color: #a78bfa;
    background: linear-gradient(135deg, rgba(108,92,231,0.15), rgba(14,165,233,0.08));
    border: 1px solid rgba(255,255,255,0.06);
    transition: transform 0.35s cubic-bezier(0.16,1,0.3,1);
}
.nav-card:hover .nav-icon { transform: scale(1.1) translateY(-2px); }

.nav-card.purple  .nav-icon { color:#a78bfa; background:linear-gradient(135deg, rgba(108,92,231,0.18), rgba(108,92,231,0.05)); }
.nav-card.blue    .nav-icon { color:#38bdf8; background:linear-gradient(135deg, rgba(14,165,233,0.18), rgba(14,165,233,0.05)); }
.nav-card.orange  .nav-icon { color:#fbbf24; background:linear-gradient(135deg, rgba(245,158,11,0.18), rgba(245,158,11,0.05)); }
.nav-card.emerald .nav-icon { color:#34d399; background:linear-gradient(135deg, rgba(16,185,129,0.18), rgba(16,185,129,0.05)); }

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

/* whole-card click target */
.nav-card-link { text-decoration: none !important; display: block; }
.nav-cta {
    margin-top: 16px;
    font-size: 0.8rem;
    font-weight: 700;
    color: var(--accent-purple);
    opacity: 0;
    transform: translateY(4px);
    transition: all 0.3s ease;
}
.nav-card:hover .nav-cta { opacity: 1; transform: translateY(0); }

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

/* ── Login page (centered) ── */
.login-logo {
    text-align: center;
    margin: 40px 0 28px;
    animation: fadeInUp 0.6s cubic-bezier(0.16,1,0.3,1) forwards;
}
.login-logo-icon {
    width: 64px; height: 64px; border-radius: 20px;
    display: inline-flex; align-items: center; justify-content: center;
    background: linear-gradient(135deg, #6C5CE7, #0EA5E9);
    font-size: 2rem;
    box-shadow: 0 8px 32px rgba(108,92,231,0.4);
    margin-bottom: 16px;
}
.login-title {
    font-size: 1.9rem; font-weight: 800;
    color: var(--text-primary); letter-spacing: -0.5px;
}
.login-subtitle {
    font-size: 0.92rem; color: var(--text-secondary); margin-top: 4px;
}

.login-box {
    background: var(--bg-card);
    border: 1px solid var(--border-subtle);
    border-radius: 20px;
    padding: 30px 28px;
    box-shadow: var(--shadow-md);
    animation: fadeInUp 0.6s cubic-bezier(0.16,1,0.3,1) 0.1s forwards;
    opacity: 0;
}

.demo-accounts {
    margin-top: 20px;
    padding: 18px;
    background: rgba(108, 92, 231, 0.05);
    border: 1px solid rgba(108, 92, 231, 0.12);
    border-radius: 16px;
    animation: fadeInUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) 0.4s forwards;
    opacity: 0;
}

.demo-title {
    font-size: 0.68rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 2px;
    color: var(--accent-purple);
    margin-bottom: 12px;
}

.demo-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 12px;
    border-radius: 10px;
    margin-bottom: 4px;
    transition: background 0.2s ease;
    cursor: default;
}

.demo-row:hover { background: rgba(108,92,231,0.06); }

.demo-email {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.74rem;
    color: var(--text-secondary);
}

.demo-pwd {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    color: var(--text-muted);
}

.demo-role {
    font-size: 0.68rem;
    font-weight: 700;
    padding: 3px 10px;
    border-radius: 6px;
    color: white;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}

.role-admin { background: linear-gradient(135deg, #6C5CE7, #F43F5E); }
.role-recruiter { background: linear-gradient(135deg, #6C5CE7, #0EA5E9); }
.role-candidate { background: linear-gradient(135deg, #10B981, #0EA5E9); }

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
    display: flex;
    align-items: center;
    gap: 18px;
    padding: 4px 0 24px 0;
    border-bottom: 1px solid var(--border-subtle);
    margin-bottom: 28px;
}

.page-header-icon {
    width: 56px; height: 56px;
    border-radius: 16px;
    display: flex; align-items: center; justify-content: center;
    background: linear-gradient(135deg, rgba(108,92,231,0.16), rgba(14,165,233,0.1));
    border: 1px solid rgba(108,92,231,0.2);
    color: #a78bfa;
    flex-shrink: 0;
    box-shadow: 0 4px 16px rgba(108,92,231,0.12);
}

.page-header-title {
    font-size: 1.9rem;
    font-weight: 800;
    color: var(--text-primary);
    letter-spacing: -0.5px;
    line-height: 1.15;
}

.page-header-sub {
    font-size: 0.92rem;
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

/* ── White input boxes with black text ── */
.stTextInput input,
.stTextArea textarea,
.stNumberInput input,
.stDateInput input {
    background-color: #ffffff !important;
    color: #111111 !important;
}
.stTextInput input::placeholder,
.stTextArea textarea::placeholder {
    color: #9ca3af !important;
}
/* selectbox / multiselect closed control */
div[data-baseweb="select"] > div {
    background-color: #ffffff !important;
}
div[data-baseweb="select"] > div,
div[data-baseweb="select"] span,
div[data-baseweb="select"] input {
    color: #111111 !important;
}
/* dropdown popover options */
ul[data-baseweb="menu"] { background-color: #ffffff !important; }
ul[data-baseweb="menu"] li { color: #111111 !important; }

/* ── Back button (small rounded pill) + main-area page links ── */
[data-testid="stMain"] a[data-testid="stPageLink-NavLink"] {
    border: 1px solid var(--border-subtle) !important;
    border-radius: 10px !important;
    padding: 8px 16px !important;
    background: var(--bg-card) !important;
    transition: all 0.25s ease !important;
}
[data-testid="stMain"] a[data-testid="stPageLink-NavLink"]:hover {
    border-color: var(--accent-purple) !important;
    background: var(--bg-card-hover) !important;
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

/* ── App loader (simulated fetch) ── */
.app-loader {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 22px;
    padding: 54px 20px;
    animation: fadeInScale 0.4s ease forwards;
}
.app-loader-ring {
    width: 58px; height: 58px;
    position: relative;
}
.app-loader-ring::before,
.app-loader-ring::after {
    content: '';
    position: absolute;
    border-radius: 50%;
    border: 3px solid transparent;
}
.app-loader-ring::before {
    inset: 0;
    border-top-color: #6C5CE7;
    border-right-color: #0EA5E9;
    animation: spin360 0.9s linear infinite;
}
.app-loader-ring::after {
    inset: 9px;
    border-bottom-color: #10B981;
    border-left-color: #34D399;
    animation: spin360 1.3s linear infinite reverse;
}
@keyframes spin360 { to { transform: rotate(360deg); } }

.app-loader-text {
    font-size: 0.95rem;
    font-weight: 600;
    color: var(--text-secondary);
    letter-spacing: 0.2px;
}
.app-loader-track {
    width: 220px; height: 4px;
    background: rgba(255,255,255,0.07);
    border-radius: 4px;
    overflow: hidden;
}
.app-loader-fill {
    height: 100%;
    width: 35%;
    border-radius: 4px;
    background: linear-gradient(90deg, #6C5CE7, #0EA5E9, #10B981);
    animation: loaderSlide 1.15s cubic-bezier(0.4,0,0.2,1) infinite;
}
@keyframes loaderSlide {
    0% { transform: translateX(-130%); }
    100% { transform: translateX(420%); }
}
</style>
"""


def inject_styles():
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


def page_header(icon: str, title: str, subtitle: str):
    icon_html = svg(icon, 28) if icon in _ICON_PATHS else f'<span style="font-size:1.6rem;">{icon}</span>'
    st.markdown(f"""
    <div class="page-header animate-in">
        <div class="page-header-icon">{icon_html}</div>
        <div class="page-header-text">
            <div class="page-header-title">{title}</div>
            <div class="page-header-sub">{subtitle}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def back_to_home():
    col = st.columns([1, 7])[0]
    with col:
        st.page_link("app.py", label="Back")


def section_label(text: str):
    st.markdown(f'<div class="section-label">{text}</div>', unsafe_allow_html=True)


def show_loading(message: str = "Analyzing data", seconds: float = 3.0):
    """Display a branded loading animation for the given duration (simulated fetch)."""
    placeholder = st.empty()
    placeholder.markdown(f"""
    <div class="app-loader">
        <div class="app-loader-ring"></div>
        <div class="app-loader-text">{message}</div>
        <div class="app-loader-track"><div class="app-loader-fill"></div></div>
    </div>
    """, unsafe_allow_html=True)
    time.sleep(seconds)
    placeholder.empty()


PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="#1a1a2e",
    font=dict(family="Outfit, sans-serif", color="#cbd5e1", size=12),
    margin=dict(l=40, r=20, t=40, b=40),
    xaxis=dict(gridcolor="rgba(255,255,255,0.05)", zerolinecolor="rgba(255,255,255,0.05)"),
    yaxis=dict(gridcolor="rgba(255,255,255,0.05)", zerolinecolor="rgba(255,255,255,0.05)"),
    legend=dict(bgcolor="rgba(26,26,46,0.8)", font=dict(size=11, color="#e2e8f0")),
    hoverlabel=dict(bgcolor="#1a1a2e", font_size=13, font_family="Outfit", bordercolor="#6C5CE7"),
)

COLORS = ["#6C5CE7", "#0EA5E9", "#10B981", "#F59E0B", "#F43F5E", "#8B5CF6", "#06B6D4", "#34D399", "#FBBF24", "#FB7185"]
