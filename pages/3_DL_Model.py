import os
import streamlit as st
import requests
import plotly.graph_objects as go
from dotenv import load_dotenv
from utils.styles import inject_styles, page_header, section_label, back_to_home, show_loading, PLOTLY_LAYOUT, COLORS
from utils.auth import require_auth, show_sidebar_info

load_dotenv()

st.set_page_config(page_title="Market Forecasting | JobLens", page_icon="◈", layout="wide")
inject_styles()
require_auth()
show_sidebar_info()

back_to_home()
page_header("forecast", "Market Forecasting",
            "6-month job demand forecast powered by LSTM / GRU / BiLSTM ensembles")

# ── Page-specific styles ──
st.markdown("""
<style>
    /* KPI row */
    .kpi-row { display: flex; gap: 12px; margin-bottom: 24px; }
    .kpi-item {
        flex: 1;
        background: #1a1a2e;
        border: 1px solid rgba(255,255,255,0.07);
        box-shadow: 0 1px 4px rgba(0,0,0,0.03);
        border-radius: 16px;
        padding: 20px 18px;
        text-align: center;
        animation: fadeInUp 0.6s cubic-bezier(0.16,1,0.3,1) forwards;
        opacity: 0;
    }
    .kpi-item:nth-child(1) { animation-delay: 0.05s; }
    .kpi-item:nth-child(2) { animation-delay: 0.10s; }
    .kpi-item:nth-child(3) { animation-delay: 0.15s; }
    .kpi-item:nth-child(4) { animation-delay: 0.20s; }
    .kpi-item:nth-child(5) { animation-delay: 0.25s; }
    .kpi-num {
        font-size: 1.8rem;
        font-weight: 800;
        letter-spacing: -1px;
        line-height: 1.1;
    }
    .kpi-num.grad-green {
        background: linear-gradient(135deg, #10B981, #0EA5E9);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .kpi-num.grad-red {
        background: linear-gradient(135deg, #F43F5E, #F59E0B);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .kpi-num.grad-purple {
        background: linear-gradient(135deg, #6C5CE7, #0EA5E9);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .kpi-desc {
        font-size: 0.68rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        color: #cbd5e1;
        margin-top: 6px;
    }

    /* sector grid */
    .sector-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(170px, 1fr));
        gap: 10px;
        margin: 16px 0 24px;
    }
    .sector-chip {
        background: #1a1a2e;
        border: 1px solid rgba(255,255,255,0.07);
        box-shadow: 0 1px 3px rgba(0,0,0,0.03);
        border-radius: 12px;
        padding: 14px 16px;
        cursor: default;
        transition: all 0.3s ease;
        animation: fadeInScale 0.5s cubic-bezier(0.16,1,0.3,1) forwards;
        opacity: 0;
    }
    .sector-chip:hover {
        background: #1e1e35;
        border-color: rgba(108,92,231,0.2);
        transform: translateY(-2px);
    }
    .sector-chip .name {
        font-size: 0.82rem;
        font-weight: 600;
        color: #e2e8f0;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .sector-chip .change {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.85rem;
        font-weight: 700;
        margin-top: 4px;
    }
    .sector-chip .change.up   { color: #10B981; }
    .sector-chip .change.down { color: #F43F5E; }
    .sector-chip .idx {
        font-size: 0.7rem;
        color: #cbd5e1;
        margin-top: 2px;
    }

    /* detail panel */
    .form-section {
        background: #1a1a2e;
        border: 1px solid rgba(255,255,255,0.07);
        box-shadow: 0 1px 4px rgba(0,0,0,0.03);
        border-radius: 20px;
        padding: 28px;
        margin-bottom: 20px;
    }
    .form-section-title {
        font-size: 0.68rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 2px;
        color: #6C5CE7;
        margin-bottom: 18px;
    }
    .detail-row {
        display: flex; justify-content: space-between;
        padding: 10px 0;
        border-bottom: 1px solid rgba(0,0,0,0.04);
        font-size: 0.85rem;
    }
    .detail-key { color: #cbd5e1; }
    .detail-val { color: #e2e8f0; font-weight: 600; }
    .mono { font-family: 'JetBrains Mono', monospace; }

    /* projection card */
    .dl-result {
        text-align: center;
        padding: 36px 20px;
        background: #1a1a2e;
        border: 1px solid rgba(255,255,255,0.07);
        box-shadow: 0 4px 16px rgba(0,0,0,0.04);
        border-radius: 24px;
        margin: 10px 0 20px;
        animation: fadeInScale 0.6s cubic-bezier(0.16,1,0.3,1) forwards;
    }
    .dl-label {
        font-size: 0.7rem; font-weight: 700;
        text-transform: uppercase; letter-spacing: 2.5px; color: #cbd5e1;
        margin-bottom: 12px;
    }
    .dl-value {
        font-size: 3rem; font-weight: 900; letter-spacing: -2px; line-height: 1.1;
    }
    .dl-value.up {
        background: linear-gradient(135deg,#10B981,#0EA5E9);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .dl-value.down {
        background: linear-gradient(135deg,#F43F5E,#F59E0B);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .dl-sub { font-size: 0.92rem; color: #cbd5e1; margin-top: 8px; font-weight: 500; }


</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# API HELPERS
# ══════════════════════════════════════════════════════════════

API_URL = os.getenv("API_URL", "http://localhost:10000")


@st.cache_data(ttl=300)
def fetch_dl_metadata():
    try:
        resp = requests.get(f"{API_URL}/forecast/metadata", timeout=10)
        resp.raise_for_status()
        return resp.json(), True
    except Exception:
        return None, False


@st.cache_data(ttl=120)
def fetch_forecast(region: str, sector: str) -> dict | None:
    try:
        resp = requests.post(
            f"{API_URL}/forecast/forecast",
            json={"region": region, "sector": sector},
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()
    except Exception:
        return None


def fetch_all_sectors(region: str, sectors: list[str]) -> list[dict]:
    """Fetch forecasts for all sectors (for overview grid)."""
    results = []
    for s in sectors:
        d = fetch_forecast(region, s)
        if d:
            results.append(d)
    return results


# ══════════════════════════════════════════════════════════════
# BUILD CHART HELPERS
# ══════════════════════════════════════════════════════════════

def build_trajectory_chart(data: dict, title_extra: str = ""):
    """Build the main Plotly forecast chart from API response."""
    hist_dates = data.get("historical_dates", [])
    hist_values = data.get("historical_values", [])
    fc_dates = data.get("forecast_dates", [])
    fc_values = data.get("forecast_values", [])
    fc_low = data.get("forecast_low", [])
    fc_high = data.get("forecast_high", [])

    if not hist_dates or not fc_dates:
        return None

    fig = go.Figure()

    # Historical line
    fig.add_trace(go.Scatter(
        x=hist_dates, y=hist_values,
        mode="lines", name="Historical",
        line=dict(color="#6C5CE7", width=2.5),
        hovertemplate="%{x}<br>Index: <b>%{y:.1f}</b><extra></extra>",
    ))

    # Bridge hist → forecast
    bridge_x = [hist_dates[-1]] + fc_dates
    bridge_y = [hist_values[-1]] + fc_values
    bridge_low = [hist_values[-1]] + fc_low
    bridge_high = [hist_values[-1]] + fc_high

    # Forecast line
    fig.add_trace(go.Scatter(
        x=bridge_x, y=bridge_y,
        mode="lines+markers", name="Forecast",
        line=dict(color="#0EA5E9", width=2.5, dash="dash"),
        marker=dict(size=8, symbol="diamond"),
        hovertemplate="%{x}<br>Forecast: <b>%{y:.1f}</b><extra></extra>",
    ))

    # Confidence band
    pct = data.get("change_pct", 0)
    band_color = "rgba(16,185,129,0.12)" if pct >= 0 else "rgba(244,63,94,0.12)"
    fig.add_trace(go.Scatter(
        x=bridge_x + bridge_x[::-1],
        y=bridge_high + bridge_low[::-1],
        fill="toself", fillcolor=band_color,
        line=dict(width=0), showlegend=True,
        name="80% Confidence", hoverinfo="skip",
    ))

    # Baseline & divider
    fig.add_hline(y=100, line_dash="dot", line_color="rgba(0,0,0,0.08)",
                  annotation_text="Pre-COVID baseline (100)",
                  annotation_font_color="#cbd5e1", annotation_font_size=11)
    fig.add_vline(x=hist_dates[-1], line_dash="dash", line_color="rgba(0,0,0,0.06)")
    fig.add_annotation(
        x=hist_dates[-1], y=max(hist_values + fc_values) + 5,
        text="Forecast →", showarrow=False, font=dict(size=11, color="#0EA5E9"),
    )

    layout = {**PLOTLY_LAYOUT}
    region = data.get("region", "")
    sector = data.get("sector", "")
    chart_title = f"{sector} — {region}" + (f" {title_extra}" if title_extra else "")
    layout.update(
        height=460,
        title=dict(text=chart_title, font=dict(size=13, color="#1e293b")),
        xaxis=dict(title="", gridcolor="rgba(0,0,0,0.05)",
                   rangeslider=dict(visible=True, thickness=0.04)),
        yaxis=dict(title="Job Postings Index", gridcolor="rgba(0,0,0,0.05)"),
        legend=dict(orientation="h", y=-0.22, x=0.5, xanchor="center"),
    )
    fig.update_layout(**layout)
    return fig


def build_comparison_chart(datasets: list[dict], label_key: str = "sector"):
    """Overlay multiple forecast lines for sector or region comparison."""
    fig = go.Figure()

    for i, data in enumerate(datasets):
        color = COLORS[i % len(COLORS)]
        label = data.get(label_key, f"Series {i+1}")
        hist_dates = data.get("historical_dates", [])
        hist_values = data.get("historical_values", [])
        fc_dates = data.get("forecast_dates", [])
        fc_values = data.get("forecast_values", [])

        if not hist_dates:
            continue

        # Historical
        fig.add_trace(go.Scatter(
            x=hist_dates, y=hist_values,
            mode="lines", name=f"{label}",
            line=dict(color=color, width=2),
            legendgroup=label,
            hovertemplate=f"{label}<br>%{{x}}: <b>%{{y:.1f}}</b><extra></extra>",
        ))

        # Forecast
        if fc_dates:
            bridge_x = [hist_dates[-1]] + fc_dates
            bridge_y = [hist_values[-1]] + fc_values
            fig.add_trace(go.Scatter(
                x=bridge_x, y=bridge_y,
                mode="lines+markers", name=f"{label} (forecast)",
                line=dict(color=color, width=2, dash="dash"),
                marker=dict(size=6, symbol="diamond"),
                legendgroup=label, showlegend=False,
                hovertemplate=f"{label} forecast<br>%{{x}}: <b>%{{y:.1f}}</b><extra></extra>",
            ))

    if not fig.data:
        return None

    # Baseline
    fig.add_hline(y=100, line_dash="dot", line_color="rgba(0,0,0,0.08)",
                  annotation_text="Baseline (100)",
                  annotation_font_color="#cbd5e1", annotation_font_size=11)

    layout = {**PLOTLY_LAYOUT}
    layout.update(
        height=500,
        title=dict(text="Comparison — Historical + 6-Month Forecast",
                   font=dict(size=13, color="#1e293b")),
        xaxis=dict(title="", gridcolor="rgba(0,0,0,0.05)",
                   rangeslider=dict(visible=True, thickness=0.04)),
        yaxis=dict(title="Job Postings Index", gridcolor="rgba(0,0,0,0.05)"),
        legend=dict(orientation="h", y=-0.22, x=0.5, xanchor="center"),
    )
    fig.update_layout(**layout)
    return fig


# ══════════════════════════════════════════════════════════════
# CHECK API
# ══════════════════════════════════════════════════════════════

metadata, api_online = fetch_dl_metadata()

if api_online:
    regions = metadata.get("regions", [])
    sectors = metadata.get("sectors", [])
    model_info = metadata.get("model", {})
    data_range = metadata.get("data_range", {})
else:
    st.error("Forecast service is currently unavailable. Please try again later.")
    regions = ["Global", "US", "AU", "CA", "DE", "FR", "GB"]
    sectors = ["Software Development", "Data & Analytics", "Accounting",
               "Marketing", "Management", "Banking & Finance"]
    model_info = {}
    data_range = {}


# ══════════════════════════════════════════════════════════════
# TABS: Forecast / Compare Sectors / Compare Regions
# ══════════════════════════════════════════════════════════════

tab_forecast, tab_sectors, tab_regions, tab_pipeline = st.tabs([
    "📈  Single Forecast",
    "🔀  Compare Sectors",
    "🌍  Compare Regions",
    "⚙️  Model Pipeline",
])


# ──────────────────────────────────────────────────
# TAB 1 — SINGLE FORECAST  (auto-updates on change)
# ──────────────────────────────────────────────────
with tab_forecast:

    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.markdown('<div class="form-section"><div class="form-section-title">Select Region & Sector</div>',
                    unsafe_allow_html=True)
        fc1, fc2 = st.columns(2)
        with fc1:
            selected_region = st.selectbox(
                "Region / Country", options=regions, index=0,
                key="dl_region", help="Global = average across all countries",
            )
        with fc2:
            selected_sector = st.selectbox(
                "Sector", options=sectors, index=0, key="dl_sector",
            )
        st.markdown('</div>', unsafe_allow_html=True)

        # Generate button
        forecast_clicked = st.button(
            "Generate Forecast", use_container_width=True,
            type="primary", key="dl_forecast_btn",
        )

    # Fetch on button click, persist in session state
    if forecast_clicked and api_online:
        show_loading("Running forecast model", 3.0)
        result = fetch_forecast(selected_region, selected_sector)
        if result:
            st.session_state["dl_result"] = result

    data = st.session_state.get("dl_result")

    with col_right:
        if data:
            current = data.get("current_value", 0)
            projected = data.get("projected_value", 0)
            pct = data.get("change_pct", 0)
            direction = "up" if pct >= 0 else "down"
            arrow = "▲" if pct >= 0 else "▼"

            st.markdown(f"""
            <div class="dl-result">
                <div class="dl-label">6-Month Projection</div>
                <div class="dl-value {direction}">{arrow} {pct:+.1f}%</div>
                <div class="dl-sub">{selected_sector} · {selected_region}</div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div class="form-section" style="margin-top: 16px;">
                <div class="form-section-title">Forecast Details</div>
                <div class="detail-row">
                    <span class="detail-key">Current Index</span>
                    <span class="detail-val mono">{current:.1f}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-key">Projected (6m)</span>
                    <span class="detail-val mono">{projected:.1f}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-key">Change (pts)</span>
                    <span class="detail-val mono">{projected - current:+.1f}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-key">Confidence Band</span>
                    <span class="detail-val mono">{data.get('low_value',0):.1f} — {data.get('high_value',0):.1f}</span>
                </div>
                <div class="detail-row" style="border: none;">
                    <span class="detail-key">Baseline (Feb 2020)</span>
                    <span class="detail-val mono">100.0</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="dl-result" style="opacity: 0.5;">
                <div class="dl-label">6-Month Projection</div>
                <div class="dl-value" style="background: linear-gradient(135deg,#cbd5e1,#cbd5e1);
                     -webkit-background-clip: text; -webkit-text-fill-color: transparent;">—</div>
                <div class="dl-sub">Select region & sector, then click Generate Forecast</div>
            </div>
            """, unsafe_allow_html=True)

    # ── KPI row ──
    if data:
        pct = data.get("change_pct", 0)
        current = data.get("current_value", 0)
        projected = data.get("projected_value", 0)
        grad = "grad-green" if pct >= 0 else "grad-red"
        st.markdown(f"""
        <div class="kpi-row">
            <div class="kpi-item">
                <div class="kpi-num grad-purple">{current:.1f}</div>
                <div class="kpi-desc">Current Index</div>
            </div>
            <div class="kpi-item">
                <div class="kpi-num {grad}">{projected:.1f}</div>
                <div class="kpi-desc">Projected 6m</div>
            </div>
            <div class="kpi-item">
                <div class="kpi-num {grad}">{"▲" if pct >= 0 else "▼"} {abs(pct):.1f}%</div>
                <div class="kpi-desc">Change</div>
            </div>
            <div class="kpi-item">
                <div class="kpi-num grad-purple">{data.get('low_value',0):.1f}</div>
                <div class="kpi-desc">Low Estimate</div>
            </div>
            <div class="kpi-item">
                <div class="kpi-num grad-purple">{data.get('high_value',0):.1f}</div>
                <div class="kpi-desc">High Estimate</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Trajectory chart ──
    if data:
        fig = build_trajectory_chart(data)
        if fig:
            st.plotly_chart(fig, use_container_width=True)

    # ── Sector overview grid ──
    if api_online and data:
        section_label("Sector Overview — " + selected_region)

        overview_clicked = st.button(
            "Load All Sectors Overview", use_container_width=True,
            key="dl_overview_btn",
        )

        if overview_clicked:
            show_loading("Loading all sectors", 3.0)
            st.session_state["dl_overview"] = fetch_all_sectors(selected_region, sectors)

        all_data = st.session_state.get("dl_overview")
        if all_data:
            # Sort by change %
            all_data.sort(key=lambda d: d.get("change_pct", 0), reverse=True)
            chips_html = ""
            for i, sd in enumerate(all_data):
                s_name = sd.get("sector", "")
                s_pct = sd.get("change_pct", 0)
                s_cur = sd.get("current_value", 0)
                direction = "up" if s_pct >= 0 else "down"
                arrow = "▲" if s_pct >= 0 else "▼"
                delay = f"animation-delay: {i * 0.04}s;"
                highlight = "border-color: rgba(108,92,231,0.4);" if s_name == selected_sector else ""
                chips_html += f"""
                <div class="sector-chip" style="{delay} {highlight}">
                    <div class="name">{s_name}</div>
                    <div class="change {direction}">{arrow} {s_pct:+.1f}%</div>
                    <div class="idx">Index: {s_cur:.0f}</div>
                </div>"""
            st.markdown(f'<div class="sector-grid">{chips_html}</div>', unsafe_allow_html=True)


# ──────────────────────────────────────────────────
# TAB 2 — COMPARE SECTORS
# ──────────────────────────────────────────────────
with tab_sectors:

    st.markdown('<div class="form-section"><div class="form-section-title">Compare Multiple Sectors</div>',
                unsafe_allow_html=True)

    cmp_region = st.selectbox(
        "Region", options=regions, index=0, key="cmp_sec_region",
    )
    cmp_sectors = st.multiselect(
        "Select Sectors to Compare (2–5)",
        options=sectors, default=sectors[:3] if len(sectors) >= 3 else sectors[:2],
        key="cmp_sectors",
    )
    st.markdown('</div>', unsafe_allow_html=True)

    cmp_sec_clicked = st.button(
        "Compare Sectors", use_container_width=True,
        type="primary", key="cmp_sec_btn",
    )

    if cmp_sec_clicked and api_online and len(cmp_sectors) >= 2:
        show_loading("Comparing sectors", 3.0)
        datasets = []
        for s in cmp_sectors[:5]:
            d = fetch_forecast(cmp_region, s)
            if d:
                datasets.append(d)
        if datasets:
            st.session_state["cmp_sec_result"] = datasets

    datasets = st.session_state.get("cmp_sec_result")

    if datasets and len(cmp_sectors) >= 2:
            # KPI comparison table
            st.markdown(f"""
            <div class="form-section">
                <div class="form-section-title">Comparison — {cmp_region}</div>
            """, unsafe_allow_html=True)
            for i, d in enumerate(datasets):
                pct = d.get("change_pct", 0)
                arrow = "▲" if pct >= 0 else "▼"
                color = "#10B981" if pct >= 0 else "#F43F5E"
                dot_color = COLORS[i % len(COLORS)]
                st.markdown(f"""
                <div class="detail-row">
                    <span class="detail-key">
                        <span style="display:inline-block;width:10px;height:10px;border-radius:50%;
                                     background:{dot_color};margin-right:8px;"></span>
                        {d.get("sector","")}
                    </span>
                    <span class="detail-val mono" style="color:{color};">
                        {d.get("current_value",0):.1f} → {d.get("projected_value",0):.1f}
                        &nbsp; {arrow} {pct:+.1f}%
                    </span>
                </div>
                """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            # Chart
            fig = build_comparison_chart(datasets, label_key="sector")
            if fig:
                fig.update_layout(title=dict(
                    text=f"Sector Comparison — {cmp_region}",
                    font=dict(size=13, color="#1e293b"),
                ))
                st.plotly_chart(fig, use_container_width=True)
    if not datasets and len(cmp_sectors) < 2:
        st.info("Select at least 2 sectors to compare.")
    elif not datasets:
        st.info("Click **Compare Sectors** to generate the comparison.")


# ──────────────────────────────────────────────────
# TAB 3 — COMPARE REGIONS
# ──────────────────────────────────────────────────
with tab_regions:

    st.markdown('<div class="form-section"><div class="form-section-title">Compare Regions for a Sector</div>',
                unsafe_allow_html=True)

    cmp_sector = st.selectbox(
        "Sector", options=sectors, index=0, key="cmp_reg_sector",
    )
    cmp_regions = st.multiselect(
        "Select Regions to Compare (2–5)",
        options=regions, default=["Global", "US", "GB"] if len(regions) >= 3 else regions[:2],
        key="cmp_regions",
    )
    st.markdown('</div>', unsafe_allow_html=True)

    cmp_reg_clicked = st.button(
        "Compare Regions", use_container_width=True,
        type="primary", key="cmp_reg_btn",
    )

    if cmp_reg_clicked and api_online and len(cmp_regions) >= 2:
        show_loading("Comparing regions", 3.0)
        datasets = []
        for r in cmp_regions[:5]:
            d = fetch_forecast(r, cmp_sector)
            if d:
                datasets.append(d)
        if datasets:
            st.session_state["cmp_reg_result"] = datasets

    datasets = st.session_state.get("cmp_reg_result")

    if datasets and len(cmp_regions) >= 2:
            # KPI comparison
            st.markdown(f"""
            <div class="form-section">
                <div class="form-section-title">Comparison — {cmp_sector}</div>
            """, unsafe_allow_html=True)
            for i, d in enumerate(datasets):
                pct = d.get("change_pct", 0)
                arrow = "▲" if pct >= 0 else "▼"
                color = "#10B981" if pct >= 0 else "#F43F5E"
                dot_color = COLORS[i % len(COLORS)]
                st.markdown(f"""
                <div class="detail-row">
                    <span class="detail-key">
                        <span style="display:inline-block;width:10px;height:10px;border-radius:50%;
                                     background:{dot_color};margin-right:8px;"></span>
                        {d.get("region","")}
                    </span>
                    <span class="detail-val mono" style="color:{color};">
                        {d.get("current_value",0):.1f} → {d.get("projected_value",0):.1f}
                        &nbsp; {arrow} {pct:+.1f}%
                    </span>
                </div>
                """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            # Chart
            fig = build_comparison_chart(datasets, label_key="region")
            if fig:
                fig.update_layout(title=dict(
                    text=f"Regional Comparison — {cmp_sector}",
                    font=dict(size=13, color="#1e293b"),
                ))
                st.plotly_chart(fig, use_container_width=True)
    if not datasets and len(cmp_regions) < 2:
        st.info("Select at least 2 regions to compare.")
    elif not datasets:
        st.info("Click **Compare Regions** to generate the comparison.")


# ──────────────────────────────────────────────────
# TAB 4 — MODEL PIPELINE
# ──────────────────────────────────────────────────
with tab_pipeline:

    # Model info card
    if model_info:
        best = model_info.get("best_architecture", "GRU").upper()
        rmse = model_info.get("rmse", "—")
        r2 = model_info.get("r2", "—")
        mae = model_info.get("mae", "—")
        start = data_range.get("start", "—") if data_range else "—"
        end = data_range.get("end", "—") if data_range else "—"
        months = data_range.get("months", "—") if data_range else "—"

        st.markdown(f"""
        <div class="kpi-row">
            <div class="kpi-item">
                <div class="kpi-num grad-purple">{best}</div>
                <div class="kpi-desc">Best Architecture</div>
            </div>
            <div class="kpi-item">
                <div class="kpi-num grad-green">{rmse}</div>
                <div class="kpi-desc">Test RMSE</div>
            </div>
            <div class="kpi-item">
                <div class="kpi-num grad-green">{mae}</div>
                <div class="kpi-desc">Test MAE</div>
            </div>
            <div class="kpi-item">
                <div class="kpi-num grad-purple">{r2}</div>
                <div class="kpi-desc">Test R²</div>
            </div>
            <div class="kpi-item">
                <div class="kpi-num grad-purple">{months}</div>
                <div class="kpi-desc">Months of Data</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    section_label("End-to-End Pipeline")

    steps = [
        ("1", "Data Ingestion",
         "Indeed Job Postings Index from 6 countries (US, AU, CA, DE, FR, GB), Feb 2020 onwards",
         ["pandas", "CSV loader"]),
        ("2", "Aggregation",
         "Monthly global/regional index per sector, filtered to total postings",
         ["groupby", "cross-country mean"]),
        ("3", "STL Denoising",
         "Seasonal-Trend decomposition, discard residual noise for cleaner signal",
         ["STL", "robust=True", "period=12"]),
        ("4", "Feature Engineering",
         "First differencing, cyclical month encoding, rolling volatility, COVID flag",
         ["np.diff", "sin/cos", "MinMaxScaler"]),
        ("5", "Training",
         "7-seed ensemble per architecture, Huber loss, L2 + dropout regularization",
         ["LSTM", "GRU", "BiLSTM", "EarlyStopping"]),
        ("6", "Forecasting",
         "Recursive 6-month forecast with 10th–90th percentile ensemble uncertainty",
         ["recursive predict", "bias correction"]),
    ]

    for num, title, desc, techs in steps:
        tags = "".join(
            f"""<span style="font-family: 'JetBrains Mono', monospace; font-size: 0.68rem;
                padding: 3px 10px; border-radius: 6px; background: rgba(108,92,231,0.08);
                border: 1px solid rgba(108,92,231,0.15); color: #6C5CE7;
                margin-right: 4px;">{t}</span>""" for t in techs
        )
        st.markdown(f"""
        <div style="display: flex; align-items: flex-start; gap: 16px; padding: 14px 0;
                    border-bottom: 1px solid rgba(0,0,0,0.04);">
            <div style="width: 32px; height: 32px; border-radius: 10px;
                        background: linear-gradient(135deg, #6C5CE7, #0EA5E9);
                        display: flex; align-items: center; justify-content: center;
                        font-weight: 800; font-size: 0.8rem; color: white; flex-shrink: 0;">{num}</div>
            <div>
                <div style="font-size: 0.95rem; font-weight: 700; color: #1e293b;
                            margin-bottom: 4px;">{title}</div>
                <div style="font-size: 0.82rem; color: #cbd5e1; line-height: 1.5;
                            margin-bottom: 6px;">{desc}</div>
                <div>{tags}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Architecture comparison
    section_label("Architecture Comparison")

    arch_data = [
        ("LSTM", "Long Short-Term Memory", "Gated memory cells for long-range dependencies"),
        ("GRU", "Gated Recurrent Unit", "Simplified gating, faster training, often comparable accuracy"),
        ("BiLSTM", "Bidirectional LSTM", "Forward + backward passes capture context from both directions"),
    ]

    cols = st.columns(3)
    for i, (name, full, desc) in enumerate(arch_data):
        with cols[i]:
            is_best = model_info.get("best_architecture", "").upper() == name
            border = "border-color: rgba(108,92,231,0.4);" if is_best else ""
            badge = '<span style="font-size:0.65rem;background:#6C5CE7;color:white;padding:2px 8px;border-radius:4px;margin-left:8px;">BEST</span>' if is_best else ""
            st.markdown(f"""
            <div class="form-section" style="{border}">
                <div style="font-size: 1.1rem; font-weight: 800; color: #1e293b;">
                    {name}{badge}
                </div>
                <div style="font-size: 0.78rem; color: #6C5CE7; margin: 4px 0 8px; font-weight: 600;">
                    {full}
                </div>
                <div style="font-size: 0.82rem; color: #cbd5e1; line-height: 1.5;">
                    {desc}
                </div>
            </div>
            """, unsafe_allow_html=True)
