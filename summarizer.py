"""LLM-powered summarization and Q&A using Ollama Cloud API."""

import requests
import streamlit as st


OLLAMA_BASE_URL = "https://api.ollama.com/v1"
MODEL = "llama3"


def _call_llm(messages: list[dict], max_tokens: int = 1000) -> str:
    """Call Ollama Cloud API with chat completions."""
    api_key = st.secrets.get("OLLAMA_API_KEY", "")
    if not api_key:
        raise ValueError("OLLAMA_API_KEY not configured. Add it to .streamlit/secrets.toml")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": MODEL,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": 0.7,
    }

    response = requests.post(
        f"{OLLAMA_BASE_URL}/chat/completions",
        headers=headers,
        json=payload,
        timeout=60,
    )
    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"]


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