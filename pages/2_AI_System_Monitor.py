import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import uuid
import plotly.graph_objects as go
import random

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="AI Monitor",
    page_icon="🧠",
    layout="wide"
)

# --- SESSION STATE INITIALIZATION (SIDEBAR) ---
if "sessions" not in st.session_state:
    st.session_state.sessions = {}
if "current_session_id" not in st.session_state:
    st.session_state.current_session_id = None
if "editing_session_id" not in st.session_state:
    st.session_state.editing_session_id = None

# Pre-populate dummy sessions for demonstration
if not st.session_state.sessions:
    st.session_state.sessions = {
        str(uuid.uuid4()): {"title": "Is GOOG a Growth Stock?"},
        str(uuid.uuid4()): {"title": "PEG Ratio Explained"},
        str(uuid.uuid4()): {"title": "Comparing KO and PEP"},
        str(uuid.uuid4()): {"title": "MSFT Intrinsic Value Analysis"}
    }
    st.session_state.current_session_id = None

def new_chat_session():
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

            col1, col2, col3 = st.columns([0.7, 0.15, 0.15])
            with col1:
                if st.button(label, key=f"load_{session_id}", use_container_width=True):
                    st.session_state.current_session_id = session_id
                    st.session_state.editing_session_id = None
                    st.rerun()
            with col2:
                if st.button("✏️", key=f"start_edit_{session_id}", use_container_width=True):
                    st.session_state.editing_session_id = session_id
                    st.rerun()
            with col3:
                if st.button("🗑️", key=f"delete_{session_id}", use_container_width=True):
                    del st.session_state.sessions[session_id]
                    if st.session_state.current_session_id == session_id:
                        st.session_state.current_session_id = None
                    st.rerun()

            if st.session_state.editing_session_id == session_id:
                new_title = st.text_input("New title", value=session_data["title"], key=f"edit_{session_id}", label_visibility="collapsed")
                if new_title and new_title != session_data["title"]:
                    st.session_state.sessions[session_id]["title"] = new_title
                    st.session_state.editing_session_id = None
                    st.rerun()


# --- MOCK DATA GENERATION ---
@st.cache_data
def generate_monitor_data():
    # High-level KPIs
    kpis = {
        'Total Traces': 4234,
        'Total Tokens': 3090,
        'Latency P99': 5.41,
        'Hallucination': 0.05,
        'QA Correctness': 0.92,
        'Relevance': 0.86,
        'Average Path Length': 3,
        'Optimal Path Length': 2
    }

    # Evaluation results dataframe
    eval_df = pd.DataFrame({
        "Evaluation": ["Router Correctness", "SQL Generation", "Analysis Clarity", "Code Runnable"],
        "Score (%)": [90, 85, 95, 100],
        "Explanation": [
            "LLM correctly chose the right tool for most queries.",
            "Some SQL queries were semantically incorrect, requiring a retry.",
            "The final responses were clear and coherent.",
            "All generated Python code was syntactically correct."
        ]
    })

    # Response Time Chart data
    response_time = np.random.normal(loc=4.5, scale=1.0, size=50)
    response_time_df = pd.DataFrame({'Run Index': np.arange(50), 'Response Time (s)': response_time})
    
    # Evaluation scores chart data
    eval_scores_data = {
        'Evaluation': ["Router Correctness", "Hallucination", "Relevance", "QA Correctness"],
        'Score': [0.92, 0.05, 0.86, 0.95],
        'Color': ['#28a745', '#dc3545', '#ffc107', '#17a2b8']
    }
    eval_scores_df = pd.DataFrame(eval_scores_data)

    # Logs data (traces)
    logs_data = {
        'Timestamp': ['2025-10-05 10:15:30', '2025-10-05 10:12:15', '2025-10-05 10:10:05',
                      '2025-10-05 10:08:45', '2025-10-05 10:05:01'],
        'Kind': ['chain', 'tool', 'chain', 'tool', 'agent'],
        'Name': ['query', 'lookup_sales_data', 'synthesize', 'execute_sql_query', 'AgentRun'],
        'Input': ['What is the purpose of...?', 'SELECT * FROM...', 'The purpose of...', 'SQL query result', 'Which stores did the best...?'],
        'Output': ['The purpose is to...', 'pd.DataFrame result...', 'Final response...', 'Success', 'Final response...'],
        'Latency (s)': [4.70, 0.14, 4.54, 0.55, 9.40]
    }
    logs_df = pd.DataFrame(logs_data)
    
    # Mock data for Traces and Tokens per Agent
    agents = ['Valuation Agent', 'Sentiment Agent', 'Strategy Agent', 'Data Agent', 'QA Agent']
    traces_per_agent = [random.randint(50, 200) for _ in agents]
    tokens_per_agent = [traces * random.randint(10, 50) for traces in traces_per_agent]
    
    traces_tokens_df = pd.DataFrame({
        'Agent': agents,
        'Traces': traces_per_agent,
        'Tokens': tokens_per_agent
    })

    # Mock data for model drift
    drift_warnings = {
        'model_name': ['Valuation Model', 'Sentiment Model'],
        'drift_score': [0.15, 0.10],
        'threshold': [0.12, 0.10],
    }
    
    return kpis, eval_df, response_time_df, eval_scores_df, logs_df, traces_tokens_df, drift_warnings

