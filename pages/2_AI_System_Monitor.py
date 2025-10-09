import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import uuid

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="AI Monitor",
    page_icon="🧠",
    layout="wide"
)

# --- SESSION STATE INITIALIZATION ---
if "sessions" not in st.session_state:
    st.session_state.sessions = {}
if "current_session_id" not in st.session_state:
    st.session_state.current_session_id = None
if "editing_session_id" not in st.session_state:
    st.session_state.editing_session_id = None

# Pre-populate dummy data for demonstration
if not st.session_state.sessions:
    st.session_state.sessions = {
        str(uuid.uuid4()): {"title": "Is GOOG a Growth Stock?"},
        str(uuid.uuid4()): {"title": "PEG Ratio Explained"},
        str(uuid.uuid4()): {"title": "Comparing KO and PEP"},
        str(uuid.uuid4()): {"title": "MSFT Intrinsic Value Analysis"} 
    }
    st.session_state.current_session_id = None

def new_chat_session():
    """Creates a new chat session."""
    session_id = str(uuid.uuid4())
    st.session_state.current_session_id = session_id
    st.session_state.sessions[session_id] = {"title": "New Chat"}
    st.session_state.editing_session_id = None

# --- SIDEBAR: CHAT HISTORY ---
with st.sidebar:
    st.header("IntrinsicAlpha AI")
    if st.button("New chat", use_container_width=True):
        new_chat_session()
        st.rerun()

    st.markdown("---")
    st.subheader("Recent")

    if st.session_state.sessions:
        for session_id, session_data in reversed(list(st.session_state.sessions.items())):
            is_active = (session_id == st.session_state.current_session_id)
            label = f"**▶ {session_data['title']}**" if is_active else session_data['title']

            # Create a horizontal layout with three columns
            col1, col2, col3 = st.columns([0.7, 0.15, 0.15])

            with col1:
                if st.button(label, key=f"load_{session_id}", use_container_width=True):
                    st.session_state.current_session_id = session_id
                    st.session_state.editing_session_id = None
                    st.rerun()

            with col2.container(border=False):
                if st.button("✏️", key=f"start_edit_{session_id}", use_container_width=True):
                    st.session_state.editing_session_id = session_id
                    st.rerun()

            with col3.container(border=False):
                if st.button("🗑️", key=f"delete_{session_id}", use_container_width=True):
                    del st.session_state.sessions[session_id]
                    if st.session_state.current_session_id == session_id:
                        st.session_state.current_session_id = None
                    st.rerun()

            # Handle the rename functionality
            if st.session_state.editing_session_id == session_id:
                new_title = st.text_input("New title", value=session_data["title"], key=f"edit_{session_id}", label_visibility="collapsed")
                if new_title and new_title != session_data["title"]:
                    st.session_state.sessions[session_id]["title"] = new_title
                    st.session_state.editing_session_id = None
                    st.rerun()

    st.markdown("---")
    
st.title("🧠 AI System Monitor")
st.markdown("A transparent look into the AI agents and their performance.")

# --- MOCK DATA GENERATION ---
@st.cache_data
def generate_monitor_data():
    # Mock data for Key Metrics
    metrics_data = {
        'Metric': ['Active Agents', 'Successful Runs', 'Average Response Time', 'Errors (24h)', 'Drift Warnings'],
        'Value': [8, 98.5, 2.3, 1, 2]
    }
    metrics_df = pd.DataFrame(metrics_data)
    
    # Mock data for Response Time chart
    response_time = np.random.normal(loc=2.5, scale=0.5, size=50)
    response_time_df = pd.DataFrame({'Timestep': np.arange(50), 'Response Time (s)': response_time})
    
    # Mock data for Drift/Accuracy
    drift_data = {'Agent': ['Valuation Agent', 'Sentiment Agent', 'Strategy Agent', 'QA Agent'],
                  'Drift Score': np.random.uniform(0.1, 0.4, 4)}
    drift_df = pd.DataFrame(drift_data)
    
    # Mock data for Recent Agent Logs
    logs_data = {
        'Timestamp': [
            '2025-10-05 10:15:30', '2025-10-05 10:12:15', '2025-10-05 10:10:05',
            '2025-10-05 10:08:45', '2025-10-05 10:05:01'
        ],
        'Agent': [
            'ValuationAgent', 'SentimentAgent', 'StrategyAgent', 'DataAgent', 'QA Agent'
        ],
        'Task': [
            'Calculate P/E Ratio', 'Analyze News Articles', 'Generate Risk Profile',
            'Fetch Market Data', 'Review Drafted Response'
        ],
        'Status': ['Success', 'Success', 'Success', 'Success', 'Warning']
    }
    logs_df = pd.DataFrame(logs_data)
    
    return metrics_df, response_time_df, drift_df, logs_df

metrics_df, response_time_df, drift_df, logs_df = generate_monitor_data()

# --- KEY METRICS ---
st.header("Key Performance Metrics")
cols = st.columns(5)
for i, row in metrics_df.iterrows():
    cols[i].metric(label=row['Metric'], value=row['Value'])

# --- AI INSIGHT BOX ---
st.markdown("---")
st.subheader("AI System Insight")
with st.container(border=True):
    st.info("ValuationAgent drift detected; retraining recommended. The latest financial data may have introduced new patterns not seen during initial training. All other agents are performing within acceptable parameters.")

# --- VISUALIZATIONS ---
st.markdown("---")
st.subheader("System Performance Over Time")
col_chart1, col_chart2 = st.columns(2)
with col_chart1:
    fig_time = px.line(
        response_time_df,
        x='Timestep',
        y='Response Time (s)',
        title='Response Time Over Last 50 Runs',
        markers=True,
        color_discrete_sequence=['#4299E1']
    )
    st.plotly_chart(fig_time, use_container_width=True)

with col_chart2:
    fig_drift = px.bar(
        drift_df,
        x='Agent',
        y='Drift Score',
        title='Agent Drift Scores',
        color_discrete_sequence=['#4299E1']
    )
    st.plotly_chart(fig_drift, use_container_width=True)
    
# --- RECENT LOGS TABLE ---
st.markdown("---")
st.subheader("Recent Agent Logs")
st.dataframe(logs_df, use_container_width=True)