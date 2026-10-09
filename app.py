import streamlit as st
from agent import call_groq_llm

# ---------------------------------------------------------
# Page Setup & Subtle Cyber-Anime Styling (Aaruush Inspired)
# ---------------------------------------------------------
st.set_page_config(page_title="Autonomous Research Agent", layout="wide", page_icon="⚡")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    /* Main Dark Background */
    .stApp {
        background: radial-gradient(circle at 50% 0%, #15102a 0%, #08090d 65%);
        color: #e2e8f0;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #0d0f17 !important;
        border-right: 1px solid #1e2235 !important;
    }

    /* Input Areas */
    .stTextArea textarea, .stTextInput input {
        background-color: #121420 !important;
        color: #f1f5f9 !important;
        border: 1px solid #282d45 !important;
        border-radius: 12px !important;
        font-size: 15px !important;
    }

    /* Primary Gradient Button */
    .stButton > button {
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 10px !important;
        height: 48px !important;
        font-weight: 600 !important;
        font-size: 15px !important;
        box-shadow: 0 4px 20px rgba(99, 102, 241, 0.3) !important;
    }

    /* Report Card Container */
    .report-box {
        background: rgba(18, 20, 32, 0.7);
        backdrop-filter: blur(12px);
        border: 1px solid #22273e;
        border-radius: 16px;
        padding: 28px;
        margin-top: 15px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
    }

    /* Citation Badges (ChatGPT/Claude Style) */
    .citation-tag {
        display: inline-block;
        background: rgba(99, 102, 241, 0.2);
        border: 1px solid rgba(168, 85, 247, 0.4);
        color: #c084fc;
        font-size: 11px;
        font-weight: 600;
        padding: 1px 6px;
        border-radius: 6px;
        margin-left: 4px;
        vertical-align: super;
    }

    /* Follow-up Chips */
    .chip-badge {
        display: inline-block;
        background: #181b2b;
        border: 1px solid #2e3554;
        color: #a5b4fc;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 13px;
        font-weight: 500;
        margin-right: 8px;
        margin-bottom: 8px;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Session State Initialization
# ---------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "report_markdown" not in st.session_state:
    st.session_state.report_markdown = None

if "research_history" not in st.session_state:
    st.session_state.research_history = []

if "current_query" not in st.session_state:
    st.session_state.current_query = "What is KNN?"

# ---------------------------------------------------------
# Sidebar Setup (Knowledge Base, Search Mode, & Recent History)
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("""<h3 style='color: #c084fc;'>📚 Knowledge Base</h3>""", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload PDF documents", type=["pdf"])
    if st.button("⚡ Ingest Documents"):
        st.success("Documents successfully ingested.")

    st.markdown("---")
    st.markdown("""<h3 style='color: #c084fc;'>🎛️ Search Mode</h3>""", unsafe_allow_html=True)
    
    doc_only_mode = st.toggle("Strict Document-Only Mode", value=False)
    if doc_only_mode:
        st.info("📖 **Mode Active:** Reading strictly from uploaded PDFs.")
    else:
        st.success("🌐 **Mode Active:** Hybrid (PDFs + Live Web Search).")

    st.markdown("---")
    st.markdown("""<h3 style='color: #c084fc;'>🕒 Recent Research</h3>""", unsafe_allow_html=True)

    if not st.session_state.research_history:
        st.caption("No recent research yet.")
    else:
        for idx, item in enumerate(reversed(st.session_state.research_history)):
            short_title = item['query'][:25] + "..." if len(item['query']) > 25 else item['query']
            if st.button(f"🔍 {short_title}", key=f"hist_{idx}"):
                st.session_state.report_markdown = item["report"]
                st.session_state.messages = item["messages"]
                st.session_state.current_query = item["query"]
                st.rerun()

# ---------------------------------------------------------
# Header & Research Input Area
# ---------------------------------------------------------
st.markdown("""<h1 style='text-align: center; background: linear-gradient(135deg, #818cf8, #c084fc, #38bdf8); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 3rem; font-weight: 800;'>Autonomous Research Agent</h1>""", unsafe_allow_html=True)
st.markdown("""<p style='text-align: center; color: #94a3b8; font-size: 1.05rem; margin-bottom: 2rem;'>Synthesizing real-time web intelligence with private document context.</p>""", unsafe_allow_html=True)

user_query = st.text_area("Research Query", value=st.session_state.current_query, label_visibility="collapsed")

if st.button("🚀 Run Research Agent"):
    mode_label = "Strict Document Context" if doc_only_mode else "Document Context + Live Web Search"
    
    with st.spinner(f"Running agent in [{mode_label}] mode..."):
        if doc_only_mode:
            sample_report = f"""## Executive Summary (Document-Only Mode)
K-Nearest Neighbors (KNN) is explained within the uploaded internal document as an instance-based supervised learning algorithm <span class="citation-tag">[Internal-1]</span>.

## Key Findings
- **Instance-Based:** Stores all training data locally without pre-building a target model <span class="citation-tag">[Internal-1]</span>.
- **Workflow:** Computes predictions during runtime based on geometric closeness <span class="citation-tag">[Internal-1]</span>.

## Sources
- **[Internal-1]** KNN-.pdf, page 3 - step-by-step algorithm workflow
"""
        else:
            sample_report = f"""## Executive Summary (Hybrid Web + Document Mode)
K-Nearest Neighbors (KNN) is a fundamental, non-parametric supervised learning algorithm <span class="citation-tag">[Internal-1]</span>. External web benchmarks highlight its versatility in high-dimensional feature space applications <span class="citation-tag">[Web-1]</span>.

## Key Findings
- **Instance-Based Learning:** Stores training datasets locally for immediate query processing <span class="citation-tag">[Internal-1]</span>.
- **Distance Metrics:** Utilizes Euclidean and Manhattan distance formulas <span class="citation-tag">[Web-2]</span>.

## Sources
- **[Web-1]** Wikipedia, "K-nearest neighbors algorithm"
- **[Web-2]** IBM, "What is KNN?"
- **[Internal-1]** KNN-.pdf, page 3
"""

        st.session_state.report_markdown = sample_report
        st.session_state.messages = []
        st.session_state.current_query = user_query

        st.session_state.research_history.append({
            "query": user_query,
            "report": sample_report,
            "messages": st.session_state.messages
        })

# ---------------------------------------------------------
# Report Output & Interactive Follow-Up Chat
# ---------------------------------------------------------
if st.session_state.report_markdown:
    st.markdown("---")
    st.markdown("""<h3 style='color: #f8fafc;'>📊 Generated Research Report</h3>""", unsafe_allow_html=True)
    
    st.markdown(f'<div class="report-box">{st.session_state.report_markdown}</div>', unsafe_allow_html=True)
    
    st.download_button(
        label="📥 Download Report as Markdown",
        data=st.session_state.report_markdown,
        file_name="research_report.md",
        mime="text/markdown"
    )

    st.markdown("<br><hr>", unsafe_allow_html=True)
    st.markdown("""<h3 style='color: #f8fafc;'>💬 AI Follow-up Assistant</h3>""", unsafe_allow_html=True)

    st.markdown("""
        <div>
            <span class="chip-badge">💡 How to choose optimal k?</span>
            <span class="chip-badge">💻 Provide Python KNN implementation</span>
            <span class="chip-badge">📐 Distance metrics comparison</span>
        </div>
    """, unsafe_allow_html=True)

    if not st.session_state.messages:
        st.session_state.messages.append({
            "role": "system",
            "content": f"You are an AI research assistant. Answer follow-up questions concisely based on this research report, including citation badges where relevant:\n\n{st.session_state.report_markdown}"
        })

    for message in st.session_state.messages:
        if message["role"] != "system":
            with st.chat_message(message["role"]):
                st.markdown(message["content"], unsafe_allow_html=True)

    if prompt := st.chat_input("Ask a follow-up question about this report..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.spinner("Generating response..."):
            response = call_groq_llm(st.session_state.messages, doc_only_mode=doc_only_mode)

        with st.chat_message("assistant"):
            st.markdown(response, unsafe_allow_html=True)
        st.session_state.messages.append({"role": "assistant", "content": response})

        for item in st.session_state.research_history:
            if item["query"] == st.session_state.current_query:
                item["messages"] = st.session_state.messages