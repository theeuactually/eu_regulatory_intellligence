"""EU legislative tracking – data fetching, analysis, visualisation, and reporting.

This module provides:
- Local fallback timelines for example legislative acts.
- API client for the EU Law Tracker.
- Metrics: mean meeting gaps, urgency detection, health scoring.
- Stage classification and progress estimation.
- Achievement badges.
- Narrative generation.
- Altair and Matplotlib visualisations.
- Automated report generation (CLI entry point).
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import altair as alt
import pandas as pd
import os
from datetime import datetime, timedelta
import requests
import re

# -----------------------------------------------------------------------------
# Configuration and static data
# -----------------------------------------------------------------------------

acts = ['Industrial Accelerator Act', 'EU Inc.', 'Saving and Investments Union', 'Chat Control']

act_tracker = {
    'Industrial Accelerator Act': '2026/0068(COD)',
    'EU Inc.': '2026/0074(COD)',
    'Saving and Investments Union': '2025/0383(COD)',
    'Chat Control': '2022/0155(COD)'
}

fallback_timelines = {
    'Industrial Accelerator Act': [
        ("Adoption of legislative proposal by the Commission", "2026-03-05"),
        ("Deliberations in Council working party", "2026-03-16"),
        ("Deliberations in Council working party", "2026-03-23"),
        ("Deliberations in Council working party", "2026-03-27"),
        ("Deliberations in Council working party", "2026-04-16"),
        ("Deliberations in Council working party", "2026-04-27"),
        ("Deliberations in Council working party", "2026-04-28"),
        ("Referral of the legislative proposal to the EP committee responsible (announced in plenary)", "2026-04-30"),
        ("Deliberations in Council working party", "2026-05-11"),
        ("Deliberations in Council working party", "2026-05-18"),
        ("Deliberations in Council working party", "2026-05-21"),
        ("Deliberations in Council", "2026-05-28"),
        ("Deliberations in Council working party", "2026-06-01"),
        ("Deliberations in Council working party", "2026-06-04"),
        ("Deliberations in Council working party", "2026-06-11"),
        ("Deliberations in Council working party", "2026-06-12"),
        ("Deliberations in Coreper", "2026-06-24"),
        ("Deliberations in Council working party", "2026-06-29"),
        ("Deliberations in Council working party", "2026-07-02"),
        ("Deliberations in Council working party", "2026-07-06"),
        ("Deliberations in Coreper", "2026-07-15")
    ],
    'EU Inc.': [
        ("Deliberations in Council", "2025-12-08"),
        ("Deliberations in Council", "2026-02-24"),
        ("Adoption of legislative proposal by the Commission", "2026-03-18"),
        ("Deliberations in Council working party", "2026-03-23"),
        ("Deliberations in Council working party", "2026-03-26"),
        ("Deliberations in Council working party", "2026-04-17"),
        ("Deliberations in Council working party", "2026-04-24"),
        ("Deliberations in Council working party", "2026-04-27"),
        ("Deliberations in Council working party", "2026-05-06"),
        ("Deliberations in Council working party", "2026-05-07"),
        ("Referral of the legislative proposal to the EP committee responsible (announced in plenary)", "2026-05-18"),
        ("Deliberations in Council working party", "2026-05-18"),
        ("Deliberations in Coreper", "2026-05-20"),
        ("Deliberations in Council", "2026-05-28"),
        ("Deliberations in Council working party", "2026-06-02"),
        ("Deliberations in Council working party", "2026-06-11"),
        ("Deliberations in Coreper", "2026-06-24"),
        ("Deliberations in Council working party", "2026-06-25"),
        ("EP committee draft report", "2026-06-29"),
        ("Deliberations in Council working party", "2026-07-02"),
        ("Deliberations in Council working party", "2026-07-08"),
        ("Deliberations in Coreper", "2026-07-15"),
        ("Adoption of an opinion by the EP opinion-giving committee", "2026-07-15"),
        ("Tabling of amendments in the EP committee responsible", "2026-07-22"),
        ("Deliberations in Council working party", "2026-07-23"),
        ("Deliberations in Council working party", "2026-09-01")
    ],
    'Saving and Investments Union': [
        ("Adoption of legislative proposal by the Commission", "2025-12-04"),
        ("Deliberations in Coreper", "2025-12-10"),
        ("Deliberations in Council", "2025-12-12"),
        ("Referral of the legislative proposal to the EP committee responsible (announced in plenary)", "2026-01-27"),
        ("Deliberations in Council working party", "2026-02-19"),
        ("Deliberations in Council working party", "2026-02-20"),
        ("Deliberations in Coreper", "2026-03-04"),
        ("Deliberations in Council working party", "2026-03-04"),
        ("Deliberations in Council working party", "2026-03-05"),
        ("Deliberations in Council", "2026-03-10"),
        ("European Economic and Social Committee opinion", "2026-03-18"),
        ("Deliberations in Council working party", "2026-03-30"),
        ("Deliberations in Council working party", "2026-03-31"),
        ("European Central Bank opinion", "2026-04-09"),
        ("Deliberations in Council working party", "2026-04-15"),
        ("Deliberations in Council working party", "2026-04-20"),
        ("Deliberations in Council working party", "2026-04-27"),
        ("Deliberations in Coreper", "2026-04-29"),
        ("Deliberations in Council", "2026-05-05"),
        ("Deliberations in Council working party", "2026-05-07"),
        ("Deliberations in Council working party", "2026-05-08"),
        ("Deliberations in Council working party", "2026-05-27"),
        ("Deliberations in Council working party", "2026-05-28"),
        ("Deliberations in Council working party", "2026-06-02"),
        ("Deliberations in Coreper", "2026-06-10"),
        ("EP committee draft report", "2026-06-11"),
        ("Deliberations in Council", "2026-06-12"),
        ("Deliberations in Council working party", "2026-06-15"),
        ("Deliberations in Council working party", "2026-06-16"),
        ("Deliberations in Coreper", "2026-06-26"),
        ("Deliberations in Coreper", "2026-07-01"),
        ("Deliberations in Coreper", "2026-07-08"),
        ("Deliberations in Council", "2026-07-10"),
        ("Deliberations in Council working party", "2026-07-17"),
        ("Tabling of amendments in the EP committee responsible", "2026-07-31")
    ],
    'Chat Control': [
        ("Adoption of legislative proposal by the Commission", "2022-05-11"),
        ("Referral of the legislative proposal to the EP committee responsible (announced in plenary)", "2022-09-12"),
        ("EP committee draft report", "2023-05-11"),
        ("Tabling of amendments in the EP committee responsible", "2023-07-14"),
        ("Endorsement by EP plenary of the committee decision to start interinstitutional negotiations", "2023-11-22"),
        ("Adoption of position by the European Parliament", "2023-11-22"),
        ("First reading conclusion/ep stale", "2024-04-24"),
        ("Deliberations in Coreper", "2024-11-20"),
        ("Deliberations in Council", "2024-11-20"),
        ("Deliberations in Council working party", "2025-03-05"),
        ("Deliberations in Council working party", "2025-04-10"),
        ("Deliberations in Council working party", "2025-06-12"),
        ("Deliberations in Council working party", "2025-09-15"),
        ("Deliberations in Coreper", "2025-10-18"),
        ("Deliberations in Council working party", "2025-11-05"),
        ("Deliberations in Council working party", "2025-12-01"),
        ("Deliberations in Council working party", "2025-12-10"),
        ("Deliberations in Council working party", "2026-01-14"),
        ("Deliberations in Council working party", "2026-02-10"),
        ("Deliberations in Council working party", "2026-03-05"),
        ("Deliberations in Council working party", "2026-04-12"),
        ("Trilogue meeting", "2025-11-20"),
        ("Trilogue meeting", "2026-02-15"),
        ("Trilogue meeting", "2026-04-10"),
        ("Trilogue meeting", "2026-05-30")
    ]
}

act_summaries = {
    'Industrial Accelerator Act': (
        "Aims to boost Europe's industrial competitiveness by streamlining permitting, "
        "accelerating strategic projects, and mobilising public-private investments."
    ),
    'EU Inc.': (
        "Proposes a new legal form for start‑ups and scale‑ups across the EU, "
        "reducing administrative burden and harmonising corporate law for innovation."
    ),
    'Saving and Investments Union': (
        "Seeks to deepen the Capital Markets Union by facilitating cross‑border "
        "investment, strengthening retail investor protection, and creating a "
        "single market for savings and investment products."
    ),
    'Chat Control': (
        "A highly debated regulation on child sexual abuse material (CSAM) detection, "
        "introducing scanning obligations for digital services and raising privacy concerns."
    )
}

# -----------------------------------------------------------------------------
# API client
# -----------------------------------------------------------------------------

def format_reference_code(procedure_code: str) -> str:
    """Convert a procedure code into the format expected by the EU Law Tracker API."""
    match = re.match(r"(\d+)/(\d+)", procedure_code)
    if match:
        year, num = match.groups()
        return f"{year}_{int(num)}"
    return procedure_code.replace("/", "_").split("(")[0]


def fetch_timeline_from_api(procedure_code: str) -> list:
    """Retrieve the legislative timeline from the EU Law Tracker API.

    Args:
        procedure_code (str): The procedure code (e.g., '2026/0068(COD)').

    Returns:
        list: A list of (event_description, date_string) tuples, or an empty list on failure.
    """
    ref_code = format_reference_code(procedure_code)
    url = f"https://law-tracker.europa.eu/notice/timeline?reference={ref_code}&version=null&lang=en"

    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "es-ES,es;q=0.9",
        "Cache-Control": "No-Cache",
        "User-Agent": "Mozilla/5.0",
        "Referer": f"https://law-tracker.europa.eu/procedure/{ref_code}?lang=en",
        "X-Requested-With": "XMLHttpRequest"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            raw_data = response.json()
            timeline = []
            for item in raw_data.get("events", []):
                event_desc = item.get("type")
                raw_date = item.get("date")
                if event_desc and raw_date:
                    try:
                        parsed_date = datetime.strptime(raw_date, "%d/%m/%Y").strftime("%Y-%m-%d")
                        timeline.append((event_desc, parsed_date))
                    except ValueError:
                        continue
            if timeline:
                return timeline
    except Exception:
        pass
    return []

# -----------------------------------------------------------------------------
# Analytical metrics
# -----------------------------------------------------------------------------

def mean_EP_meeting(timeline: list) -> float:
    """Calculate the average gap (in days) between European Parliament-related events."""
    ep_dates = [date for event, date in timeline if any(k in event.lower() for k in ['ep', 'parliament', 'committee'])]
    if len(ep_dates) < 2:
        return 0.0
    ep_dates = [np.datetime64(date) for date in ep_dates]
    return float(np.mean(np.diff(ep_dates).astype('timedelta64[D]').astype(int)))


def mean_Trilogue_meeting(timeline: list) -> float:
    """Calculate the average gap (in days) between Trilogue meetings."""
    trilogue_dates = [date for event, date in timeline if "trilogue" in event.lower()]
    if len(trilogue_dates) < 2:
        return 0.0
    trilogue_dates = [np.datetime64(date) for date in trilogue_dates]
    return float(np.mean(np.diff(trilogue_dates).astype('timedelta64[D]').astype(int)))


def mean_CWP_meeting(timeline: list) -> float:
    """Calculate the average gap (in days) between Council Working Party meetings."""
    cwp_dates = [np.datetime64(date) for event, date in timeline if "Council working party" in event]
    if len(cwp_dates) < 2:
        return 0.0
    return float(np.mean(np.diff(cwp_dates).astype('timedelta64[D]').astype(int)))


def mean_COR_meeting(timeline: list) -> float:
    """Calculate the average gap (in days) between Coreper meetings."""
    cor_dates = [np.datetime64(date) for event, date in timeline if "Coreper" in event]
    if len(cor_dates) < 2:
        return 0.0
    return float(np.mean(np.diff(cor_dates).astype('timedelta64[D]').astype(int)))


def distance_last_CWP_COR_meeting(timeline: list) -> float:
    """Return the absolute difference (in days) between the last CWP and last Coreper meeting."""
    cwp_dates = [date for event, date in timeline if "Council working party" in event]
    cor_dates = [date for event, date in timeline if "Coreper" in event]
    if not cwp_dates or not cor_dates:
        return 0.0
    return abs((np.datetime64(cwp_dates[-1]) - np.datetime64(cor_dates[-1])).astype('timedelta64[D]').astype(int))


def is_urgent(timeline: list) -> bool:
    """Determine if the legislative process is urgent based on meeting frequency."""
    mean_cwp = mean_CWP_meeting(timeline)
    mean_cor = mean_COR_meeting(timeline)
    distance = distance_last_CWP_COR_meeting(timeline)
    return (mean_cwp <= 14 or mean_cor <= 14) and distance <= 10


def compute_act_health(timeline: list) -> dict:
    """Evaluate legislative health and return a status, score, and explanatory message.

    Args:
        timeline (list): List of (event, date) tuples.

    Returns:
        dict: Contains keys 'status', 'score' (0-100), 'message', and 'details'.
    """
    if not timeline:
        return {"status": "Unknown", "score": 0, "message": "No timeline data.", "details": {}}

    total_events = len(timeline)
    m_cwp = mean_CWP_meeting(timeline)
    m_cor = mean_COR_meeting(timeline)
    urgent_flag = is_urgent(timeline)

    last_date = sorted([pd.to_datetime(date) for _, date in timeline])[-1]
    days_since_last = (pd.Timestamp.now() - last_date).days

    score = 100
    issues = []
    if m_cwp > 30:
        score -= 20
        issues.append(f"CWP gap {m_cwp:.1f}d")
    if m_cor > 30:
        score -= 15
        issues.append(f"Coreper gap {m_cor:.1f}d")
    if days_since_last > 60:
        score -= 25
        issues.append(f"inactive {days_since_last}d")
    elif days_since_last > 30:
        score -= 10
    if total_events > 20:
        score += 10
    elif total_events < 5:
        score -= 10
    score = max(0, min(100, score))

    if urgent_flag:
        status = "Urgent"
        message = "Fast‑track process – high meeting frequency."
    elif score >= 80:
        status = "Healthy"
        message = "Steady progress with regular milestones."
    elif score >= 50:
        status = "At Risk"
        message = "Some delays or low activity; monitor closely."
    else:
        status = "Stalled"
        message = "Significant inactivity or very slow progress."

    return {
        "status": status,
        "score": score,
        "message": message,
        "details": {
            "total_events": total_events,
            "mean_cwp": m_cwp,
            "mean_cor": m_cor,
            "days_since_last": days_since_last,
            "urgent": urgent_flag
        }
    }

# -----------------------------------------------------------------------------
# Stage classification, badges, and narrative
# -----------------------------------------------------------------------------

def classify_stage(timeline: list) -> tuple:
    """Classify the current legislative stage and estimate progress (0-100%).

    Args:
        timeline (list): List of (event, date) tuples.

    Returns:
        tuple: (stage_name, progress_percent)
    """
    if not timeline:
        return "Unknown", 0

    events = [event for event, _ in timeline]
    event_lower = [e.lower() for e in events]

    if any("trilogue" in e for e in event_lower):
        stage = "Trilogue negotiations"
        progress = 85
    elif any("adoption of position by the european parliament" in e for e in event_lower):
        stage = "EP position adopted"
        progress = 70
    elif any("ep committee draft report" in e for e in event_lower):
        stage = "EP committee review"
        progress = 55
    elif any("referral" in e for e in event_lower):
        stage = "Parliament referral"
        progress = 40
    elif any("adoption of legislative proposal by the commission" in e for e in event_lower):
        stage = "Commission proposal"
        progress = 20
    elif any("coreper" in e for e in event_lower) or any("council working party" in e for e in event_lower):
        stage = "Council negotiations"
        progress = 30
    else:
        stage = "Early stages"
        progress = 10

    if len(timeline) > 30:
        progress = min(95, progress + 10)
    elif len(timeline) > 20:
        progress = min(90, progress + 5)

    return stage, min(progress, 100)


def get_badges(timeline: list) -> list:
    """Return a list of achievement badges based on the timeline.

    Each badge is a tuple (badge_text, css_class).
    """
    badges = []
    events = [event for event, _ in timeline]
    event_lower = [e.lower() for e in events]

    if any("trilogue" in e for e in event_lower):
        badges.append(("🏛️ Trilogue reached", "badge-purple"))
    if is_urgent(timeline):
        badges.append(("🚀 Fast‑Track", "badge-red"))
    if len(timeline) > 30:
        badges.append(("📈 High activity", "badge-blue"))
    if any("adoption of legislative proposal by the commission" in e for e in event_lower):
        badges.append(("📄 Commission proposal", "badge-green"))
    if any("referral" in e for e in event_lower):
        badges.append(("📋 Referred to EP", "badge-yellow"))
    if any("coreper" in e for e in event_lower):
        badges.append(("🤝 Coreper involvement", "badge-blue"))
    if any("council working party" in e for e in event_lower):
        badges.append(("⚙️ CWP discussions", "badge-green"))

    if compute_act_health(timeline)["status"] == "Stalled":
        badges.append(("⏳ Stalled", "badge-red"))

    if len(timeline) < 5:
        badges.append(("🌱 Just started", "badge-yellow"))

    return badges[:5]  # limit to 5 badges


def generate_narrative(timeline: list, act_name: str) -> str:
    """Generate a human‑readable summary of the act's legislative journey."""
    if not timeline:
        return f"No timeline data available for {act_name}."

    sorted_timeline = sorted(timeline, key=lambda x: x[1])
    first_event, first_date = sorted_timeline[0]
    last_event, last_date = sorted_timeline[-1]
    total_events = len(sorted_timeline)

    cwp_count = sum(1 for e, _ in sorted_timeline if "Council working party" in e)
    cor_count = sum(1 for e, _ in sorted_timeline if "Coreper" in e)
    ep_count = sum(1 for e, _ in sorted_timeline if any(k in e.lower() for k in ['ep', 'parliament', 'committee']))
    trilogue_count = sum(1 for e, _ in sorted_timeline if "trilogue" in e.lower())

    last_dt = pd.to_datetime(last_date)
    days_since = (pd.Timestamp.now() - last_dt).days

    parts = [
        f"The legislative journey of **{act_name}** began on {first_date} with “{first_event}”.",
        f"Since then, **{total_events}** milestones have been recorded.",
    ]
    if cwp_count:
        parts.append(f"The Council Working Party has met **{cwp_count}** times.")
    if cor_count:
        parts.append(f"Coreper has convened **{cor_count}** times.")
    if ep_count:
        parts.append(f"The European Parliament has been involved in **{ep_count}** events.")
    if trilogue_count:
        parts.append(f"**{trilogue_count}** trilogue meetings indicate active interinstitutional negotiations.")

    if days_since <= 7:
        parts.append(f"🟢 The most recent activity was **{days_since}** days ago – very current.")
    elif days_since <= 30:
        parts.append(f"🟡 The last event occurred **{days_since}** days ago – moderate pace.")
    else:
        parts.append(f"🔴 No new events for **{days_since}** days – may be stalled.")

    health = compute_act_health(timeline)
    parts.append(f"**Health status:** {health['status']} ({health['score']}/100) – {health['message']}")

    return " ".join(parts)

