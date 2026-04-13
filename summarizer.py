"""LLM-powered summarization and Q&A using Ollama Cloud API."""

import requests
import streamlit as st


OLLAMA_BASE_URL = "https://api.ollama.com/api"
MODEL = "llama3"


def _call_llm(messages: list[dict], max_tokens: int = 1000) -> str:
    """Call Ollama Cloud API with /api/generate endpoint."""
    api_key = st.secrets.get("OLLAMA_API_KEY", "")
    if not api_key:
        raise ValueError("OLLAMA_API_KEY not configured. Add it to .streamlit/secrets.toml")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    # Build prompt from messages
    prompt_parts = []
    for msg in messages:
        role = msg["role"].capitalize()
        prompt_parts.append(f"{role}: {msg['content']}")
    prompt = "\n\n".join(prompt_parts)

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
        f"{OLLAMA_BASE_URL}/generate",
        headers=headers,
        json=payload,
        timeout=120,
    )
    response.raise_for_status()
    data = response.json()
    return data.get("response", "")


def summarize(transcript: str) -> str:
    """Generate a bullet-point summary of the video transcript."""
    prompt = f"""Summarize the following video transcript in 3-5 concise bullet points. 
Write in the same language as the transcript. Do not add emoji.

Transcript:
{transcript[:8000]}"""
    messages = [{"role": "user", "content": prompt}]
    return _call_llm(messages, max_tokens=500)


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

    messages = [{"role": "user", "content": prompt}]
    return _call_llm(messages, max_tokens=800)