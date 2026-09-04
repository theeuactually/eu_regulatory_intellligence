"""Streamlit dashboard for EU legislative act monitoring.

This dashboard provides:
- Live data fetching (with caching)
- Health gauge
- Metric grid (total milestones, mean gaps, urgency)
- Progress stages and achievement badges
- Interactive timeline chart
- Act comparison mode
- Glossary of Brussels terms
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import altair as alt

import eu
from eu import act_tracker, act_summaries, fallback_timelines

# -----------------------------------------------------------------------------
# Page configuration & custom styling
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="EU Regulatory Intelligence",
    page_icon="🇪🇺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for metrics, gauges, badges, and stage indicators
st.markdown("""
<style>
    div[data-testid="metric-container"] {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        padding: 16px;
        border-radius: 10px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        transition: transform 0.2s ease;
    }
    div[data-testid="metric-container"]:hover {
        transform: translateY(-2px);
        border-color: #003399;
    }
    .stTabs [data-baseweb="tab-list"] { gap: 12px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #ffffff;
        border-radius: 6px 6px 0px 0px;
        padding: 10px 20px;
        border: 1px solid #e2e8f0;
    }
    .slogan-box {
        margin-bottom: 25px;
        color: #64748b;
        font-size: 1.1rem;
        font-style: italic;
    }
    .badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-right: 8px;
        margin-bottom: 6px;
        background-color: #e2e8f0;
        color: #1e293b;
    }
    .badge-green { background-color: #dcfce7; color: #166534; }
    .badge-yellow { background-color: #fef9c3; color: #854d0e; }
    .badge-red { background-color: #fee2e2; color: #991b1b; }
    .badge-blue { background-color: #dbeafe; color: #1e40af; }
    .badge-purple { background-color: #f3e8ff; color: #6b21a8; }
    .stage-container {
        background-color: #f1f5f9;
        border-radius: 8px;
        padding: 12px 18px;
        margin: 10px 0;
        border-left: 4px solid #003399;
    }
    .stage-label {
        font-weight: 600;
        font-size: 1.1rem;
        color: #0f172a;
    }
    .stage-progress {
        background-color: #e2e8f0;
        border-radius: 10px;
        height: 8px;
        margin-top: 6px;
    }
    .stage-progress-fill {
        height: 100%;
        border-radius: 10px;
        background: linear-gradient(90deg, #3b82f6, #003399);
        transition: width 0.4s ease;
    }
    .gauge-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 4px;
        height: 100%;
    }
    .gauge-ring {
        width: 100px;
        height: 100px;
        border-radius: 50%;
        background: conic-gradient(
            var(--gauge-color) var(--gauge-percent),
            #e2e8f0 var(--gauge-percent)
        );
        display: flex;
        align-items: center;
        justify-content: center;
        position: relative;
    }
    .gauge-ring::after {
        content: "";
        position: absolute;
        width: 76px;
        height: 76px;
        background: white;
        border-radius: 50%;
    }
    .gauge-value {
        position: relative;
        z-index: 1;
        font-weight: 700;
        font-size: 1.6rem;
        color: #0f172a;
    }
    .gauge-label {
        font-size: 0.9rem;
        color: #64748b;
        margin-top: 4px;
    }
    .gauge-status {
        font-weight: 600;
        font-size: 1.1rem;
        margin-top: 2px;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Header and sidebar
# -----------------------------------------------------------------------------
st.title("🇪🇺 EU Regulatory Intelligence Dashboard")
st.markdown(
    '<p class="slogan-box">"Is the EU actually doing that?" — Real‑time automated tracking and civic transparency analysis.</p>',
    unsafe_allow_html=True
)

st.sidebar.header("⚙️ Control Panel")

act_names = list(act_tracker.keys())
selected_name = st.sidebar.selectbox("Select a Legislative Act:", act_names)
procedure_code = act_tracker[selected_name]

compare = st.sidebar.checkbox("🔁 Compare with another act", value=False)
if compare:
    compare_name = st.sidebar.selectbox(
        "Choose act to compare:",
        [a for a in act_names if a != selected_name],
        key="compare_act"
    )
    compare_code = act_tracker[compare_name]
else:
    compare_name = None
    compare_code = None

if st.sidebar.button("🔄 Live Data Refresh", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.info("💡 **Tip:** Data is cached for 10 minutes. Click refresh to force a live fetch.")

# -----------------------------------------------------------------------------
# Data fetching with caching
# -----------------------------------------------------------------------------
@st.cache_data(ttl=600, show_spinner="Fetching live data from EU API...")
def fetch_act_data(procedure_code, act_name):
    """Fetch timeline data from the EU API or fallback to local data."""
    timeline = eu.fetch_timeline_from_api(procedure_code)
    if not timeline:
        timeline = eu.fallback_timelines.get(act_name, [])
    return timeline, datetime.now()

timeline_data, last_fetched = fetch_act_data(procedure_code, selected_name)
if compare:
    compare_timeline, _ = fetch_act_data(compare_code, compare_name)
else:
    compare_timeline = None

st.sidebar.caption(f"🕒 Last updated: {last_fetched.strftime('%H:%M:%S')}")

# -----------------------------------------------------------------------------
# Metrics helper
# -----------------------------------------------------------------------------
def get_act_metrics(timeline):
    """Compute all metrics for a given timeline."""
    if not timeline:
        return None
    health = eu.compute_act_health(timeline)
    m_cwp = eu.mean_CWP_meeting(timeline)
    m_cor = eu.mean_COR_meeting(timeline)
    urgent = eu.is_urgent(timeline)
    stage, progress = eu.classify_stage(timeline)
    badges = eu.get_badges(timeline)
    return {
        "health": health,
        "m_cwp": m_cwp,
        "m_cor": m_cor,
        "urgent": urgent,
        "stage": stage,
        "progress": progress,
        "badges": badges,
        "total_events": len(timeline)
    }

metrics = get_act_metrics(timeline_data)
if compare:
    compare_metrics = get_act_metrics(compare_timeline)
else:
    compare_metrics = None

if not timeline_data:
    st.warning("⚠️ Could not retrieve data for this dossier.")
    st.stop()

# -----------------------------------------------------------------------------
# Main content
# -----------------------------------------------------------------------------
st.subheader(f"{selected_name} (`{procedure_code}`)")

# Layout: main column (and compare column if enabled)
if compare:
    col_main, col_compare = st.columns([2, 1])
else:
    col_main = st.columns(1)[0]
    col_compare = None

with col_main:
    # Row: metrics 2x2 on the left, health gauge on the right
    left_col, right_col = st.columns([3, 1])

    with left_col:
        row1 = st.columns(2)
        row1[0].metric("Total Milestones", metrics["total_events"])
        row1[1].metric("Mean CWP Gap", f"{metrics['m_cwp']:.1f} days")

        row2 = st.columns(2)
        row2[0].metric("Mean Coreper Gap", f"{metrics['m_cor']:.1f} days")
        row2[1].metric("Active Urgency", "YES 🚨" if metrics["urgent"] else "NO 🟢")

    with right_col:
        health = metrics["health"]
        score = health["score"]
        status = health["status"]
        color = {"Healthy": "green", "At Risk": "orange", "Stalled": "red", "Urgent": "red"}.get(status, "gray")

        st.markdown(f"""
        <div class="gauge-container">
            <div class="gauge-ring" style="--gauge-percent: {score}%; --gauge-color: {color};">
                <span class="gauge-value">{score}</span>
            </div>
            <div class="gauge-status" style="color:{color};">{status}</div>
            <div class="gauge-label">Health Score</div>
        </div>
        """, unsafe_allow_html=True)

    # Badges
    if metrics["badges"]:
        st.markdown("#### 🏅 Achievements")
        badge_html = "".join(
            f'<span class="badge {cls}">{badge}</span>'
            for badge, cls in metrics["badges"]
        )
        st.markdown(badge_html, unsafe_allow_html=True)

    # Progress stage
    stage = metrics["stage"]
    progress = metrics["progress"]
    st.markdown(f"""
    <div class="stage-container">
        <div class="stage-label">📍 Current Stage: {stage}</div>
        <div class="stage-progress">
            <div class="stage-progress-fill" style="width:{progress}%;"></div>
        </div>
        <div style="font-size:0.85rem; color:#475569; margin-top:4px;">
            Estimated progress: {progress}% of typical legislative cycle
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Act summary
    st.markdown("#### 📖 About this Act")
    summary = act_summaries.get(selected_name, "No summary available.")
    st.info(summary)

# Compare column
if compare and col_compare is not None:
    with col_compare:
        st.markdown(f"### ↔️ {compare_name}")
        st.markdown(f"`{compare_code}`")
        if compare_metrics:
            c_health = compare_metrics["health"]
            c_score = c_health["score"]
            c_status = c_health["status"]
            c_color = {"Healthy": "green", "At Risk": "orange", "Stalled": "red", "Urgent": "red"}.get(c_status, "gray")
            st.markdown(f"""
            <div class="gauge-container" style="justify-content:flex-start;">
                <div class="gauge-ring" style="--gauge-percent: {c_score}%; --gauge-color: {c_color}; width:60px; height:60px;">
                    <span class="gauge-value" style="font-size:1rem;">{c_score}</span>
                </div>
                <div class="gauge-status" style="color:{c_color};">{c_status}</div>
                <div class="gauge-label" style="font-size:0.8rem;">Health</div>
            </div>
            """, unsafe_allow_html=True)
            st.metric("Total Milestones", compare_metrics["total_events"])
            st.metric("Urgency", "YES 🚨" if compare_metrics["urgent"] else "NO 🟢")
            st.caption(f"Stage: {compare_metrics['stage']} ({compare_metrics['progress']}%)")
        else:
            st.warning("No data for comparison act.")

# -----------------------------------------------------------------------------
# Interactive Timeline Chart
# -----------------------------------------------------------------------------
st.markdown("### 🧭 Legislative Lifecycle – Interactive View")
st.caption("Use the legend to toggle event types on/off. Hover for details.")

event_types = ["CWP", "Coreper", "European Parliament", "Trilogue"]
selected_types = st.multiselect(
    "Show event types:",
    options=event_types,
    default=event_types,
    key="event_filter"
)

try:
    chart = eu.visualize_timeline_for_streamlit(
        timeline_data=timeline_data,
        act_name=selected_name,
        include_types=selected_types
    )
    st.altair_chart(chart, use_container_width=True)
except Exception as e:
    st.error(f"Error generating chart: {e}")

if compare and compare_timeline:
    st.markdown("---")
    st.markdown(f"#### 🔁 Overlay: {compare_name} (dashed lines)")
    try:
        chart_compare = eu.visualize_timeline_for_streamlit(
            timeline_data=compare_timeline,
            act_name=compare_name,
            include_types=selected_types,
            is_compare=True,
            base_color="#ef4444"
        )
        st.altair_chart(chart_compare, use_container_width=True)
    except Exception as e:
        st.error(f"Error generating compare chart: {e}")

# -----------------------------------------------------------------------------
# Glossary / Explainer (placed below the chart)
# -----------------------------------------------------------------------------
with st.expander("📖 What do these Brussels terms mean?"):
    st.markdown("""
    - **Council Working Party (CWP):** Technical groups where national diplomats dissect the proposal line by line.
    - **Coreper:** Committee of Permanent Representatives (Ambassadors). They iron out political deals before ministerial votes.
    - **European Parliament (EP):** The directly elected house representing citizens, adopting committee reports and plenary resolutions.
    - **Trilogues:** Informal negotiations between Parliament, Council, and Commission. *When trilogues accelerate, a final deal is near.*
    - **Active Urgency Alert:** Calculated automatically based on meeting cadences and clustering.
    """)