# -----------------------------------------------------------------------------
# Visualisation (Altair and Matplotlib)
# -----------------------------------------------------------------------------

def visualize_timeline_for_streamlit(
    timeline_data: list,
    act_name: str = "",
    include_types: list = None,
    is_compare: bool = False,
    base_color: str = None
) -> alt.Chart:
    """Generate an interactive Altair chart for Streamlit.

    Args:
        timeline_data: List of (event, date) tuples.
        act_name: Title for the chart.
        include_types: List of event types to include (e.g., ["CWP", "Coreper"]).
        is_compare: If True, use dashed lines and a different colour scheme.
        base_color: Optional base colour for compare mode.

    Returns:
        alt.Chart: The Altair chart object.
    """
    if not timeline_data:
        raise ValueError("No timeline data to visualise")

    df = pd.DataFrame(timeline_data, columns=["Event", "Date"])
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values("Date").reset_index(drop=True)

    def classify(event: str) -> str:
        if "Council working party" in event:
            return "CWP"
        elif "Coreper" in event:
            return "Coreper"
        elif any(word in event for word in ["EP", "Parliament", "Committee"]):
            return "European Parliament"
        elif "trilogue" in event.lower():
            return "Trilogue"
        else:
            return "Other"

    df["Type"] = df["Event"].apply(classify)

    if include_types:
        df = df[df["Type"].isin(include_types)]

    if df.empty:
        raise ValueError("No events of selected types.")

    # Lines for CWP and Coreper: cumulative count per type
    line_data = df[df["Type"].isin(["CWP", "Coreper"])].copy()
    if not line_data.empty:
        line_data = line_data.sort_values(["Type", "Date"])
        line_data["Cumulative"] = line_data.groupby("Type").cumcount() + 1
    else:
        line_data = pd.DataFrame(columns=["Event", "Date", "Type", "Cumulative"])

    # Rules for EP and Trilogue
    rule_data = df[df["Type"].isin(["European Parliament", "Trilogue"])].copy()

    if is_compare:
        color_domain = ["CWP", "Coreper", "European Parliament", "Trilogue"]
        color_range = [base_color or "#ef4444"] * 4
        stroke_dash = [4, 4]  # dashed
    else:
        color_domain = ["CWP", "Coreper", "European Parliament", "Trilogue"]
        color_range = ["#003399", "#F59E0B", "#3B82F6", "#10B981"]
        stroke_dash = [1, 0]  # solid

    color_scale = alt.Scale(domain=color_domain, range=color_range)

    charts = []

    if not line_data.empty:
        line_chart = alt.Chart(line_data).mark_line(
            point=alt.OverlayMarkDef(size=60, filled=True),
            strokeDash=stroke_dash
        ).encode(
            x=alt.X("Date:T", title="Date", axis=alt.Axis(format="%b %Y", labelAngle=30)),
            y=alt.Y("Cumulative:Q", title="Cumulative Milestones", scale=alt.Scale(zero=True)),
            color=alt.Color("Type:N", scale=color_scale, title="Event Type"),
            tooltip=["Event:N", "Date:T", "Type:N"]
        )
        charts.append(line_chart)

    if not rule_data.empty:
        rule_chart = alt.Chart(rule_data).mark_rule(
            strokeWidth=2,
            opacity=0.8,
            strokeDash=stroke_dash
        ).encode(
            x="Date:T",
            color=alt.Color("Type:N", scale=color_scale, title="Event Type"),
            tooltip=["Event:N", "Date:T", "Type:N"]
        )
        charts.append(rule_chart)

    if not charts:
        raise ValueError("No data to plot after filtering.")

    chart = alt.layer(*charts).resolve_scale(
        color="shared"
    ).properties(
        title=alt.TitleParams(
            f"{'Comparison: ' if is_compare else ''}Institutional Activity – {act_name}",
            fontSize=16,
            fontWeight="bold",
            color="#1E293B",
            subtitle="Lines: cumulative meetings (CWP & Coreper)  |  Vertical lines: EP & Trilogue milestones"
        ),
        width="container",
        height=400
    ).configure_axis(
        labelFontSize=11,
        titleFontSize=12,
        gridColor="#E2E8F0",
        gridOpacity=0.5
    ).configure_legend(
        titleFontSize=12,
        labelFontSize=11,
        orient="top-left",
        offset=10
    ).interactive()

    return chart


