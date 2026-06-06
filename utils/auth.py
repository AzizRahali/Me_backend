import hashlib
import streamlit as st

# ── Static user registry (no database needed) ──
USERS = {
    "azizrahali3@gmail.com": {
        "password_hash": hashlib.sha256(b"candidate123").hexdigest(),
        "role": "Candidate",
        "full_name": "Aziz Rahali",
    },
    "bayoudhimed@gmail.com": {
        "password_hash": hashlib.sha256(b"recruiter123").hexdigest(),
        "role": "Recruiter",
        "full_name": "Bayoudh Imed",
    },
    "aziz.rahali@wecioo.com": {
        "password_hash": hashlib.sha256(b"admin123").hexdigest(),
        "role": "Admin",
        "full_name": "Aziz Rahali",
    },
}


def check_password(email: str, password: str) -> dict | None:
    user = USERS.get(email)
    if user and user["password_hash"] == hashlib.sha256(password.encode()).hexdigest():
        return {"email": email, "role": user["role"], "full_name": user["full_name"]}
    return None


def login_form():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if st.session_state.authenticated:
        return True

    # ── Centered login ──
    col_l, col_c, col_r = st.columns([1, 1.4, 1])
    with col_c:
        st.markdown(
            '<div class="login-logo">'
            '<div class="login-logo-icon">&#9672;</div>'
            '<div class="login-title">JobLens</div>'
            '<div class="login-subtitle">Job Market Intelligence Platform</div>'
            '</div>',
            unsafe_allow_html=True,
        )

        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        with st.form("login_form"):
            email = st.text_input("Email address", placeholder="you@example.com")
            password = st.text_input("Password", type="password", placeholder="••••••••••")
            submitted = st.form_submit_button("Sign In", use_container_width=True, type="primary")
        st.markdown('</div>', unsafe_allow_html=True)

        if submitted:
            user = check_password(email, password)
            if user:
                st.session_state.authenticated = True
                st.session_state.email = user["email"]
                st.session_state.role = user["role"]
                st.session_state.full_name = user["full_name"]
                st.rerun()
            else:
                st.error("Invalid email or password.")

        # ── Demo accounts ──
        st.markdown(
            '<div class="demo-accounts">'
            '<div class="demo-title">&#128274; Demo Accounts</div>'
            '<div class="demo-row"><span class="demo-email">aziz.rahali@wecioo.com</span>'
            '<span class="demo-role role-admin">Admin</span></div>'
            '<div class="demo-row"><span class="demo-email">bayoudhimed@gmail.com</span>'
            '<span class="demo-role role-recruiter">Recruiter</span></div>'
            '<div class="demo-row"><span class="demo-email">azizrahali3@gmail.com</span>'
            '<span class="demo-role role-candidate">Candidate</span></div>'
            '<div style="margin-top:10px;padding:8px 12px;background:rgba(108,92,231,0.06);'
            'border-radius:8px;font-size:0.72rem;color:#cbd5e1;text-align:center;">'
            'Password: <span style="font-family:\'JetBrains Mono\',monospace;color:#a78bfa;">role + 123</span>'
            '&nbsp;&nbsp;e.g. <span style="font-family:\'JetBrains Mono\',monospace;color:#a78bfa;">admin123</span>'
            '</div>'
            '</div>',
            unsafe_allow_html=True,
        )

    return False


def require_auth():
    if not st.session_state.get("authenticated", False):
        st.warning("Please login from the home page.")
        st.stop()


def get_role():
    return st.session_state.get("role", "Candidate")


