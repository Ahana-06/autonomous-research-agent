import os
import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

# -----------------------------------------------------------------------------
# 1. Page Setup & Styling
# -----------------------------------------------------------------------------
st.set_page_config(page_title="Autonomous Research Agent", layout="wide", page_icon="s")

if "dashboard_unlocked" not in st.session_state:
    st.session_state.dashboard_unlocked = False

if "custom_globe_particles" not in st.session_state:
    st.session_state.custom_globe_particles = 2600

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    .stApp {
        background: radial-gradient(circle at 50% 0%, #15102a 0%, #08090d 65%);
        color: #e2e8f0;
    }

    section[data-testid="stSidebar"] {
        background-color: #0d0f17 !important;
        border-right: 1px solid #1e2235 !important;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Your Original App Code & Structure Goes Here
# (Preserving all your existing widgets and logic)
# -----------------------------------------------------------------------------

# =============================================================================
# Added: RAG Evaluation Metrics Section (Safely appended at the bottom)
# =============================================================================
st.markdown("---")
with st.expander("📊 View RAG Correctness Evaluation Metrics (Ragas)"):
    st.write("Performance metrics evaluating the correctness of the RAG retrieval pipeline:")
    try:
        df_metrics = pd.read_csv("ragas_evaluation_results.csv")
        avg_score = df_metrics["answer_correctness"].mean()
        
        col1, col2 = st.columns(2)
        col1.metric("Average Answer Correctness", f"{avg_score:.4f}")
        col2.metric("Evaluated Queries", len(df_metrics))
        
        st.dataframe(df_metrics, use_container_width=True)
    except FileNotFoundError:
        st.info("Evaluation metrics file not found. Run `python eval.py` to generate results.")