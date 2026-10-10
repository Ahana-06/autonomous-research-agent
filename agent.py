import os
import requests

def call_groq_llm(messages, doc_only_mode=False):
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        try:
            import streamlit as st
            api_key = st.secrets.get("GROQ_API_KEY")
        except Exception:
            pass

    if not api_key:
        return "⚠️ Error: GROQ_API_KEY is missing in Streamlit Secrets."

    url = "https://api.groq.com/openai/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key.strip()}",
        "Content-Type": "application/json"
    }

    formatted_messages = [{"role": m["role"], "content": m["content"]} for m in messages]

    payload = {
        "model": "openai/gpt-oss-20b",  # Active and supported model ID
        "messages": formatted_messages,
        "temperature": 0.3,
        "max_tokens": 1024
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        data = response.json()

        if response.status_code == 200:
            return data["choices"][0]["message"]["content"]
        else:
            error_msg = data.get("error", {}).get("message", response.text)
            return f"API Response Error ({response.status_code}): {error_msg}"
            
    except Exception as e:
        return f"Request Exception: {str(e)}"