def show_sidebar_info():
    role = st.session_state.get("role", "")
    role_lower = role.lower()
    initials = "".join([w[0] for w in st.session_state.get("full_name", "U").split()[:2]]).upper()

    accent_map = {
        "admin": ("#6C5CE7", "linear-gradient(135deg, #6C5CE7, #F43F5E)"),
        "recruiter": ("#0EA5E9", "linear-gradient(135deg, #6C5CE7, #0EA5E9)"),
        "candidate": ("#10B981", "linear-gradient(135deg, #10B981, #0EA5E9)"),
    }
    accent_color, accent_gradient = accent_map.get(role_lower, ("#6C5CE7", "linear-gradient(135deg, #6C5CE7, #0EA5E9)"))

    with st.sidebar:
        if st.session_state.get("authenticated", False):

            st.markdown(f"""
            <style>
                section[data-testid="stSidebar"] {{
                    background: #1a1a2e !important;
                    border-right: 1px solid rgba(255,255,255,0.07) !important;
                    box-shadow: 2px 0 12px rgba(0,0,0,0.3);
                }}
                section[data-testid="stSidebar"] > div:first-child {{
                    padding-top: 1rem;
                }}
                div[data-testid="stSidebarNav"] {{ display: none !important; }}
                section[data-testid="stSidebar"] a {{
                    text-decoration: none !important;
                }}

                .sb-nav-link {{
                    display: flex; align-items: center; gap: 14px;
                    padding: 13px 18px; margin: 3px 8px;
                    border-radius: 14px; cursor: pointer;
                    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
                    text-decoration: none !important;
                    border: 1px solid transparent;
                }}
                .sb-nav-link:hover {{
                    background: rgba(108, 92, 231, 0.04);
                    border-color: rgba(108, 92, 231, 0.08);
                    transform: translateX(4px);
                }}

                .sb-divider {{
                    height: 1px;
                    background: linear-gradient(90deg, transparent, rgba(0,0,0,0.06), transparent);
                    margin: 16px 20px;
                }}

                .sb-section {{
                    font-family: 'Outfit', sans-serif;
                    font-size: 0.62rem; font-weight: 700;
                    text-transform: uppercase; letter-spacing: 2.5px;
                    color: #cbd5e1;
                    padding: 8px 26px 6px;
                }}

                .sb-profile {{
                    margin: 6px 8px; padding: 18px;
                    border-radius: 16px;
                    background: rgba(255,255,255,0.04);
                    border: 1px solid rgba(255,255,255,0.07);
                    transition: all 0.3s ease;
                }}
                .sb-profile:hover {{
                    background: rgba(255,255,255,0.07);
                    border-color: rgba(108,92,231,0.2);
                }}
                .sb-profile-top {{ display: flex; align-items: center; gap: 14px; }}
                .sb-avatar {{
                    width: 44px; height: 44px; border-radius: 13px;
                    background: {accent_gradient};
                    display: flex; align-items: center; justify-content: center;
                    font-family: 'Outfit', sans-serif; font-weight: 800;
                    font-size: 0.95rem; color: white; flex-shrink: 0;
                    box-shadow: 0 4px 12px {accent_color}25;
                }}
                .sb-profile-info {{ overflow: hidden; }}
                .sb-profile-name {{
                    font-family: 'Outfit', sans-serif; font-size: 0.92rem;
                    font-weight: 700; color: #e2e8f0;
                    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
                }}
                .sb-profile-email {{
                    font-family: 'JetBrains Mono', monospace; font-size: 0.68rem;
                    color: #cbd5e1;
                    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
                    margin-top: 2px;
                }}
                .sb-role-pill {{
                    display: inline-block; margin-top: 12px;
                    font-family: 'Outfit', sans-serif; font-size: 0.68rem;
                    font-weight: 700; text-transform: uppercase; letter-spacing: 1.5px;
                    padding: 5px 14px; border-radius: 8px;
                    background: {accent_gradient}; color: white;
                    box-shadow: 0 2px 8px {accent_color}18;
                }}

                .sb-logo {{ display: flex; align-items: center; gap: 12px; padding: 8px 20px 4px; margin-bottom: 4px; }}
                .sb-logo-mark {{
                    width: 36px; height: 36px; border-radius: 11px;
                    background: {accent_gradient};
                    display: flex; align-items: center; justify-content: center;
                    font-size: 1.1rem;
                    box-shadow: 0 4px 16px {accent_color}20;
                }}
                .sb-logo-text {{ font-family: 'Outfit', sans-serif; font-size: 1.35rem; font-weight: 800; color: #e2e8f0; letter-spacing: -0.5px; }}
                .sb-logo-sub {{
                    font-family: 'Outfit', sans-serif; font-size: 0.6rem;
                    color: #cbd5e1; letter-spacing: 2px; text-transform: uppercase;
                    padding-left: 20px; margin-top: -2px; margin-bottom: 4px;
                }}

                .sb-signout-wrap .stButton > button {{
                    background: rgba(244, 63, 94, 0.05) !important;
                    border: 1px solid rgba(244, 63, 94, 0.12) !important;
                    color: #F43F5E !important;
                    font-size: 0.82rem !important; font-weight: 600 !important;
                    border-radius: 12px !important; padding: 10px !important;
                    margin-top: 4px; transition: all 0.3s ease;
                    box-shadow: none !important;
                }}
                .sb-signout-wrap .stButton > button:hover {{
                    background: rgba(244, 63, 94, 0.1) !important;
                    border-color: rgba(244, 63, 94, 0.2) !important;
                    transform: none;
                }}

                /* page link overrides */
                section[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"] {{
                    display: flex !important; align-items: center !important; gap: 10px !important;
                    padding: 13px 18px !important; margin: 3px 0 !important;
                    border-radius: 14px !important; border: 1px solid transparent !important;
                    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
                    text-decoration: none !important; background: transparent !important;
                }}
                section[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"]:hover {{
                    background: rgba(108, 92, 231, 0.1) !important;
                    border-color: rgba(108, 92, 231, 0.2) !important;
                    transform: translateX(4px);
                }}
                section[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"] span,
                section[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"] p {{
                    font-family: 'Outfit', sans-serif !important;
                    font-size: 0.88rem !important; font-weight: 500 !important;
                    color: #cbd5e1 !important; transition: color 0.25s ease !important;
                }}
                section[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"]:hover span,
                section[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"]:hover p {{
                    color: #e2e8f0 !important;
                }}
            </style>

            <div class="sb-logo">
                <div class="sb-logo-mark">&#9672;</div>
                <div class="sb-logo-text">JobLens</div>
            </div>
            <div class="sb-logo-sub">Intelligence Platform</div>

            <div class="sb-divider"></div>

            <div class="sb-profile">
                <div class="sb-profile-top">
                    <div class="sb-avatar">{initials}</div>
                    <div class="sb-profile-info">
                        <div class="sb-profile-name">{st.session_state.full_name}</div>
                        <div class="sb-profile-email">{st.session_state.email}</div>
                    </div>
                </div>
                <span class="sb-role-pill">{role}</span>
            </div>

            <div class="sb-divider"></div>

            <div class="sb-section">Navigation</div>
            """, unsafe_allow_html=True)

            st.page_link("app.py", label="Home")
            st.page_link("pages/1_Dashboard.py", label="Market Overview")

            st.markdown('<div class="sb-section" style="margin-top: 10px;">AI Models</div>', unsafe_allow_html=True)

            st.page_link("pages/2_ML_Prediction.py", label="Salary Predictor")
            st.page_link("pages/3_DL_Model.py", label="Market Forecasting")
            st.page_link("pages/4_NLP_Analysis.py", label="Career Advisor")

            st.markdown('<div class="sb-divider"></div>', unsafe_allow_html=True)

            st.markdown('<div class="sb-signout-wrap">', unsafe_allow_html=True)
            if st.button("Sign Out", use_container_width=True):
                for key in ["authenticated", "email", "role", "full_name"]:
                    st.session_state.pop(key, None)
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
