import streamlit as st
import pandas as pd

st.set_page_config(page_title="RAG Evaluation Metrics", page_icon="📊", layout="wide")

st.title("📊 RAG Evaluation Metrics (Ragas)")
st.write("Performance metrics evaluating the correctness of the RAG retrieval pipeline.")

try:
    df_metrics = pd.read_csv("ragas_evaluation_results.csv")
    avg_score = df_metrics["answer_correctness"].mean()
    
    col1, col2 = st.columns(2)
    col1.metric("Average Answer Correctness", f"{avg_score:.4f}")
    col2.metric("Evaluated Queries", len(df_metrics))
    
    st.divider()
    st.subheader("Detailed Evaluation Breakdown")
    st.dataframe(df_metrics, use_container_width=True)
except FileNotFoundError:
    st.info("Evaluation metrics file not found. Run `python eval.py` to generate results.")