def visualize_legislative_timeline(timeline_data: list, act_name: str = "", save_path: str = None) -> plt.Figure:
    """Matplotlib version of the timeline visualisation (used for CLI report generation)."""
    if not timeline_data:
        raise ValueError("No timeline data to visualise")

    fig, ax = plt.subplots(figsize=(10, 5))
    cwp_events = sorted([(datetime.strptime(date, "%Y-%m-%d"), event) for event, date in timeline_data if "Council working party" in event], key=lambda x: x[0])
    cor_events = sorted([(datetime.strptime(date, "%Y-%m-%d"), event) for event, date in timeline_data if "Coreper" in event], key=lambda x: x[0])
    ep_dates = sorted([datetime.strptime(date, "%Y-%m-%d") for event, date in timeline_data if any(k in event.lower() for k in ['ep', 'parliament', 'committee'])])
    trilogue_dates = sorted([datetime.strptime(date, "%Y-%m-%d") for event, date in timeline_data if "trilogue" in event.lower()])

    if cwp_events:
        cwp_dates, _ = zip(*cwp_events)
        ax.plot(cwp_dates, range(len(cwp_dates)), marker='o', label='Council Working Parties', color='#003399', linewidth=2, alpha=0.7)
    if cor_events:
        cor_dates, _ = zip(*cor_events)
        ax.plot(cor_dates, range(len(cor_dates)), marker='s', label='Coreper (Ambassadors)', color='#F59E0B', linewidth=2, alpha=0.7)
    for i, date in enumerate(ep_dates):
        ax.axvline(x=mdates.date2num(date), color='#3B82F6', linestyle='--', linewidth=1.5, alpha=0.8, label='European Parliament' if i == 0 else "")
    for i, date in enumerate(trilogue_dates):
        ax.axvline(x=mdates.date2num(date), color='#10B981', linestyle='-', linewidth=2.5, alpha=0.9, label='Trilogues' if i == 0 else "")

    ax.set_title(f"Institutional Dynamics - {act_name}" if act_name else "Legislative Timeline", fontsize=12, fontweight='bold', pad=15)
    ax.set_xlabel("Date", fontsize=10)
    ax.set_ylabel("Milestone Count", fontsize=10)
    ax.grid(True, linestyle='--', alpha=0.6)
    handles, labels = ax.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    ax.legend(by_label.values(), by_label.keys(), loc='upper left', frameon=True)
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
    return fig

