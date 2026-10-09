import os
from groq import Groq

def call_groq_llm(messages, doc_only_mode=False):
    """
    Calls the Groq API using the clean model identifier.
    Reads GROQ_API_KEY from environment / st.secrets.
    """
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        try:
            import streamlit as st
            api_key = st.secrets.get("GROQ_API_KEY")
        except Exception:
            pass

    if not api_key:
        return "⚠️ Error: GROQ_API_KEY is not configured in Streamlit Secrets or Environment Variables."

    try:
        client = Groq(api_key=api_key)
        
        # Clean model string to prevent 404 / hidden character issues
        model_name = "llama-3.3-70b-versatile"

        # Format messages for the Groq client
        formatted_messages = []
        for msg in messages:
            formatted_messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })

        completion = client.chat.completions.create(
            model=model_name,
            messages=formatted_messages,
            temperature=0.3,
            max_tokens=1024
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error calling Groq API: {str(e)}"