"""
Builds and runs the autonomous ReAct research agent.

The agent reasons step by step (Thought -> Action -> Observation), deciding
on each turn whether to query the private document store, query the live
web, or synthesize a final structured report. LangGraph's prebuilt
create_react_agent implements this loop; we supply the tools and a system
prompt that encodes the research policy described in the problem statement.
"""
from langgraph.prebuilt import create_react_agent

import config
from tools import search_internal_documents, search_web

SYSTEM_PROMPT = """You are an autonomous research analyst. Given a research \
topic or question, you must produce a rigorous, well-cited report by \
combining a private internal document store with live web search.

Follow this policy on every question:
1. Always call search_internal_documents first to check what the \
organization's own documents already say.
2. Identify what is MISSING, stale, or unconfirmed in those results \
(e.g. no data on a fast-moving topic, no numbers newer than the documents' \
publication date, no coverage of the specific sub-question asked).
3. Call search_web to fill exactly those gaps and to verify or update any \
internal claims that could plausibly have changed. Do not skip this step \
just because internal results seemed adequate on a time-sensitive topic.
4. You may call either tool multiple times with refined queries if the \
first results are thin or off-target.
5. Cross-check facts that appear in both sources; note any disagreement \
explicitly rather than silently picking one.
6. Never fabricate a citation. Only cite snippet numbers ([Internal-N], \
[Web-N]) that were actually returned by a tool call in this conversation.

When you have enough evidence, produce your FINAL ANSWER as a structured \
Markdown report with exactly these sections:

## Executive Summary
2-4 sentences giving the direct answer / bottom line.

## Key Findings
A bulleted list of the most important, individually-citable facts.

## Detailed Analysis
Several paragraphs synthesizing internal and external evidence, comparing \
and contextualizing them. Cite inline like "... grew 18% in 2025 \
[Web-2][Internal-1]."

## Gaps & Caveats
What remains uncertain, contested, or unavailable in either source.

## Sources
A flat list mapping every citation tag used above to its source \
(file + page for [Internal-N], URL for [Web-N]).

Be concise but substantive. Do not include your internal reasoning, only \
the final report, in your last message.
"""


def get_llm():
    """Instantiate the chat model for whichever provider is configured.

    LLM_PROVIDER controls this ("groq" | "google" | "anthropic" | "ollama").
    Imports are done lazily inside each branch so you only need the one
    integration package actually installed/used for your chosen provider.
    """
    provider = (config.LLM_PROVIDER or "groq").lower()

    if provider == "groq":
        from langchain_groq import ChatGroq
        if not config.GROQ_API_KEY:
            raise ValueError(
                "LLM_PROVIDER is 'groq' but GROQ_API_KEY is not set. "
                "Get a free key at https://console.groq.com/keys"
            )
        return ChatGroq(
            model=config.GROQ_MODEL,
            api_key=config.GROQ_API_KEY,
            temperature=config.LLM_TEMPERATURE,
            max_tokens=config.LLM_MAX_TOKENS,
        )

    if provider == "google":
        from langchain_google_genai import ChatGoogleGenerativeAI
        if not config.GOOGLE_API_KEY:
            raise ValueError(
                "LLM_PROVIDER is 'google' but GOOGLE_API_KEY is not set. "
                "Get a free key at https://aistudio.google.com/apikey"
            )
        return ChatGoogleGenerativeAI(
            model=config.GOOGLE_MODEL,
            google_api_key=config.GOOGLE_API_KEY,
            temperature=config.LLM_TEMPERATURE,
            max_output_tokens=config.LLM_MAX_TOKENS,
        )

    if provider == "ollama":
        from langchain_ollama import ChatOllama
        return ChatOllama(
            model=config.OLLAMA_MODEL,
            base_url=config.OLLAMA_BASE_URL,
            temperature=config.LLM_TEMPERATURE,
        )

    if provider == "anthropic":
        from langchain_anthropic import ChatAnthropic
        if not config.ANTHROPIC_API_KEY:
            raise ValueError(
                "LLM_PROVIDER is 'anthropic' but ANTHROPIC_API_KEY is not set."
            )
        return ChatAnthropic(
            model=config.ANTHROPIC_MODEL,
            api_key=config.ANTHROPIC_API_KEY,
            temperature=config.LLM_TEMPERATURE,
            max_tokens=config.LLM_MAX_TOKENS,
        )

    raise ValueError(
        f"Unknown LLM_PROVIDER '{provider}'. Use one of: groq, google, "
        "anthropic, ollama."
    )


def build_agent():
    """Construct the LangGraph ReAct agent (LLM + tools + system prompt)."""
    llm = get_llm()
    tools = [search_internal_documents, search_web]
    return create_react_agent(llm, tools, prompt=SYSTEM_PROMPT)


def run_research(question: str, recursion_limit: int = None):
    """Run the agent to completion on a research question (blocking).

    Returns the full list of LangGraph messages (human / AI / tool), so the
    caller can render the ReAct trace as well as the final report, which is
    the content of the last message.
    """
    recursion_limit = recursion_limit or config.RECURSION_LIMIT
    agent = build_agent()
    result = agent.invoke(
        {"messages": [("user", question)]},
        config={"recursion_limit": recursion_limit},
    )
    return result["messages"]


def stream_research(question: str, recursion_limit: int = None):
    """Run the agent step by step, yielding the message list after each
    reasoning/tool step completes.

    Preferred over run_research for UIs: the caller can render each tool
    call and result as soon as it happens, rather than waiting silently for
    the entire (potentially multi-step) run to finish.
    """
    recursion_limit = recursion_limit or config.RECURSION_LIMIT
    agent = build_agent()
    for step in agent.stream(
        {"messages": [("user", question)]},
        config={"recursion_limit": recursion_limit},
        stream_mode="values",
    ):
        yield step["messages"]