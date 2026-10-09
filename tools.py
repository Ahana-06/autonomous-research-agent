"""
The two tools the ReAct agent can call:

  1. search_internal_documents - similarity search over the private
     ChromaDB collection built from the user's uploaded PDFs.
  2. search_web               - live web search via the Tavily API.

Each tool returns a plain-text block of numbered, source-tagged snippets
so the agent (and the final report) can cite them as [Internal-N] / [Web-N].
"""
from langchain_core.tools import tool
from tavily import TavilyClient

import config
from ingestion import load_existing_vectorstore

_vectorstore = None


def get_vectorstore():
    """Lazily open the persisted Chroma collection (built via ingestion.py)."""
    global _vectorstore
    if _vectorstore is None:
        _vectorstore = load_existing_vectorstore()
    return _vectorstore


def reset_vectorstore_cache():
    """Call after re-ingesting documents so the next tool call re-opens it."""
    global _vectorstore
    _vectorstore = None


@tool
def search_internal_documents(query: str) -> str:
    """Search the private internal PDF knowledge base for passages relevant
    to the query. Use this FIRST for any factual question, since it reflects
    the organization's own vetted documents. Returns numbered snippets tagged
    [Internal-N] with their source file and page number. If nothing relevant
    comes back, or the results look outdated / incomplete, follow up with
    search_web."""
    try:
        vs = get_vectorstore()
        results = vs.similarity_search_with_relevance_scores(query, k=config.TOP_K)
    except Exception as exc:  # e.g. no collection built yet
        return (
            "The internal document knowledge base is empty or unavailable "
            f"({exc}). Skip to search_web instead."
        )

    if not results:
        return "No relevant internal documents found for this query."

    formatted = []
    for i, (doc, score) in enumerate(results, 1):
        source = doc.metadata.get("source", "unknown")
        page = doc.metadata.get("page", "?")
        formatted.append(
            f"[Internal-{i}] (source: {source}, page: {page}, "
            f"relevance: {score:.2f})\n{doc.page_content.strip()}"
        )
    return "\n\n".join(formatted)


@tool
def search_web(query: str) -> str:
    """Search the live public web for current, real-time, or recent
    information (news, latest figures, releases, events) via Tavily. Use
    this when the internal knowledge base has no answer, an outdated answer,
    or when the question explicitly needs up-to-date external context.
    Returns numbered snippets tagged [Web-N] with their source URL."""
    if not config.TAVILY_API_KEY:
        return "Web search is unavailable: no TAVILY_API_KEY configured."

    client = TavilyClient(api_key=config.TAVILY_API_KEY)
    try:
        response = client.search(
            query=query,
            search_depth="advanced",
            max_results=config.WEB_MAX_RESULTS,
            include_answer=False,
        )
    except Exception as exc:
        return f"Web search failed: {exc}"

    results = response.get("results", [])
    if not results:
        return "No web results found for this query."

    formatted = []
    for i, r in enumerate(results, 1):
        title = r.get("title", "Untitled")
        url = r.get("url", "unknown")
        content = (r.get("content") or "").strip()[:800]
        formatted.append(f"[Web-{i}] (source: {url})\nTitle: {title}\n{content}")
    return "\n\n".join(formatted)
