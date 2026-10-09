# Autonomous Research Agent

An interactive dashboard where an autonomous **ReAct** agent answers a research
question by combining:

- **Private RAG** — semantic search over your own PDFs, embedded and stored
  in **ChromaDB**.
- **Live web search** — via the **Tavily** API (free tier, no card
  required), for real-time / recent information not covered by the internal
  documents.
- **A free-tier LLM** as the reasoning engine — **Groq** by default (fast,
  generous free limits), with **Google Gemini**, fully-local **Ollama**, or
  paid **Anthropic Claude** available as drop-in swaps — orchestrated with
  **LangGraph**'s prebuilt ReAct agent.
- **Streamlit** as the UI.

**Everything in the default configuration is free**: Groq's free tier for
the LLM, Tavily's free tier for web search, and local `sentence-transformers`
embeddings that need no API key or cost at all.

The agent decides for itself, turn by turn, whether to consult your
documents, search the web, or (once it has enough evidence) write the final
structured, cited report.

## How it works

```
User question
     │
     ▼
┌─────────────────────────────┐
│   LangGraph ReAct agent      │◄──────────────┐
│   (Claude as the LLM)        │                │
└──────────────┬───────────────┘                │
       Thought │ decides next action            │
               ▼                                │
   ┌───────────────────────┐   ┌────────────────────────┐
   │ search_internal_docs  │   │      search_web         │
   │ (Chroma similarity     │   │ (Tavily live search)    │
   │  search over your PDFs)│   └────────────────────────┘
   └───────────────────────┘                │
               │           Observation       │
               └──────────────┬──────────────┘
                               ▼
                  loops until agent has enough
                  evidence, then emits the final
                  Markdown report with citations
```

Policy baked into the agent's system prompt (see `agent.py`):
1. Always check internal documents first.
2. Identify what's missing, stale, or unconfirmed.
3. Search the web to fill exactly those gaps / verify time-sensitive facts.
4. Cross-check and flag disagreements between sources.
5. Cite every claim as `[Internal-N]` or `[Web-N]`, traceable to a real
   tool-call result — never fabricated.
6. Output a structured report: Executive Summary, Key Findings, Detailed
   Analysis, Gaps & Caveats, Sources.

## Setup (100% free)

```bash
cd research_agent
python -m venv venv && source venv/bin/activate   # optional but recommended
pip install -r requirements.txt
cp .env.example .env   # then edit .env with your real API keys
```

You need two free keys:
1. **Groq** (LLM) — https://console.groq.com/keys — free tier, no card.
2. **Tavily** (web search) — https://tavily.com — free tier (1,000
   searches/month), no card.

Put both in `.env`:
```
TAVILY_API_KEY=tvly-...
LLM_PROVIDER=groq
GROQ_API_KEY=gsk_...
```

No OpenAI key is ever required: document embeddings run locally via
`sentence-transformers` (no external API calls, no per-embedding cost).

### Other free/local LLM options

Set `LLM_PROVIDER` in `.env` (or pick it from the sidebar dropdown at
runtime) to switch:

| Provider              | `LLM_PROVIDER` value | Key needed                                   | Notes                          |
|------------------------|----------------------|-----------------------------------------------|---------------------------------|
| Groq (default)          | `groq`                | `GROQ_API_KEY`                                | Free, very fast, Llama 3.3 70B |
| Google Gemini           | `google`              | `GOOGLE_API_KEY`                              | Free tier, `gemini-2.0-flash`  |
| Ollama (fully local)    | `ollama`              | none — run `ollama serve` + `ollama pull llama3.1` | No API key, no internet needed for the LLM |
| Anthropic Claude        | `anthropic`           | `ANTHROPIC_API_KEY`                           | Paid, only if you want Claude  |

Only install the LangChain integration package for the provider you're
using (see the comments in `requirements.txt`) — `langchain-groq` is
included by default.

## Run

```bash
streamlit run app.py
```

Then in the browser:
1. Enter your API keys in the sidebar (or rely on your `.env`).
2. Upload one or more PDF documents and click **Ingest documents** to build
   the private vector store.
3. Type a research question and click **Run research agent**.
4. Watch the live tool-call trace, then read (and download) the final
   Markdown report.

## Files

| File            | Purpose                                                        |
|-----------------|------------------------------------------------------------------|
| `config.py`     | All tunable settings, loaded from environment / `.env`.          |
| `ingestion.py`  | Loads PDFs, chunks them, embeds them, persists them to Chroma.   |
| `tools.py`      | The two agent tools: internal RAG search and Tavily web search.  |
| `agent.py`      | Builds the LangGraph ReAct agent and its research-policy prompt. |
| `app.py`        | The Streamlit dashboard tying everything together.               |

## Notes & extension ideas

- **Model choice**: each provider's model name lives in `config.py`
  (`GROQ_MODEL`, `GOOGLE_MODEL`, etc.) — override via `.env` if you want a
  different size/speed/quality tradeoff (e.g. a smaller/faster Groq model).
- **Swap FAISS for Chroma**: `ingestion.py` isolates all vector-store code,
  so switching to `langchain_community.vectorstores.FAISS` only requires
  changing that one file.
- **Swap embeddings**: set `EMBEDDING_MODEL` or replace
  `HuggingFaceEmbeddings` with `OpenAIEmbeddings` if you'd rather use a
  hosted embedding API.
- **Persistence across sessions**: the Chroma store persists to
  `CHROMA_DIR` on disk, so re-running the app without re-ingesting will
  reuse the last-built knowledge base.
- **Cost/latency control**: `TOP_K` and `WEB_MAX_RESULTS` in `config.py`
  cap how much context each tool call returns; `RECURSION_LIMIT` caps how
  many agent reasoning steps a single question can take.
