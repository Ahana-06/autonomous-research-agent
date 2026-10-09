"""
Central configuration for the research agent.

All values can be overridden via environment variables or a local .env file
(see .env.example). Nothing here should contain real secrets.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# --- API keys -----------------------------------------------------------
# Tavily has a free tier (1,000 searches/month, no card required):
# https://tavily.com
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")

# LLM provider keys - you only need to fill in the one matching
# LLM_PROVIDER below. All of these have a free tier:
#   groq      -> https://console.groq.com/keys        (free, fast, generous)
#   google    -> https://aistudio.google.com/apikey    (free tier)
#   anthropic -> https://console.anthropic.com         (paid, not free)
#   ollama    -> no key needed, runs 100% locally: https://ollama.com
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# --- Model / provider settings --------------------------------------------
# One of: "groq" (default, free), "google" (free), "anthropic" (paid),
# "ollama" (free, fully local, requires `ollama serve` running).
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq")

# Model name per provider (override any of these in .env if you want a
# different size/speed/quality tradeoff).
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
GOOGLE_MODEL = os.getenv("GOOGLE_MODEL", "gemini-3.6-flash")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-5")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.2"))
# Lower default so requests leave more headroom under free-tier TPM
# (tokens/minute) rate limits; raise it if you're on a paid tier.
LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "1200"))

# --- Embeddings / vector store --------------------------------------------
# Local, free, no-API-key embedding model. Swap for OpenAIEmbeddings if you
# prefer and have an OPENAI_API_KEY set.
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
CHROMA_DIR = os.getenv("CHROMA_DIR", "./chroma_store")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "research_docs")

# --- Chunking ---------------------------------------------------------
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "150"))

# --- Retrieval / search ---------------------------------------------------
TOP_K = int(os.getenv("TOP_K", "3"))
WEB_MAX_RESULTS = int(os.getenv("WEB_MAX_RESULTS", "3"))
# "basic" is noticeably faster than "advanced"; switch back to "advanced"
# only if you need deeper web results and can tolerate the extra latency.
TAVILY_SEARCH_DEPTH = os.getenv("TAVILY_SEARCH_DEPTH", "basic")
# How many characters of each retrieved snippet to keep. Smaller = fewer
# tokens per request = less likely to hit a free-tier TPM (tokens/minute)
# rate limit, at the cost of less context per snippet.
SNIPPET_CHAR_LIMIT = int(os.getenv("SNIPPET_CHAR_LIMIT", "400"))

# --- Agent -----------------------------------------------------------
# Caps how many reasoning/tool-call rounds a single question can take.
# Lower = faster but may cut off a complex question early; higher = more
# thorough but slower. 12-15 is usually enough for internal+web research.
RECURSION_LIMIT = int(os.getenv("RECURSION_LIMIT", "15"))
