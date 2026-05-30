import streamlit as st
import requests
import os
from dotenv import load_dotenv
from utils.styles import inject_styles, page_header, section_label, back_to_home
from utils.auth import require_auth, show_sidebar_info, get_role

load_dotenv()

st.set_page_config(page_title="Career Advisor | JobLens", page_icon="◈", layout="wide")
inject_styles()
require_auth()
show_sidebar_info()

back_to_home()

# ── API config ──
NLP_API_URL = os.getenv("NLP_API_URL", "https://arijarfaoui39--recommend.modal.run")
NLP_API_KEY = os.getenv("NLP_API_KEY", "areejazizmelekarijmlnlp54227725")

COMMON_SKILLS = [
    "SQL", "Python", "Excel", "Power BI", "Tableau", "R",
    "AWS", "Azure", "Spark", "Pandas", "NumPy",
    "Machine Learning", "Looker", "Snowflake", "Airflow",
]

COMMON_COUNTRIES = [
    "Europe", "United States", "United Kingdom", "Germany",
    "France", "Canada", "Australia", "India", "Netherlands",
    "Switzerland", "Remote / Anywhere",
]

# ── Page styles ──
st.markdown("""
<style>
    /* ── Form section ── */
    .form-section {
        background: #ffffff;
        border: 1px solid rgba(0,0,0,0.06);
        box-shadow: 0 1px 4px rgba(0,0,0,0.03);
        border-radius: 18px;
        padding: 28px 30px 24px;
        margin-bottom: 30px;
    }
    .form-section-title {
        font-size: 0.68rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 2px;
        color: #6C5CE7;
        margin-bottom: 18px;
    }

    /* ── Result cards ── */
    .result-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 12px;
        margin-top: 16px;
    }
    .result-card {
        background: #ffffff;
        border: 1px solid rgba(0,0,0,0.06);
        box-shadow: 0 1px 3px rgba(0,0,0,0.03);
        border-radius: 14px;
        padding: 16px;
        transition: all 0.3s ease;
    }
    .result-card:hover {
        background: #f8f9ff;
        border-color: rgba(108,92,231,0.15);
    }
    .result-card-label {
        font-size: 0.65rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        color: #94a3b8;
        margin-bottom: 6px;
    }
    .result-card-value {
        font-size: 1rem;
        font-weight: 600;
        color: #1e293b;
    }

    /* ── Score ring ── */
    .score-ring {
        width: 90px; height: 90px;
        border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        margin: 0 auto 12px;
        position: relative;
    }
    .score-ring::before {
        content: '';
        position: absolute; inset: 0;
        border-radius: 50%;
        padding: 4px;
        background: conic-gradient(
            #6C5CE7 calc(var(--score) * 1%),
            #f1f5f9 calc(var(--score) * 1%)
        );
        -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
        -webkit-mask-composite: xor;
        mask-composite: exclude;
    }
    .score-value {
        font-size: 1.5rem; font-weight: 800;
        background: linear-gradient(135deg, #6C5CE7, #0EA5E9);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* ── Skill tags ── */
    .skill-tags { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 8px; }
    .skill-tag {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem; font-weight: 500;
        padding: 4px 12px; border-radius: 8px;
        transition: all 0.2s ease;
    }
    .skill-tag.matched {
        background: rgba(16,185,129,0.1);
        border: 1px solid rgba(16,185,129,0.2);
        color: #10B981;
    }
    .skill-tag.missing {
        background: rgba(244,63,94,0.1);
        border: 1px solid rgba(244,63,94,0.2);
        color: #F43F5E;
    }
    .skill-tag.learn {
        background: rgba(245,158,11,0.1);
        border: 1px solid rgba(245,158,11,0.2);
        color: #F59E0B;
    }
    .skill-tag.required {
        background: rgba(99,102,241,0.1);
        border: 1px solid rgba(99,102,241,0.2);
        color: #818CF8;
    }

    /* ── Job card ── */
    .job-card {
        background: #ffffff;
        border: 1px solid rgba(0,0,0,0.06);
        border-radius: 14px;
        padding: 16px 18px;
        margin-top: 8px;
        transition: all 0.3s ease;
    }
    .job-card:hover {
        background: #f8f9ff;
        transform: translateX(4px);
    }
    .job-card-title { font-size: 0.92rem; font-weight: 700; color: #1e293b; }
    .job-card-meta  { font-size: 0.78rem; color: #64748b; margin-top: 4px; }
    .job-card-salary {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.82rem; font-weight: 600;
        color: #10B981; margin-top: 6px;
    }
    .job-card-skills { display: flex; flex-wrap: wrap; gap: 4px; margin-top: 8px; }

    /* ── Error box ── */
    .api-error {
        background: rgba(244,63,94,0.04);
        border: 1px solid rgba(244,63,94,0.15);
        border-radius: 14px;
        padding: 16px 20px;
        color: #F43F5E;
        font-size: 0.88rem; line-height: 1.5;
    }
    .api-error strong { color: #FB7185; }
    .cold-start-note {
        font-size: 0.78rem; color: #64748b;
        margin-top: 8px; font-style: italic;
    }

    /* ── Response wrapper ── */
    .response-wrapper {
        background: #ffffff;
        border: 1px solid rgba(0,0,0,0.06);
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        border-radius: 18px;
        padding: 28px 30px;
        margin-top: 20px;
        animation: fadeInUp 0.5s cubic-bezier(0.16,1,0.3,1) forwards;
    }
    .response-header {
        display: flex; align-items: center; gap: 12px;
        margin-bottom: 18px;
    }
    .response-avatar {
        width: 36px; height: 36px;
        border-radius: 12px;
        display: flex; align-items: center; justify-content: center;
        font-size: 1rem; font-weight: 700;
        background: linear-gradient(135deg, #6C5CE7, #0EA5E9);
        box-shadow: 0 4px 15px rgba(108,92,231,0.25);
    }
    .response-label {
        font-size: 0.72rem; font-weight: 700;
        text-transform: uppercase; letter-spacing: 1.5px;
        color: #6C5CE7;
    }

    /* ── Summary strip ── */
    .summary-strip {
        display: flex; gap: 8px; flex-wrap: wrap;
        margin-top: 6px;
    }
    .summary-chip {
        font-size: 0.72rem; font-weight: 600;
        padding: 4px 12px; border-radius: 8px;
        background: rgba(108,92,231,0.06);
        border: 1px solid rgba(108,92,231,0.12);
        color: #6C5CE7;
    }
</style>
""", unsafe_allow_html=True)

