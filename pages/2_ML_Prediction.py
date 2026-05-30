import os
import streamlit as st
import requests
from dotenv import load_dotenv
from utils.styles import inject_styles, page_header, section_label, back_to_home
from utils.auth import require_auth, show_sidebar_info, get_role

load_dotenv()

st.set_page_config(page_title="Salary Predictor | JobLens", page_icon="◈", layout="wide")
inject_styles()
require_auth()
show_sidebar_info()

back_to_home()
page_header("🤖", "Salary Predictor",
            "Predict salary & degree requirements for data-related jobs using machine learning")

# ── Page-specific styles ──
st.markdown("""
<style>
    .salary-result {
        text-align: center;
        padding: 40px 20px;
        background: #ffffff;
        border: 1px solid rgba(0,0,0,0.06);
        border-radius: 24px;
        margin: 20px 0;
        box-shadow: 0 4px 16px rgba(0,0,0,0.04);
        animation: fadeInScale 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    }
    .salary-label {
        font-size: 0.7rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 2.5px;
        color: #64748b;
        margin-bottom: 12px;
    }
    .salary-amount {
        font-size: 3.5rem;
        font-weight: 900;
        letter-spacing: -2px;
        background: linear-gradient(135deg, #10B981, #0EA5E9);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        line-height: 1.1;
    }
    .salary-unit {
        font-size: 1rem;
        color: #94a3b8;
        margin-top: 8px;
        font-weight: 500;
    }

    /* Degree prediction card */
    .degree-result {
        text-align: center;
        padding: 30px 20px;
        background: #ffffff;
        border: 1px solid rgba(0,0,0,0.06);
        border-radius: 24px;
        margin-bottom: 16px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.04);
        animation: fadeInScale 0.5s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    }
    .degree-label-header {
        font-size: 0.7rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 2.5px;
        color: #64748b;
        margin-bottom: 16px;
    }
    .degree-verdict {
        font-size: 1.3rem;
        font-weight: 800;
        margin-bottom: 6px;
    }
    .degree-verdict.no-degree {
        background: linear-gradient(135deg, #10B981, #34D399);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .degree-verdict.degree-needed {
        background: linear-gradient(135deg, #F59E0B, #F97316);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .degree-prob {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.82rem;
        color: #64748b;
        margin-top: 4px;
    }

    /* Probability bar */
    .prob-bar-wrap {
        width: 100%;
        height: 8px;
        background: #f1f5f9;
        border-radius: 4px;
        margin: 14px 0 6px;
        overflow: hidden;
    }
    .prob-bar-fill {
        height: 100%;
        border-radius: 4px;
        transition: width 0.6s ease;
    }
    .prob-bar-fill.high { background: linear-gradient(90deg, #10B981, #34D399); }
    .prob-bar-fill.mid  { background: linear-gradient(90deg, #F59E0B, #FBBF24); }
    .prob-bar-fill.low  { background: linear-gradient(90deg, #F43F5E, #FB7185); }

    /* Feed indicator */
    .feed-indicator {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 6px;
        font-size: 0.7rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        color: #94a3b8;
        margin: 8px 0 4px;
    }
    .feed-arrow {
        font-size: 1rem;
        color: #6C5CE7;
        animation: pulseGlow 2s infinite;
    }

    .form-section {
        background: #ffffff;
        border: 1px solid rgba(0,0,0,0.06);
        border-radius: 20px;
        padding: 28px;
        margin-bottom: 20px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.03);
    }
    .form-section-title {
        font-size: 0.68rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 2px;
        color: #6C5CE7;
        margin-bottom: 18px;
    }

    .skill-chip {
        display: inline-block;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        font-weight: 500;
        padding: 5px 14px;
        margin: 3px;
        border-radius: 8px;
        background: rgba(108,92,231,0.08);
        border: 1px solid rgba(108,92,231,0.15);
        color: #6C5CE7;
    }

</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
# API CONNECTIONS
# ═══════════════════════════════════════════════════════════
API_URL = os.getenv("API_URL", "http://localhost:10000")


@st.cache_data(ttl=300)
def fetch_salary_metadata():
    try:
        resp = requests.get(f"{API_URL}/salary/metadata", timeout=10)
        resp.raise_for_status()
        return resp.json(), True
    except Exception:
        return None, False


@st.cache_data(ttl=300)
def fetch_degree_metadata():
    try:
        resp = requests.get(f"{API_URL}/degree/metadata", timeout=10)
        resp.raise_for_status()
        return resp.json(), True
    except Exception:
        return None, False


def predict_salary(payload: dict) -> dict | None:
    try:
        resp = requests.post(f"{API_URL}/salary/predict", json=payload, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        st.error(f"Salary prediction failed: {e}")
        return None


def predict_degree(payload: dict) -> dict | None:
    try:
        resp = requests.post(f"{API_URL}/degree/predict", json=payload, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        st.error(f"Degree prediction failed: {e}")
        return None


# ── Load metadata from both APIs ──
salary_meta, salary_online = fetch_salary_metadata()
degree_meta, degree_online = fetch_degree_metadata()

salary_options = salary_meta.get("options", {}) if salary_meta else {}

# If salary API is offline, stop
if not salary_online:
    st.error("Salary prediction service is currently unavailable. Please try again later.")
    st.stop()


# ══════════════════════════════════════════════════════════════
# PREDICTION FORM
# ══════════════════════════════════════════════════════════════

section_label("Job Details")

col_left, col_right = st.columns([2, 1])

with col_left:

    # ── Job Information ──
    st.markdown(
        '<div class="form-section"><div class="form-section-title">Job Information</div>',
        unsafe_allow_html=True,
    )

    fc1, fc2 = st.columns(2)
    with fc1:
        job_title_short = st.selectbox(
            "Job Role",
            options=salary_options.get("job_title_short", []),
            index=0,
            key="ml_role",
        )
    with fc2:
        job_country = st.selectbox(
            "Country",
            options=salary_options.get("job_country", []),
            index=0,
            key="ml_country",
        )

    fc3, fc4 = st.columns(2)
    with fc3:
        schedule_type = st.selectbox(
            "Contract Type",
            options=[
                "Full-time",
                "Part-time",
                "Contractor",
                "Full-time and Contractor",
                "Full-time and Part-time",
                "Internship",
            ],
            index=0,
            key="ml_schedule",
        )
    with fc4:
        company_size = st.selectbox(
            "Company Size",
            options=salary_options.get("company_size", []),
            index=0,
            key="ml_size",
        )

    job_title = st.text_input(
        "Full Job Title",
        value=f"Senior {job_title_short}",
        placeholder="e.g. Senior Machine Learning Data Scientist",
        key="ml_title",
    )

    st.markdown("</div>", unsafe_allow_html=True)

    # ── Skills ──
    st.markdown(
        '<div class="form-section"><div class="form-section-title">Skills</div>',
        unsafe_allow_html=True,
    )

    common_skills = [
        "python", "sql", "r", "excel", "tableau", "power bi",
        "spark", "aws", "azure", "gcp", "tensorflow", "pytorch",
        "scikit-learn", "docker", "git", "java", "scala",
        "airflow", "dbt", "snowflake", "kafka", "hadoop",
        "mongodb", "postgresql", "linux", "go", "sas", "matlab",
    ]
    selected_skills = st.multiselect(
        "Select Skills",
        options=common_skills,
        default=["python", "sql"],
        key="ml_skills",
    )

    custom_skills = st.text_input(
        "Additional Skills (comma-separated)",
        placeholder="e.g. kubernetes, mlflow, databricks",
        key="ml_custom_skills",
    )

    if custom_skills:
        extra = [s.strip().lower() for s in custom_skills.split(",") if s.strip()]
        all_skills = selected_skills + extra
    else:
        all_skills = selected_skills

    if all_skills:
        chips = "".join(f'<span class="skill-chip">{s}</span>' for s in all_skills)
        st.markdown(f'<div style="margin-top: 8px;">{chips}</div>', unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # ── Benefits & Preferences ──
    st.markdown(
        '<div class="form-section"><div class="form-section-title">Benefits & Preferences</div>',
        unsafe_allow_html=True,
    )

    bc1, bc2 = st.columns(2)
    with bc1:
        work_from_home = st.toggle("Remote / WFH", value=False, key="ml_remote")
    with bc2:
        health_ins = st.toggle("Health Insurance", value=True, key="ml_health")

    st.markdown("</div>", unsafe_allow_html=True)

    # ── Predict Button ──
    predict_clicked = st.button(
        "Predict Salary & Degree Requirement",
        use_container_width=True,
        type="primary",
        key="ml_predict",
    )


# ══════════════════════════════════════════════════════════════
# RIGHT COLUMN — Results
# ══════════════════════════════════════════════════════════════
with col_right:

    if predict_clicked:

        # ── Step 1: Degree classification ──
        degree_result = None
        predicted_no_degree = False

        if degree_online:
            degree_payload = {
                "job_title_short": job_title_short,
                "job_country": job_country,
                "job_schedule_type": schedule_type,
                "company_size": company_size,
                "job_work_from_home": work_from_home,
                "job_health_insurance": health_ins,
                "job_title": job_title,
                "job_skills": all_skills,
            }

            with st.spinner("Classifying degree requirement..."):
                degree_result = predict_degree(degree_payload)

            if degree_result:
                predicted_no_degree = degree_result.get("predicted_no_degree_mention", False)
        else:
            # Degree API offline — default to False
            predicted_no_degree = False

        # ── Step 2: Salary prediction (fed with degree result) ──
        salary_payload = {
            "job_title_short": job_title_short,
            "job_country": job_country,
            "job_schedule_type": schedule_type,
            "company_size": company_size,
            "job_title": job_title,
            "job_skills": all_skills,
            "job_work_from_home": work_from_home,
            "job_no_degree_mention": predicted_no_degree,
            "job_health_insurance": health_ins,
        }

        with st.spinner("Predicting salary..."):
            salary_result = predict_salary(salary_payload)

        if salary_result:
            salary = salary_result.get(
                "predicted_salary_rounded",
                salary_result.get("predicted_salary", 0),
            )
            st.session_state["last_prediction"] = {
                "salary": salary,
                "payload": salary_payload,
                "degree": degree_result,
            }

    # ── Display results or placeholder ──
    pred = st.session_state.get("last_prediction")

    if pred:
        degree_data = pred.get("degree")
        salary = pred["salary"]
        p = pred["payload"]

        # ── Degree card ──
        if degree_data:
            prob = degree_data.get("probability_no_degree_mention", 0)
            prob_pct = degree_data.get("probability_no_degree_mention_percent", 0)
            is_no_degree = degree_data.get("predicted_no_degree_mention", False)
            label = degree_data.get("predicted_label", "unknown")

            if is_no_degree:
                verdict_class = "no-degree"
                verdict_text = "No Degree Required"
                verdict_icon = "&#10003;"
            else:
                verdict_class = "degree-needed"
                verdict_text = "Degree Likely Required"
                verdict_icon = "&#9888;"

            # Choose bar color
            if prob >= 0.65:
                bar_class = "high"
            elif prob >= 0.4:
                bar_class = "mid"
            else:
                bar_class = "low"

            st.markdown(f"""
            <div class="degree-result">
                <div class="degree-label-header">Degree Requirement</div>
                <div class="degree-verdict {verdict_class}">
                    {verdict_icon} {verdict_text}
                </div>
                <div class="prob-bar-wrap">
                    <div class="prob-bar-fill {bar_class}" style="width: {prob_pct}%;"></div>
                </div>
                <div class="degree-prob">
                    {prob_pct:.1f}% probability no degree is needed
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Feed arrow
            st.markdown("""
            <div class="feed-indicator">
                <span class="feed-arrow">&#8595;</span>
                Auto-fed into salary prediction
                <span class="feed-arrow">&#8595;</span>
            </div>
            """, unsafe_allow_html=True)

        elif not degree_online:
            st.markdown("""
            <div class="degree-result" style="opacity:0.5;">
                <div class="degree-label-header">Degree Requirement</div>
                <div style="font-size:0.88rem; color:#94a3b8;">
                    Degree API offline — skipped
                </div>
            </div>
            """, unsafe_allow_html=True)

        # ── Salary card ──
        st.markdown(f"""
        <div class="salary-result">
            <div class="salary-label">Predicted Yearly Salary</div>
            <div class="salary-amount">${salary:,.0f}</div>
            <div class="salary-unit">USD / year</div>
        </div>
        """, unsafe_allow_html=True)

        # ── Prediction details ──
        degree_badge = ""
        if degree_data:
            is_nd = degree_data.get("predicted_no_degree_mention", False)
            degree_badge = (
                '<span style="color:#10B981;">No degree required (auto-detected)</span>'
                if is_nd
                else '<span style="color:#F59E0B;">Degree likely required (auto-detected)</span>'
            )
        else:
            degree_badge = '<span style="color:#94a3b8;">Defaulted to degree required</span>'

        st.markdown(f"""
        <div class="form-section" style="margin-top: 16px;">
            <div class="form-section-title">Prediction Details</div>
            <div style="font-size: 0.82rem; line-height: 2.2; color: #64748b;">
                <div><span style="color: #94a3b8;">Role:</span> <span style="color: #1e293b;">{p["job_title_short"]}</span></div>
                <div><span style="color: #94a3b8;">Title:</span> <span style="color: #1e293b;">{p["job_title"]}</span></div>
                <div><span style="color: #94a3b8;">Country:</span> <span style="color: #1e293b;">{p["job_country"]}</span></div>
                <div><span style="color: #94a3b8;">Schedule:</span> <span style="color: #1e293b;">{p["job_schedule_type"]}</span></div>
                <div><span style="color: #94a3b8;">Company:</span> <span style="color: #1e293b;">{p["company_size"]}</span></div>
                <div><span style="color: #94a3b8;">Remote:</span> <span style="color: #1e293b;">{"Yes" if p["job_work_from_home"] else "No"}</span></div>
                <div><span style="color: #94a3b8;">Degree:</span> {degree_badge}</div>
                <div><span style="color: #94a3b8;">Skills:</span> <span style="color: #1e293b;">{", ".join(p["job_skills"])}</span></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    else:
        # Placeholder
        st.markdown("""
        <div class="degree-result" style="opacity: 0.5;">
            <div class="degree-label-header">Degree Requirement</div>
            <div style="font-size: 1.3rem; font-weight: 800; color: #94a3b8;">—</div>
            <div style="font-size: 0.82rem; color: #94a3b8; margin-top: 6px;">
                Auto-detected when you predict
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="salary-result" style="opacity: 0.5;">
            <div class="salary-label">Predicted Yearly Salary</div>
            <div class="salary-amount" style="background: linear-gradient(135deg, #94a3b8, #cbd5e1);
                 -webkit-background-clip: text; -webkit-text-fill-color: transparent;">—</div>
            <div class="salary-unit">Fill in job details and click Predict</div>
        </div>
        """, unsafe_allow_html=True)
