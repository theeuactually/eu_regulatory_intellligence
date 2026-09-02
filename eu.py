import numpy as np 
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import os
from datetime import datetime
import requests
import re

acts = ['Industrial Accelerator Act', 'EU Inc.', 'Saving and Investments Union', 'Chat Control']

act_tracker = {'Industrial Accelerator Act' : '2026/0068(COD)', 'EU Inc.' : '2026/0074(COD)', 'Saving and Investments Union' : '2025/0383(COD)',
               'Chat Control' : '2022/0155(COD)'}

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

### FETCHING DATA ###
def format_reference_code(procedure_code: str) -> str:
    match = re.match(r"(\d+)/(\d+)", procedure_code)
    if match:
        year, num = match.groups()
        return f"{year}_{int(num)}"
    return procedure_code.replace("/", "_").split("(")[0]

def fetch_timeline_from_api(procedure_code: str) -> list:
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
            timeline_tuples = []
            for item in raw_data.get("events", []):
                event_desc = item.get("type")
                raw_date = item.get("date")
                if event_desc and raw_date:
                    try:
                        parsed_date = datetime.strptime(raw_date, "%d/%m/%Y").strftime("%Y-%m-%d")
                        timeline_tuples.append((event_desc, parsed_date))
                    except ValueError:
                        continue
            if timeline_tuples:
                return timeline_tuples
    except Exception:
        pass
        
    return []

### ANALYSIS ###

def mean_EP_meeting(timeline: list) -> float:
    ep_dates = [date for event, date in timeline if any(k in event.lower() for k in ['ep', 'parliament', 'committee'])]
    if len(ep_dates) < 2:
        return 0.0
    ep_dates = [np.datetime64(date) for date in ep_dates]
    return float(np.mean(np.diff(ep_dates).astype('timedelta64[D]').astype(int)))

def mean_Trilogue_meeting(timeline: list) -> float:
    trilogue_dates = [date for event, date in timeline if "trilogue" in event.lower()]
    if len(trilogue_dates) < 2:
        return 0.0
    trilogue_dates = [np.datetime64(date) for date in trilogue_dates]
    return float(np.mean(np.diff(trilogue_dates).astype('timedelta64[D]').astype(int)))

def mean_CWP_meeting(timeline: list) -> float:
    cwp_dates = [np.datetime64(date) for event, date in timeline if "Council working party" in event]
    if len(cwp_dates) < 2:
        return 0.0
    return float(np.mean(np.diff(cwp_dates).astype('timedelta64[D]').astype(int)))

def mean_COR_meeting(timeline: list) -> float:
    cor_dates = [np.datetime64(date) for event, date in timeline if "Coreper" in event]
    if len(cor_dates) < 2:
        return 0.0
    return float(np.mean(np.diff(cor_dates).astype('timedelta64[D]').astype(int)))

def distance_last_CWP_COR_meeting(timeline: list) -> float:
    cwp_dates = [date for event, date in timeline if "Council working party" in event]
    cor_dates = [date for event, date in timeline if "Coreper" in event]
    if not cwp_dates or not cor_dates:
        return 0.0
    return abs((np.datetime64(cwp_dates[-1]) - np.datetime64(cor_dates[-1])).astype('timedelta64[D]').astype(int))

def is_urgent(timeline: list) -> bool:
    mean_cwp = mean_CWP_meeting(timeline)
    mean_cor = mean_COR_meeting(timeline)
    distance = distance_last_CWP_COR_meeting(timeline)
    return (mean_cwp <= 14 or mean_cor <= 14) and distance <= 10

### VISUALIZATION FUNCTIONS ###

def visualize_legislative_timeline(timeline_data: list, act_name: str = "", save_path: str = None) -> plt.Figure:
    """
    Genera una gráfica de la línea de tiempo legislativa.
    
    Args:
        timeline_data: Lista de tuplas (evento, fecha) 
        act_name: Nombre del acto legislativo (para el título)
        save_path: Ruta para guardar la gráfica (opcional)
    
    Returns:
        Figura de matplotlib
    """
    if not timeline_data:
        raise ValueError("No hay datos de timeline para visualizar")
    
    fig, ax = plt.subplots(figsize=(10, 5))
    
    # Preparar datos
    cwp_events = sorted([
        (datetime.strptime(date, "%Y-%m-%d"), event) 
        for event, date in timeline_data 
        if "Council working party" in event
    ], key=lambda x: x[0])
    
    cor_events = sorted([
        (datetime.strptime(date, "%Y-%m-%d"), event) 
        for event, date in timeline_data 
        if "Coreper" in event
    ], key=lambda x: x[0])
    
    ep_dates = sorted([
        datetime.strptime(date, "%Y-%m-%d") 
        for event, date in timeline_data 
        if any(k in event.lower() for k in ['ep', 'parliament', 'committee'])
    ])
    
    trilogue_dates = sorted([
        datetime.strptime(date, "%Y-%m-%d") 
        for event, date in timeline_data 
        if "trilogue" in event.lower()
    ])
    
    # Council Working Parties - línea progresiva con puntos
    if cwp_events:
        cwp_dates, _ = zip(*cwp_events)
        ax.plot(
            cwp_dates, 
            range(len(cwp_dates)), 
            marker='o', 
            label='Council Working Parties', 
            color='#003399', 
            linewidth=2, 
            alpha=0.7
        )
    
    # Coreper - línea progresiva con puntos
    if cor_events:
        cor_dates, _ = zip(*cor_events)
        ax.plot(
            cor_dates, 
            range(len(cor_dates)), 
            marker='s', 
            label='Coreper (Ambassadors)', 
            color='#F59E0B', 
            linewidth=2, 
            alpha=0.7
        )
    
    # European Parliament - líneas verticales
    for i, date in enumerate(ep_dates):
        ax.axvline(
            x=mdates.date2num(date), 
            color='#3B82F6', 
            linestyle='--', 
            linewidth=1.5, 
            alpha=0.8, 
            label='European Parliament' if i == 0 else ""
        )
    
    # Trilogues - líneas verticales
    for i, date in enumerate(trilogue_dates):
        ax.axvline(
            x=mdates.date2num(date), 
            color='#10B981', 
            linestyle='-', 
            linewidth=2.5, 
            alpha=0.9, 
            label='Trilogues (Final Deal Phase)' if i == 0 else ""
        )
    
    # Configuración de la gráfica
    title = f"Institutional Dynamics - {act_name}" if act_name else "Legislative Timeline"
    ax.set_title(title, fontsize=12, fontweight='bold', pad=15)
    ax.set_xlabel("Date", fontsize=10)
    ax.set_ylabel("Milestone Count", fontsize=10)
    ax.grid(True, linestyle='--', alpha=0.6)
    
    # Leyenda sin duplicados
    handles, labels = ax.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    ax.legend(by_label.values(), by_label.keys(), loc='upper left', frameon=True)
    
    plt.tight_layout()
    
    # Guardar si se especifica ruta
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
    
    return fig