page_header(
    "💬", "Career Advisor",
    "AI-powered career guidance — describe your profile and get matched with relevant jobs",
)


# ═══════════════════════════════════════════════════════════
# SESSION STATE
# ═══════════════════════════════════════════════════════════
if "nlp_result" not in st.session_state:
    st.session_state.nlp_result = None
if "nlp_profile_text" not in st.session_state:
    st.session_state.nlp_profile_text = ""


# ═══════════════════════════════════════════════════════════
# MAIN FORM — skills, countries, options
# ═══════════════════════════════════════════════════════════
st.markdown('<div class="form-section-title">Build your profile</div>', unsafe_allow_html=True)

# ── Skills ──
section_label("YOUR SKILLS")
st.caption("Select from common skills and/or type your own")
selected_skills = st.multiselect(
    "Skills",
    options=COMMON_SKILLS,
    default=[],
    placeholder="Click to select skills...",
    label_visibility="collapsed",
)
custom_skills_input = st.text_input(
    "Or type additional skills (comma-separated)",
    placeholder="e.g. dbt, kafka, docker, scikit-learn",
    label_visibility="visible",
)

st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

# ── Location & Experience row ──
col_loc, col_exp = st.columns(2)

with col_loc:
    section_label("PREFERRED LOCATION")
    st.caption("Select a country or type your own")
    country_options = ["not specified"] + COMMON_COUNTRIES
    chosen_country = st.selectbox(
        "Country", country_options,
        label_visibility="collapsed",
    )
    custom_country = st.text_input(
        "Or type a custom location",
        placeholder="e.g. Switzerland, Middle East",
        label_visibility="visible",
    )