kpis, eval_df, response_time_df, eval_scores_df, logs_df, traces_tokens_df, drift_warnings = generate_monitor_data()

# --- HEADER ---
st.title("🧠 AI System Monitor")
st.markdown("A transparent, real-time view into your AI agents, their performance, and actionable alerts.")
st.markdown("---")

# --- AI AGENT SCORECARD ---
st.header("AI Agent Scorecard")

kpi_cols = st.columns(6)

kpi_cols[0].metric(label="Total Traces", value=kpis['Total Traces'], help="The total number of requests processed by the system.")
kpi_cols[1].metric(label="Total Tokens", value=kpis['Total Tokens'], help="The total number of LLM tokens used.")
kpi_cols[2].metric(label="Latency P99", value=f"{kpis['Latency P99']:.2f}s", help="The latency below which 99% of all requests fell. A value over 5 seconds may indicate a performance bottleneck.")
kpi_cols[3].metric(label="QA Correctness", value=f"{kpis['QA Correctness']:.0%}", help="The percentage of times the agent's output was correct on a test set.")
kpi_cols[4].metric(label="Relevance", value=f"{kpis['Relevance']:.0%}", help="The percentage of times the agent's output was relevant to the query.")
kpi_cols[5].metric(label="Average Path Length", value=f"{kpis['Average Path Length']}", help=f"The average number of steps the agent took to solve a problem. The optimal path is {kpis['Optimal Path Length']} steps.")

st.markdown("---")

# --- AI SUMMARY SECTION ---
st.header("AI System Summary")
with st.container(border=True):
    st.markdown("A quick overview of system health and key insights derived from the metrics.")
    st.info(f"""
        **Overall System Status:** The system is **stable** with some areas for optimization.
        
        ⚠️ **Drift Warning:** Drift detected in the **Valuation Model** and the **Sentiment Model**.

        - The P99 latency of {kpis['Latency P99']:.2f}s is higher than the recommended benchmark, which could lead to a degraded user experience under high load.
        - The average path length of {kpis['Average Path Length']} is greater than the optimal {kpis['Optimal Path Length']}, suggesting inefficiencies in the agent's decision-making flow.
        """)

st.markdown("---")

# --- EVALUATION RESULTS ---
st.subheader("Evaluation Results")
st.markdown("LLM-as-a-judge and code-based evaluators assess agent components on a test set.")
st.dataframe(eval_df, use_container_width=True)

# --- SYSTEM PERFORMANCE CHARTS ---
st.markdown("---")
st.subheader("System Performance Over Time")
col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    fig_time = px.line(
        response_time_df,
        x='Run Index',
        y='Response Time (s)',
        title='Response Time Over Last 50 Runs',
        markers=True,
        color_discrete_sequence=['#2563EB']
    )
    fig_time.update_layout(
        yaxis_title="Seconds",
        xaxis_title="Run Index",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=12)
    )
    st.plotly_chart(fig_time, use_container_width=True)

with col_chart2:
    fig_eval_scores = px.bar(
        eval_scores_df,
        x='Evaluation',
        y='Score',
        title='Evaluation Scores by Type',
        color='Color',
        color_discrete_map={
            '#28a745': '#28a745',
            '#dc3545': '#dc3545',
            '#ffc107': '#ffc107',
            '#17a2b8': '#17a2b8'
        },
        range_y=[0, 1]
    )
    fig_eval_scores.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=12),
        showlegend=False 
    )
    st.plotly_chart(fig_eval_scores, use_container_width=True)

# --- TRACES & TOKENS PER AGENT ---
st.markdown("---")
st.subheader("Traces and Tokens per Agent")
st.markdown("Visualize the workload distribution across different AI agents.")
traces_tokens_col = st.columns([0.5, 0.5])
with traces_tokens_col[0]:
    fig_traces = px.bar(
        traces_tokens_df,
        x='Agent',
        y='Traces',
        title='Traces per Agent',
        color_discrete_sequence=['#1D4ED8']
    )
    fig_traces.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=12)
    )
    st.plotly_chart(fig_traces, use_container_width=True)

with traces_tokens_col[1]:
    fig_tokens = px.bar(
        traces_tokens_df,
        x='Agent',
        y='Tokens',
        title='Tokens per Agent',
        color_discrete_sequence=['#1D4ED8']
    )
    fig_tokens.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=12)
    )
    st.plotly_chart(fig_tokens, use_container_width=True)


# --- RECENT LOGS ---
st.markdown("---")
st.subheader("📋 Recent Agent Logs (Traces)")
st.markdown("A detailed, step-by-step log of the agent's decision-making process for the last few runs.")
st.dataframe(logs_df, use_container_width=True)
st.markdown("---")