def visualize_timeline_for_streamlit(timeline_data: list, act_name: str) -> plt.Figure:
    """
    Versión específica para Streamlit que trabaja con pandas Timestamps.
    
    Args:
        timeline_data: Lista de tuplas (evento, fecha)
        act_name: Nombre del acto legislativo
    
    Returns:
        Figura de matplotlib
    """
    if not timeline_data:
        raise ValueError("No hay datos de timeline para visualizar")
    
    fig, ax = plt.subplots(figsize=(10, 4.5))
    
    # Preparar datos usando pandas Timestamp
    cwp_dates = sorted([
        pd.to_datetime(date) 
        for event, date in timeline_data 
        if "Council working party" in event
    ])
    
    cor_dates = sorted([
        pd.to_datetime(date) 
        for event, date in timeline_data 
        if "Coreper" in event
    ])
    
    ep_dates = sorted([
        pd.to_datetime(date) 
        for event, date in timeline_data 
        if "EP" in event or "parliament" in event.lower()
    ])
    
    trilogue_dates = sorted([
        pd.to_datetime(date) 
        for event, date in timeline_data 
        if "trilogue" in event.lower()
    ])
    
    # CWP - línea con puntos
    if cwp_dates:
        ax.plot(
            cwp_dates, 
            range(len(cwp_dates)), 
            marker='o', 
            label='Council Working Parties', 
            color='#003399', 
            linewidth=2, 
            alpha=0.7
        )
    
    # Coreper - línea con puntos
    if cor_dates:
        ax.plot(
            cor_dates, 
            range(len(cor_dates)), 
            marker='s', 
            label='Coreper (Ambassadors)', 
            color='#F59E0B', 
            linewidth=2, 
            alpha=0.7
        )
    
    # EP - líneas verticales
    for i, date in enumerate(ep_dates):
        ax.axvline(
            x=date, 
            color='#3B82F6', 
            linestyle='--', 
            linewidth=1.5, 
            alpha=0.7, 
            label='European Parliament' if i == 0 else ""
        )
    
    # Trilogues - líneas verticales
    for i, date in enumerate(trilogue_dates):
        ax.axvline(
            x=date, 
            color='#10B981', 
            linestyle='-', 
            linewidth=2, 
            alpha=0.7, 
            label='Trilogues (Final Deal Phase)' if i == 0 else ""
        )
    
    ax.set_title(
        f"Institutional Dynamics - {act_name}", 
        fontsize=12, 
        fontweight='bold', 
        color='#1E293B', 
        pad=15
    )
    ax.set_xlabel("Date", fontsize=10, color='#64748b')
    ax.set_ylabel("Milestone Count", fontsize=10, color='#64748b')
    
    handles, labels = ax.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    ax.legend(by_label.values(), by_label.keys(), frameon=True, facecolor='#ffffff', edgecolor='#e2e8f0')
    
    ax.grid(True, linestyle='--', alpha=0.5, color='#cbd5e1')
    plt.xticks(rotation=30)
    plt.tight_layout()
    
    return fig


### ACTUALIZACIÓN DE run_automation() ###

def run_automation():
    """Genera reportes y gráficas para todos los actos legislativos."""
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
        
        act_summary = [
            f"Act: {act_name} ({code})",
            f"  - Mean CWP: {m_cwp:.2f} days",
            f"  - Mean Coreper: {m_cor:.2f} days",
            f"  - Distance last CWP-COREPER: {int(dist)} days",
            f"  - Urgency Alert: {urgent}",
            "",
            "  [Timeline Summary]"
        ]
        for date, event in sorted(timeline, key=lambda x: x[1]):
            act_summary.append(f"{date}: {event}")
        act_summary.append("-" * 60)
        act_summary.append("")
        
        report_lines.extend(act_summary)
        
        # Generar y guardar gráfica usando la nueva función
        safe_name = act_name.split("(")[0].strip().replace(" ", "_")
        save_path = f"output_reports/{safe_name}_{timestamp}.png"
        
        try:
            fig = visualize_legislative_timeline(
                timeline_data=timeline,
                act_name=act_name,
                save_path=save_path
            )
            plt.close(fig)  # Liberar memoria
        except Exception as e:
            print(f"Error generando gráfica para {act_name}: {e}")

    report_content = "\n".join(report_lines)
    with open(report_filename, "w", encoding="utf-8") as f:
        f.write(report_content)
        
    print(report_content)
    print(f"\n[Automation Success] Report saved to '{report_filename}' and graphs exported to 'output_reports/'.")