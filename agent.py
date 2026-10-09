import os
import streamlit as st
from dotenv import load_dotenv
from groq import Groq

# Load local environment variables if available
load_dotenv()

# Read from Streamlit Cloud Secrets first, fallback to local environment variable
groq_api_key = st.secrets.get("GROQ_API_KEY", os.getenv("GROQ_API_KEY", ""))

client = Groq(api_key=groq_api_key) if groq_api_key else None

def call_groq_llm(messages, doc_only_mode=False):
    """
    Sends conversation history to Groq LLM, adjusting system instructions
    based on the Strict Document-Only toggle.
    """
    if not client:
        return "⚠️ Error: GROQ_API_KEY is missing. Please add GROQ_API_KEY to Streamlit Secrets or your local .env file."

    # Dynamic system instruction based on search mode
    system_instruction = (
        "You are an AI research assistant. STRICT RULE: Answer exclusively using the "
        "provided private PDF documents. Do NOT reference external web knowledge."
        if doc_only_mode
        else "You are an AI research assistant. Synthesize answers by cross-referencing "
             "both private PDF documents AND live web search results."
    )

    # Format messages array with updated system prompt
    formatted_messages = [{"role": "system", "content": system_instruction}] + [
        msg for msg in messages if msg["role"] != "system"
    ]

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=formatted_messages,
            temperature=0.3 if doc_only_mode else 0.7,
            max_tokens=1024,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error calling Groq API: {str(e)}"