with col_exp:
    section_label("EXPERIENCE & ROLE")
    experience_level = st.selectbox(
        "Experience Level",
        ["not specified", "junior", "mid-level", "senior"],
    )
    target_role = st.text_input(
        "Target Role",
        placeholder="e.g. Data Analyst, Data Engineer",
    )

# ── Remote, salary, top_k row ──
col_r, col_s, col_k = st.columns(3)
with col_r:
    remote_preference = st.selectbox(
        "Remote Preference",
        ["not specified", "remote", "hybrid", "onsite", "flexible"],
    )
with col_s:
    salary_expectation = st.text_input(
        "Salary Expectation (yearly)",
        value="not specified",
        placeholder="e.g. 60000",
    )
with col_k:
    top_k = st.slider("Job results", min_value=3, max_value=8, value=5)

st.markdown("---")

# ── Profile text + submit ──
section_label("DESCRIBE YOUR PROFILE")
profile_text = st.text_area(
    "Profile",
    placeholder="Tell us about yourself, e.g.: I'm a junior data analyst with 1 year of experience in SQL and Excel. I'm looking for remote Data Analyst roles in Europe.",
    height=100,
    label_visibility="collapsed",
)

# ── Quick prompt chips ──
st.caption("Or pick a quick example:")
qc1, qc2 = st.columns(2)
with qc1:
    if st.button("🎯  Junior analyst, SQL + Excel, remote Europe", use_container_width=True, key="qp1"):
        st.session_state["_quick"] = "I'm a junior data analyst with SQL and Excel, looking for remote roles in Europe"
        st.rerun()
    if st.button("📊  Power BI + Tableau, aspiring data scientist", use_container_width=True, key="qp3"):
        st.session_state["_quick"] = "I know Power BI and Tableau, interested in becoming a data scientist"
        st.rerun()
with qc2:
    if st.button("🚀  Senior Python dev, transition to data eng", use_container_width=True, key="qp2"):
        st.session_state["_quick"] = "Senior Python developer with 5 years experience, want to transition to data engineering"
        st.rerun()
    if st.button("🤖  ML engineer, TensorFlow + PyTorch, senior", use_container_width=True, key="qp4"):
        st.session_state["_quick"] = "ML engineer with TensorFlow and PyTorch, looking for senior roles with high salary"
        st.rerun()

# Resolve final profile text
quick_prompt = st.session_state.pop("_quick", None)
final_profile = profile_text or quick_prompt or ""

# ── Submit button ──
st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
submit_clicked = st.button(
    "Get Recommendations",
    type="primary",
    use_container_width=True,
    disabled=(not final_profile),
)


# ═══════════════════════════════════════════════════════════
# API CALL
# ═══════════════════════════════════════════════════════════
def call_recommendation_api(profile: str) -> dict:
    """Call the Modal-hosted NLP recommendation API."""

    # Merge selected + custom skills
    all_skills = [s.lower() for s in selected_skills]
    if custom_skills_input:
        extras = [s.strip().lower() for s in custom_skills_input.split(",") if s.strip()]
        all_skills.extend(extras)

    # Resolve location: custom text overrides dropdown
    location = custom_country.strip() if custom_country.strip() else chosen_country

    payload = {
        "profile": profile,
        "experience_level": experience_level,
        "target_role": target_role if target_role else "not specified",
        "skills": all_skills,
        "preferred_location": location,
        "remote_preference": remote_preference,
        "salary_expectation": salary_expectation if salary_expectation else "not specified",
        "top_k": top_k,
    }

    headers = {"Content-Type": "application/json"}
    if NLP_API_KEY and NLP_API_KEY != "PASTE_YOUR_API_KEY_HERE":
        headers["x-api-key"] = NLP_API_KEY

    try:
        resp = requests.post(NLP_API_URL, json=payload, headers=headers, timeout=120)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.Timeout:
        return {
            "error": "Request timed out. The GPU container may be cold-starting. "
                     "Please wait ~30 seconds and try again."
        }
    except requests.exceptions.ConnectionError:
        return {
            "error": "Cannot connect to the recommendation API. "
                     "Make sure the backend is running (modal serve)."
        }
    except requests.exceptions.HTTPError:
        detail = ""
        try:
            detail = resp.json().get("detail", resp.text[:300])
        except Exception:
            detail = resp.text[:300]
        return {"error": f"API returned {resp.status_code}: {detail}"}
    except Exception as e:
        return {"error": str(e)}


