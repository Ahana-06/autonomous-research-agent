import os
import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

# -----------------------------------------------------------------------------
# 1. Page Setup & Styling
# -----------------------------------------------------------------------------
st.set_page_config(page_title="Autonomous Research Agent", layout="wide", page_icon="🌐")

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
# 2. Main Page / Globe & Research Agent Layout
# (All your existing 3D Globe & Dashboard logic remains here intact)
# -----------------------------------------------------------------------------


# -----------------------------------------------------------------------------
# 3. Sidebar Configuration & RAG Metrics Expander
# -----------------------------------------------------------------------------
with st.sidebar:
    # --- Your existing Sidebar Widgets (Knowledge Base, Search Mode, etc.) ---
    st.markdown("### 📚 Knowledge Base")
    st.caption("Upload PDF documents")
    # (Existing upload / ingest logic...)

    st.markdown("---")
    st.markdown("### ⚙️ Search Mode")
    # (Existing search toggle logic...)

    st.markdown("---")
    st.markdown("### 🕒 Recent Research")
    st.caption("No recent research yet.")

    # =========================================================================
    # Added: RAG Evaluation Metrics Section (Sidebar Integration)
    # =========================================================================
    st.markdown("---")
    with st.expander("📊 View RAG Metrics (Ragas)"):
        try:
            df_metrics = pd.read_csv("ragas_evaluation_results.csv")
            avg_score = df_metrics["answer_correctness"].mean()
            
            st.metric("Avg Correctness", f"{avg_score:.4f}")
            st.caption(f"Evaluated Queries: {len(df_metrics)}")
            
            # Show concise view in sidebar
            st.dataframe(
                df_metrics[["question", "answer_correctness"]], 
                use_container_width=True
            )
        except FileNotFoundError:
            st.info("Run `python eval.py` to generate evaluation metrics.")