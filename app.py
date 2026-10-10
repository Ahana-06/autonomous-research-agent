"""
RAGtective - Streamlit dashboard for the autonomous research agent.

Run with:  streamlit run app.py
"""
import html
import os
import tempfile

import streamlit as st

import config
from ingestion import build_vectorstore
from tools import reset_vectorstore_cache
from agent import stream_research, get_llm

st.set_page_config(page_title="RAGtective", layout="wide", page_icon="🔎")

# ==========================================================================
# Design system: cockpit / HUD console. Black canvas, scanlines, bracket-
# framed panels, futuristic display type, mono readouts.
# ==========================================================================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@600;800&family=Rajdhani:wght@500;600&family=JetBrains+Mono:wght@400;500&display=swap');

    :root {
        --black: #030404;
        --panel: #0A0C0B;
        --hud: #39FF88;
        --hud-dim: #1F8A54;
        --amber: #FFB000;
        --text: #E6F2EA;
        --muted: #7A8C82;
    }

    .stApp {
        background:
            repeating-linear-gradient(0deg, rgba(57,255,136,0.025) 0px,
                rgba(57,255,136,0.025) 1px, transparent 1px, transparent 3px),
            radial-gradient(ellipse 1000px 600px at 50% -10%, rgba(57,255,136,0.07), transparent 60%),
            var(--black);
    }
    html, body, [class*="css"] { font-family: 'Rajdhani', sans-serif; color: var(--text); }

    .hero-wrap { text-align: center; padding: 2rem 0 1.5rem 0; }
    .hero-title {
        font-family: 'Orbitron', sans-serif; font-weight: 800; font-size: 2.6rem;
        letter-spacing: 0.12em; color: var(--hud);
        text-shadow: 0 0 14px rgba(57,255,136,0.45); margin-bottom: 0.5rem;
    }
    .hero-sub {
        font-family: 'JetBrains Mono', monospace; color: var(--muted);
        font-size: 0.85rem; letter-spacing: 0.03em; max-width: 560px; margin: 0 auto;
    }
    .hero-tag {
        display: inline-block; font-family: 'JetBrains Mono', monospace;
        font-size: 0.7rem; letter-spacing: 0.15em; color: var(--hud-dim);
        border: 1px solid var(--hud-dim); padding: 0.15rem 0.6rem;
        border-radius: 2px; margin-bottom: 0.8rem;
    }
    h1, h2, h3 {
        font-family: 'Rajdhani', sans-serif !important; font-weight: 600 !important;
        color: var(--text) !important; letter-spacing: 0.02em;
    }

    section[data-testid="stSidebar"] {
        background-color: var(--panel); border-right: 1px solid var(--hud-dim);
    }
    section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] h3 {
        font-family: 'JetBrains Mono', monospace !important; font-size: 0.85rem !important;
        letter-spacing: 0.08em; color: var(--hud) !important;
    }

    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: var(--panel) !important; border: 1px solid var(--hud-dim) !important;
        border-radius: 2px !important; position: relative; padding: 0.5rem;
    }
    div[data-testid="stVerticalBlockBorderWrapper"]::before,
    div[data-testid="stVerticalBlockBorderWrapper"]::after {
        content: ""; position: absolute; width: 14px; height: 14px;
        border-color: var(--hud); border-style: solid; border-width: 0;
    }
    div[data-testid="stVerticalBlockBorderWrapper"]::before {
        top: -1px; left: -1px; border-top-width: 2px; border-left-width: 2px;
    }
    div[data-testid="stVerticalBlockBorderWrapper"]::after {
        bottom: -1px; right: -1px; border-bottom-width: 2px; border-right-width: 2px;
    }

    .stTextArea textarea, .stTextInput input {
        background: var(--panel) !important; border: 1px solid var(--hud-dim) !important;
        border-radius: 2px !important; color: var(--text) !important;
        font-family: 'JetBrains Mono', monospace !important; font-size: 0.95rem !important;
    }
    .stTextArea textarea:focus, .stTextInput input:focus {
        border: 1px solid var(--hud) !important; box-shadow: 0 0 10px rgba(57,255,136,0.35) !important;
    }
    div[data-baseweb="select"] > div {
        background: var(--panel) !important; border: 1px solid var(--hud-dim) !important;
        border-radius: 2px !important;
    }
    section[data-testid="stFileUploaderDropzone"] {
        background: var(--panel); border: 1px dashed var(--hud-dim); border-radius: 2px;
    }

    .stButton > button {
        font-family: 'JetBrains Mono', monospace; font-weight: 500;
        letter-spacing: 0.06em; text-transform: uppercase; border-radius: 2px;
        border: 1px solid var(--hud);
    }
    .stButton > button[kind="primary"] { background-color: var(--hud); color: #030404; }
    .stButton > button[kind="primary"]:hover {
        background-color: var(--amber); border-color: var(--amber); color: #030404;
    }
    .stButton > button[kind="secondary"] { background: transparent; color: var(--hud); }
    .stButton > button[kind="secondary"]:hover { background: rgba(57,255,136,0.12); }
    .stDownloadButton > button {
        border-radius: 2px; border: 1px solid var(--amber); color: var(--amber);
        background: transparent; font-family: 'JetBrains Mono', monospace;
        letter-spacing: 0.06em; text-transform: uppercase;
    }
    .stDownloadButton > button:hover { background: var(--amber); color: #030404; }

    hr { border-top: 1px solid var(--hud-dim); }

    .trace-tool {
        font-family: 'JetBrains Mono', monospace; font-size: 0.85rem;
        border-left: 2px solid var(--hud); padding: 0.4rem 0 0.4rem 0.8rem;
        margin: 0.4rem 0; color: var(--text);
    }
    .trace-tool .tool-name { color: var(--hud); font-weight: 600; }
    .trace-result {
        font-family: 'JetBrains Mono', monospace; border-left: 2px solid var(--amber);
        padding: 0.4rem 0 0.4rem 0.8rem; margin: 0.4rem 0 0.9rem 0;
        color: var(--muted); font-size: 0.78rem;
    }
    .trace-result pre {
        background: var(--panel); border: 1px solid var(--hud-dim);
        border-radius: 2px; font-size: 0.75rem; white-space: pre-wrap;
    }
    .followup-title {
        font-family: 'JetBrains Mono', monospace; color: var(--hud);
        letter-spacing: 0.08em; font-size: 0.95rem; margin: 1.2rem 0 0.2rem 0;
    }
    .followup-sub { color: var(--muted); font-size: 0.9rem; margin-bottom: 0.6rem; }

    footer {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero-wrap">
        <div class="hero-tag">CASE FILE SYSTEM // ONLINE</div><br/>
        <div class="hero-title">🔎 RAGTECTIVE</div>
        <div class="hero-sub">STATE THE CASE. AGENT CROSS-EXAMINES PRIVATE
        DOCUMENTS + LIVE WEB. EVERY CLUE CITED.</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# --------------------------------------------------------------------------
# Session state
# --------------------------------------------------------------------------
st.session_state.setdefault("report", None)
st.session_state.setdefault("report_question", "")
st.session_state.setdefault("chat", [])  # [{"role": "user"|"assistant", "content": str}]

# --------------------------------------------------------------------------
# Sidebar: LLM provider + knowledge base setup
# --------------------------------------------------------------------------
PROVIDER_INFO = {
    "groq": ("GROQ_API_KEY", "Free key: console.groq.com/keys"),
    "google": ("GOOGLE_API_KEY", "Free key: aistudio.google.com/apikey"),
    "ollama": (None, "No key needed - run `ollama serve` locally first."),
    "anthropic": ("ANTHROPIC_API_KEY", "Paid: console.anthropic.com"),
}

with st.sidebar:
    st.markdown("### SYSTEM SETUP")

    provider = st.selectbox(
        "LLM provider",
        options=list(PROVIDER_INFO.keys()),
        index=list(PROVIDER_INFO.keys()).index(config.LLM_PROVIDER)
        if config.LLM_PROVIDER in PROVIDER_INFO else 0,
        help="Groq and Google both have free tiers; Ollama is free and fully local.",
    )
    os.environ["LLM_PROVIDER"] = provider
    config.LLM_PROVIDER = provider  # get_llm() reads config, not the environment
    env_var, hint = PROVIDER_INFO[provider]
    st.caption(hint)

    # Keys come from .env (local) or Streamlit Secrets (cloud) - never from
    # this UI. Silent when fine; warns only if something required is missing.
    if env_var and not os.getenv(env_var):
        st.error(f"{env_var} is missing. Add it to .env (or Streamlit Secrets).", icon="⚠️")
    if not os.getenv("TAVILY_API_KEY"):
        st.error("TAVILY_API_KEY is missing. Add it to .env (or Streamlit Secrets).", icon="⚠️")

    st.divider()
    st.markdown("### EVIDENCE LOCKER")
    uploaded_files = st.file_uploader(
        "Upload PDF documents", type=["pdf"], accept_multiple_files=True
    )
    if st.button("Log evidence", disabled=not uploaded_files, type="primary"):
        with st.spinner("Chunking, embedding, and indexing..."):
            tmp_paths = []
            for f in uploaded_files:
                tmp_path = os.path.join(tempfile.gettempdir(), f.name)
                with open(tmp_path, "wb") as out:
                    out.write(f.getbuffer())
                tmp_paths.append(tmp_path)
            try:
                _, n_chunks = build_vectorstore(tmp_paths)
                reset_vectorstore_cache()
                st.session_state["kb_ready"] = True
                st.success(f"Indexed {n_chunks} chunks from {len(tmp_paths)} document(s).")
            except Exception as exc:
                st.error(f"Ingestion failed: {exc}")

    if st.session_state.get("kb_ready"):
        st.caption("EVIDENCE LOCKER: READY")
    else:
        st.caption("EVIDENCE LOCKER: EMPTY — running on web search only.")


def answer_followup(report: str, history: list, user_msg: str) -> str:
    """Answer a follow-up question using the finished report as context."""
    from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

    system = (
        "You are a research assistant. Answer the user's follow-up questions "
        "using the research report below. Be concise. If the report does not "
        "cover the question, say so briefly instead of inventing facts.\n\n"
        "REPORT:\n" + report[:6000]
    )
    msgs = [SystemMessage(content=system)]
    for h in history[-6:]:
        cls = HumanMessage if h["role"] == "user" else AIMessage
        msgs.append(cls(content=h["content"]))
    msgs.append(HumanMessage(content=user_msg))
    return get_llm().invoke(msgs).content


# --------------------------------------------------------------------------
# Main: state the case
# --------------------------------------------------------------------------
_, center_col, _ = st.columns([1, 4, 1])
with center_col:
    question = st.text_area(
        "Research topic or question",
        placeholder=(
            "e.g. What are the latest advances in solid-state battery energy "
            "density, and how do they compare to our internal R&D benchmarks?"
        ),
        height=110,
        label_visibility="collapsed",
    )
    run_clicked = st.button("OPEN THE CASE 🔎", type="primary", use_container_width=True)

if run_clicked:
    required_env, _ = PROVIDER_INFO[provider]
    if not question.strip():
        st.warning("Please enter a research question.")
    elif required_env and not os.environ.get(required_env):
        st.error(f"{required_env} is missing.")
    else:
        status = st.status("FOLLOWING THE CLUES...", expanded=True)
        messages = None
        try:
            shown = 0
            with status:
                for messages in stream_research(question):
                    for m in messages[shown:]:
                        msg_type = getattr(m, "type", m.__class__.__name__)
                        tool_calls = getattr(m, "tool_calls", None)
                        if msg_type in ("ai", "AIMessage") and tool_calls:
                            for tc in tool_calls:
                                query = html.escape(str(tc["args"].get("query", tc["args"])))
                                st.markdown(
                                    f'<div class="trace-tool">'
                                    f'<span class="tool-name">[{html.escape(tc["name"].upper())}]</span>'
                                    f' &nbsp;→&nbsp; {query}</div>',
                                    unsafe_allow_html=True,
                                )
                        elif msg_type in ("tool", "ToolMessage"):
                            preview = html.escape(str(m.content)[:600])
                            st.markdown(
                                f'<div class="trace-result">RESULT LOG'
                                f'<pre>{preview}</pre></div>',
                                unsafe_allow_html=True,
                            )
                    shown = len(messages)
            status.update(label="CASE CLOSED 🕵️", state="complete")
            if messages:
                # Persist so the report survives the reruns that follow-up
                # buttons and chat input trigger.
                st.session_state["report"] = messages[-1].content
                st.session_state["report_question"] = question
                st.session_state["chat"] = []
        except Exception as exc:
            status.update(label="TRAIL WENT COLD", state="error")
            st.error(f"Agent run failed: {exc}")

# --------------------------------------------------------------------------
# Report + follow-up assistant
# --------------------------------------------------------------------------
report = st.session_state["report"]
if report:
    st.markdown("### CASE FILE")
    with st.container(border=True):
        st.markdown(report)
    st.download_button(
        "Download the case file (Markdown)",
        data=report,
        file_name="case_file.md",
        mime="text/markdown",
    )

    st.markdown('<div class="followup-title">💬 FOLLOW-UP ASSISTANT</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="followup-sub">Click a quick prompt or ask your own question '
        'about this report.</div>',
        unsafe_allow_html=True,
    )

    quick = None
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("💡 Key takeaways", use_container_width=True):
            quick = "Summarize the core key takeaways from this report."
    with c2:
        if st.button("🧪 Practical example", use_container_width=True):
            quick = "Give a clean, practical example based on this report."
    with c3:
        if st.button("🔭 Future outlook", use_container_width=True):
            quick = "What is the future outlook or what challenges does this report mention?"

    typed = st.chat_input("Ask a follow-up question about this report...")
    user_msg = quick or typed

    if user_msg:
        with st.spinner("Thinking..."):
            try:
                reply = answer_followup(report, st.session_state["chat"], user_msg)
            except Exception as exc:
                reply = f"Follow-up failed: {exc}"
        st.session_state["chat"].append({"role": "user", "content": user_msg})
        st.session_state["chat"].append({"role": "assistant", "content": reply})

    for turn in st.session_state["chat"]:
        with st.chat_message(turn["role"]):
            st.markdown(turn["content"])

st.divider()
st.caption(
    "TIP: log evidence (PDFs) first so the agent has an internal baseline "
    "to compare against live web findings."
)