# ═══════════════════════════════════════════════════════════
# RESPONSE TRANSFORMER
# ═══════════════════════════════════════════════════════════
def transform_api_response(raw: dict) -> dict:
    """Convert raw API JSON into the dict our render function expects."""
    if "error" in raw:
        return raw

    rec = raw.get("recommendation", {})
    jobs_raw = raw.get("retrieved_jobs", [])

    jobs = []
    for j in jobs_raw:
        salary = j.get("salary_year_avg", "not specified")
        if salary and salary != "not specified":
            try:
                salary = f"${float(salary):,.0f}/yr"
            except (ValueError, TypeError):
                salary = str(salary)
        else:
            salary = "Not specified"

        loc_parts = []
        if j.get("location"):
            loc_parts.append(j["location"])
        elif j.get("country"):
            loc_parts.append(j["country"])
        remote_flag = j.get("remote", "")
        if remote_flag and remote_flag.lower() not in ("not remote", ""):
            loc_parts.append(f"({remote_flag})")

        jobs.append({
            "title": j.get("job_title", j.get("job_title_short", "Unknown")),
            "company": j.get("company_name", "Unknown"),
            "location": " ".join(loc_parts) if loc_parts else "Not specified",
            "salary": salary,
            "required_skills": j.get("required_skills", []),
        })

    roles = rec.get("recommended_roles", [])

    return {
        "score": rec.get("match_score", 0),
        "recommended_role": ", ".join(roles) if roles else "Not specified",
        "matched_skills": rec.get("matched_skills", []),
        "missing_skills": rec.get("missing_skills", []),
        "learning": rec.get("learning_recommendations", []),
        "jobs": jobs,
        "explanation": rec.get("explanation", ""),
    }


