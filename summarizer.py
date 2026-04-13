"""LLM-powered summarization and Q&A using Ollama Cloud API."""

import requests
import streamlit as st


OLLAMA_API_URL = "https://ollama.com/api/generate"
MODEL = "gemma4:27b-cloud"


def _call_llm(prompt: str, max_tokens: int = 1000) -> str:
    """Call Ollama Cloud API via /api/generate."""
    api_key = st.secrets.get("OLLAMA_API_KEY", "")
    if not api_key:
        raise ValueError("OLLAMA_API_KEY not configured. Add it to Streamlit Cloud secrets.")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "num_predict": max_tokens,
            "temperature": 0.7,
        },
    }

    response = requests.post(
        OLLAMA_API_URL,
        headers=headers,
        json=payload,
        timeout=120,
    )
    if not response.ok:
        raise ValueError(f"API error {response.status_code} from {response.url}: {response.text[:200]}")
    data = response.json()
    return data.get("response", "")


def summarize(transcript: str) -> str:
    """Generate a bullet-point summary of the video transcript."""
    prompt = f"""Summarize the following video transcript in 3-5 concise bullet points. 
Write in the same language as the transcript. Do not add emoji.

Transcript:
{transcript[:8000]}"""
    return _call_llm(prompt, max_tokens=500)


def answer_question(transcript: str, question: str, chat_history: list[dict]) -> str:
    """Answer a question about the video content."""
    history_str = ""
    for msg in chat_history:
        role = "User" if msg["role"] == "user" else "Assistant"
        history_str += f"{role}: {msg['content']}\n"

    prompt = f"""Based on the following video transcript, answer the user's question. 
If the answer is not in the transcript, say so honestly.
Write in the same language as the question.

Transcript:
{transcript[:6000]}

Conversation so far:
{history_str}

Question: {question}"""

    return _call_llm(prompt, max_tokens=800)