# -----------------------------------------------------------------------------
# Automated report generation (CLI entry point)
# -----------------------------------------------------------------------------

def run_automation():
    """Generate a markdown report and charts for all tracked acts."""
    os.makedirs("output_reports", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_filename = f"output_reports/regulatory_intelligence_report_{timestamp}.md"

    report_lines = [
        "============================================================",
        "EU REGULATORY INTELLIGENCE - AUTOMATED REPORT (LIVE DATA)",
        f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "============================================================",
        ""
    ]

    for act_name, code in act_tracker.items():
        timeline = fetch_timeline_from_api(code)
        if not timeline:
            timeline = fallback_timelines.get(act_name, [])

        if not timeline:
            continue

        m_cwp = mean_CWP_meeting(timeline)
        m_cor = mean_COR_meeting(timeline)
        dist = distance_last_CWP_COR_meeting(timeline)
        urgent = "[YES]" if is_urgent(timeline) else "[NO]"
        health = compute_act_health(timeline)
        stage, progress = classify_stage(timeline)
        badges = get_badges(timeline)
        narrative = generate_narrative(timeline, act_name)

        act_summary = [
            f"Act: {act_name} ({code})",
            f"  - Health: {health['status']} ({health['score']}/100) – {health['message']}",
            f"  - Stage: {stage} ({progress}% complete)",
            f"  - Mean CWP: {m_cwp:.2f} days",
            f"  - Mean Coreper: {m_cor:.2f} days",
            f"  - Urgency Alert: {urgent}",
            f"  - Badges: {', '.join(b[0] for b in badges) if badges else 'None'}",
            "",
            "  [Narrative]",
            narrative,
            "",
            "  [Timeline Summary]"
        ]
        for date, event in sorted(timeline, key=lambda x: x[1]):
            act_summary.append(f"{date}: {event}")
        act_summary.append("-" * 60)
        act_summary.append("")

        report_lines.extend(act_summary)

        safe_name = act_name.split("(")[0].strip().replace(" ", "_")
        save_path = f"output_reports/{safe_name}_{timestamp}.png"
        try:
            fig = visualize_legislative_timeline(timeline_data=timeline, act_name=act_name, save_path=save_path)
            plt.close(fig)
        except Exception as e:
            print(f"Error generating chart for {act_name}: {e}")

    report_content = "\n".join(report_lines)
    with open(report_filename, "w", encoding="utf-8") as f:
        f.write(report_content)

    print(report_content)
    print(f"\n[Automation Success] Report saved to '{report_filename}' and graphs exported to 'output_reports/'.")


if __name__ == "__main__":
    run_automation()