# ═══════════════════════════════════════════════════════════
# RENDER
# ═══════════════════════════════════════════════════════════
def render_result(data: dict):
    """Render API result with Streamlit + HTML cards."""

    if "error" in data:
        st.markdown(f"""
        <div class="api-error">
            <strong>Something went wrong</strong><br>
            {data["error"]}
        </div>
        <div class="cold-start-note">
            Tip: the first request may be slow because the GPU container needs to start up.
            Try again in 30-60 seconds.
        </div>
        """, unsafe_allow_html=True)
        return

    # ── Explanation ──
    st.markdown(f"""
    <div class="response-wrapper">
        <div class="response-header">
            <div class="response-avatar">AI</div>
            <div class="response-label">Recommendation</div>
        </div>
        <div style="color:#1e293b; font-size:0.92rem; line-height:1.65; margin-bottom:4px;">
            {data["explanation"]}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Score + Role row ──
    matched_tags = "".join(
        f'<span class="skill-tag matched">{s}</span>' for s in data["matched_skills"]
    )
    missing_tags = "".join(
        f'<span class="skill-tag missing">{s}</span>' for s in data["missing_skills"]
    )
    learn_tags = "".join(
        f'<span class="skill-tag learn">{tip}</span>' for tip in data["learning"]
    )

    st.markdown(f"""
    <div class="result-grid">
        <div class="result-card" style="text-align:center;">
            <div class="score-ring" style="--score: {data['score']};">
                <span class="score-value">{data['score']}</span>
            </div>
            <div class="result-card-label" style="text-align:center;">Match Score</div>
        </div>
        <div class="result-card">
            <div class="result-card-label">Recommended Roles</div>
            <div class="result-card-value">{data['recommended_role']}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Skills sections ──
    st.markdown(f"""
    <div style="margin-top:18px;">
        <div class="result-card-label">Matched Skills</div>
        <div class="skill-tags">{matched_tags or '<span style="color:#94a3b8;font-size:0.82rem;">None detected</span>'}</div>
    </div>
    <div style="margin-top:14px;">
        <div class="result-card-label">Skills to Develop</div>
        <div class="skill-tags">{missing_tags or '<span style="color:#94a3b8;font-size:0.82rem;">None</span>'}</div>
    </div>
    <div style="margin-top:14px;">
        <div class="result-card-label">Learning Path</div>
        <div class="skill-tags">{learn_tags or '<span style="color:#94a3b8;font-size:0.82rem;">No suggestions</span>'}</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Job cards ──
    if data["jobs"]:
        st.markdown(
            '<div style="margin-top:20px;"><div class="result-card-label">Matching Job Postings</div></div>',
            unsafe_allow_html=True,
        )
        for job in data["jobs"]:
            req_skills = ""
            if job.get("required_skills"):
                pills = "".join(
                    f'<span class="skill-tag required">{sk}</span>'
                    for sk in job["required_skills"][:8]
                )
                req_skills = f'<div class="job-card-skills">{pills}</div>'

            st.markdown(f"""
            <div class="job-card">
                <div class="job-card-title">{job["title"]}</div>
                <div class="job-card-meta">{job["company"]} &middot; {job["location"]}</div>
                <div class="job-card-salary">{job["salary"]}</div>
                {req_skills}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown(
            '<div style="color:#94a3b8;font-size:0.82rem;margin-top:18px;">No matching jobs found</div>',
            unsafe_allow_html=True,
        )


# ═══════════════════════════════════════════════════════════
# HANDLE SUBMIT
# ═══════════════════════════════════════════════════════════
if submit_clicked and final_profile:
    if not NLP_API_KEY or NLP_API_KEY == "PASTE_YOUR_API_KEY_HERE":
        st.error("Set your **NLP_API_KEY** in the `.env` file first. Ask the backend owner for the key.")
    else:
        # Build summary of what was sent
        all_sk = [s for s in selected_skills]
        if custom_skills_input:
            all_sk += [s.strip() for s in custom_skills_input.split(",") if s.strip()]
        loc = custom_country.strip() if custom_country.strip() else chosen_country

        summary_parts = []
        if all_sk:
            summary_parts.append(f"Skills: {', '.join(all_sk)}")
        if loc and loc != "not specified":
            summary_parts.append(f"Location: {loc}")
        if experience_level != "not specified":
            summary_parts.append(f"Level: {experience_level}")
        if target_role:
            summary_parts.append(f"Role: {target_role}")
        if remote_preference != "not specified":
            summary_parts.append(f"Remote: {remote_preference}")

        with st.spinner("Analyzing your profile... (first request may take ~30s for GPU cold start)"):
            raw = call_recommendation_api(final_profile)
            result = transform_api_response(raw)
            st.session_state.nlp_result = result
            st.session_state.nlp_profile_text = final_profile
            st.session_state.nlp_summary = summary_parts
        st.rerun()


# ═══════════════════════════════════════════════════════════
# DISPLAY RESULTS (persisted in session_state)
# ═══════════════════════════════════════════════════════════
if st.session_state.nlp_result is not None:
    st.markdown("---")

    # Show what was sent
    summary = st.session_state.get("nlp_summary", [])
    profile_sent = st.session_state.get("nlp_profile_text", "")

    if summary:
        chips = "".join(f'<span class="summary-chip">{s}</span>' for s in summary)
        st.markdown(f"""
        <div style="margin-bottom:6px;">
            <div class="result-card-label">Your Query</div>
            <div style="color:#1e293b;font-size:0.88rem;margin:6px 0 10px;">{profile_sent}</div>
            <div class="summary-strip">{chips}</div>
        </div>
        """, unsafe_allow_html=True)

    render_result(st.session_state.nlp_result)

    # Reset button
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    if st.button("Clear Results & Try Again", use_container_width=True):
        st.session_state.nlp_result = None
        st.session_state.nlp_profile_text = ""
        st.session_state.nlp_summary = []
        st.rerun()
