import streamlit as st
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import sys
import os

import eu

# Page configuration
st.set_page_config(
    page_title="EU Regulatory Intelligence", 
    page_icon="🇪🇺", 
    layout="wide"
)

# 🎨 CUSTOM CSS INJECTION (Professional RegTech & Civic Tech Design)
st.markdown("""
    <style>
    /* General style for metric containers and cards */
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
    /* Tab headers styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #ffffff;
        border-radius: 6px 6px 0px 0px;
        padding: 10px 20px;
        border: 1px solid #e2e8f0;
    }
    /* Subtitle / slogan styling */
    .slogan-box {
        margin-bottom: 25px;
        color: #64748b;
        font-size: 1.1rem;
        font-style: italic;
    }
    </style>
""", unsafe_allow_html=True)

# Main Header with brand identity
st.title("🇪🇺 EU Regulatory Intelligence Dashboard")
st.markdown('<p class="slogan-box">"Is the EU actually doing that?" — Real-time automated tracking and civic transparency analysis.</p>', unsafe_allow_html=True)

# Sidebar Control Panel
st.sidebar.header("⚙️ Control Panel")
selected_name = st.sidebar.selectbox("Select a Legislative Act:", list(eu.act_tracker.keys()))
procedure_code = eu.act_tracker[selected_name]

# Button to force network refresh
if st.sidebar.button("🔄 Live Data Refresh", use_container_width=True):
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.info("💡 **Tip:** Use the button above to fetch fresh data directly from the official EU Law Tracker.")

st.subheader(f"{selected_name} (`{procedure_code}`)")

# Fetch data using eu.py function (with built-in automatic fallback)
with st.spinner("Querying the official EU API (with local fallback)..."):
    timeline_data = eu.fetch_timeline_from_api(procedure_code)
    if not timeline_data:
        timeline_data = eu.fallback_timelines.get(selected_name, [])

if timeline_data:
    st.success(f"Successfully loaded {len(timeline_data)} legislative milestones!")
    
    # Calculate advanced metrics using eu.py functions
    m_cwp = eu.mean_CWP_meeting(timeline_data)
    m_cor = eu.mean_COR_meeting(timeline_data)
    dist = eu.distance_last_CWP_COR_meeting(timeline_data)
    urgent = eu.is_urgent(timeline_data)
    
    # Display metrics in Streamlit columns with enhanced design
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Milestones", len(timeline_data))
    col2.metric("Mean CWP Gap", f"{m_cwp:.1f} days")
    col3.metric("Mean Coreper Gap", f"{m_cor:.1f} days")
    col4.metric("Active Urgency", "YES 🚨" if urgent else "NO 🟢")

    # Visual spacer
    st.write("")

    # 📖 CIVIC CONTEXT / GLOSSARY EXPANDER
    with st.expander("📖 What do these Brussels terms mean?"):
        st.markdown("""
        - **Council Working Party (CWP):** Technical groups where national diplomats dissect the proposal line by line.
        - **Coreper:** Committee of Permanent Representatives (Ambassadors). They iron out political deals before ministerial votes.
        - **European Parliament (EP):** The directly elected house representing citizens, adopting committee reports and plenary resolutions.
        - **Trilogues:** Informal negotiations between Parliament, Council, and Commission. *When trilogues accelerate, a final deal is near.*
        - **Active Urgency Alert:** Calculated automatically based on meeting cadences and clustering.
        """)

    st.write("")

    # Process data into a DataFrame for visualizations
    df_timeline = pd.DataFrame(timeline_data, columns=["Legislative Milestone", "Date"])
    df_timeline["Fecha_dt"] = pd.to_datetime(df_timeline["Date"])
    df_timeline = df_timeline.sort_values("Fecha_dt")
    
    latest_event = df_timeline.iloc[-1]
    
    # Build the analytical markdown report
    markdown_report = f"""### 📝 Regulatory Intelligence & Civic Report

- **Dossier Code:** `{procedure_code}` - {selected_name}
- **Latest Recorded Milestone:** {latest_event['Legislative Milestone']} 
- **Date of Last Movement:** {latest_event['Date']}
- **Urgency Alert:** {'[YES] (High meeting frequency)' if urgent else '[NO] (Standard pace)'}

---

#### 🔍 Pipeline Technical Analysis
- **Mean time between CWP meetings:** {m_cwp:.2f} days
- **Mean time between Coreper meetings:** {m_cor:.2f} days
- **Recent CWP-Coreper distance:** {int(dist)} days
"""

    # Organize content into interactive tabs
    tab_reporte, tab_tabla, tab_grafica = st.tabs(["📄 Analytical Report (MD)", "📅 Timeline", "📊 Temporal Chart"])
    
    with tab_reporte:
        st.markdown("### Executive Summary & Conclusions")
        st.markdown(markdown_report)
        st.download_button(
            label="📥 Download Report as Markdown",
            data=markdown_report,
            file_name=f"report_{procedure_code.replace('/', '_')}.md",
            mime="text/markdown"
        )
        
    with tab_tabla:
        st.markdown("### 📅 Act Chronology")
        st.dataframe(df_timeline[["Legislative Milestone", "Date"]], use_container_width=True, hide_index=True)
        
    with tab_grafica:
        st.markdown("### 📊 Full Legislative Lifecycle Progression")
        
        try:
            # Usar la nueva función de visualización
            fig = eu.visualize_timeline_for_streamlit(
                timeline_data=timeline_data,
                act_name=selected_name
            )
            st.pyplot(fig)
            plt.close(fig)  # Liberar memoria
        except Exception as e:
            st.error(f"Error al generar la gráfica: {e}")
else:
    st.warning("⚠️ Could not retrieve data for this dossier.")