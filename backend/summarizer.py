"""LLM-powered summarization and Q&A (no Streamlit dependency).

Supports two backends:
- Ollama Cloud: /api/chat
- OpenAI-compatible: Groq, OpenAI, local Ollama /v1/chat/completions
"""

import requests
from config import get_llm_config


def _flatten_to_single_user(messages: list[dict]) -> list[dict]:
    """Merge all messages into a single user message for Ollama Cloud."""
    parts = []
    for m in messages:
        if m["role"] == "system":
            parts.append(f"[Instructions]\n{m['content']}")
        elif m["role"] == "user":
            parts.append(f"[User]\n{m['content']}")
        elif m["role"] == "assistant":
            parts.append(f"[Assistant]\n{m['content']}")
    return [{"role": "user", "content": "\n\n".join(parts)}]


def _call_ollama_cloud(messages: list[dict], max_tokens: int = 1000) -> str:
    """Call Ollama Cloud /api/chat endpoint."""
    cfg = get_llm_config()
    flat_messages = _flatten_to_single_user(messages)

    response = requests.post(
        f"{cfg['base_url']}/api/chat",
        headers={
            "Authorization": f"Bearer {cfg['api_key']}",
            "Content-Type": "application/json",
        },
        json={
            "model": cfg["model"],
            "messages": flat_messages,
            "stream": False,
            "options": {
                "num_predict": max_tokens,
                "temperature": 0.4,
            },
        },
        timeout=120,
    )
    if not response.ok:
        raise ValueError(
            f"Ollama Cloud API error {response.status_code}: {response.text[:300]}"
        )
    data = response.json()
    return data.get("message", {}).get("content", "")


def _call_openai_compat(messages: list[dict], max_tokens: int = 1000) -> str:
    """Call OpenAI-compatible /v1/chat/completions endpoint."""
    from openai import OpenAI

    cfg = get_llm_config()
    client = OpenAI(api_key=cfg["api_key"], base_url=cfg["base_url"])
    response = client.chat.completions.create(
        model=cfg["model"],
        messages=messages,
        max_tokens=max_tokens,
        temperature=0.4,
    )
    return response.choices[0].message.content


def _call_llm(messages: list[dict], max_tokens: int = 1000) -> str:
    """Route to the correct backend based on LLM_PROVIDER."""
    cfg = get_llm_config()
    if cfg["provider"] == "ollama-cloud":
        return _call_ollama_cloud(messages, max_tokens)
    else:
        return _call_openai_compat(messages, max_tokens)


def summarize(transcript: str, lang: str = "ko") -> str:
    """Generate a structured summary of the video transcript."""
    if not transcript or not transcript.strip():
        raise ValueError("Transcript is empty. Cannot generate summary.")

    max_chars = 12000
    truncated = transcript[:max_chars]
    if len(transcript) > max_chars:
        truncated += "\n\n[... transcript truncated ...]"

    if lang == "ko":
        messages = [
            {
                "role": "system",
                "content": (
                    "너는 영상 요약 전문 어시스턴트야. "
                    "반드시 한국어로 답변해. 영어로 답변하지 마."
                ),
            },
            {
                "role": "user",
                "content": (
                    "다음 영상 자막을 요약해줘. 자막이 영어여도 반드시 한국어로 작성해:\n"
                    "1. 한 줄 요약 (TL;DR)\n"
                    "2. 핵심 포인트 3~5개 (불릿)\n"
                    "3. 주요 키워드/토픽\n\n"
                    f"자막:\n{truncated}"
                ),
            },
        ]
    else:
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a video summarization assistant. "
                    "Write concise, accurate summaries in English."
                ),
            },
            {
                "role": "user",
                "content": (
                    "Summarize this video transcript in English. Provide:\n"
                    "1. A one-line TL;DR\n"
                    "2. 3-5 key bullet points\n"
                    "3. Key topics/keywords mentioned\n\n"
                    f"Transcript:\n{truncated}"
                ),
            },
        ]

    return _call_llm(messages, max_tokens=600)


def answer_question(transcript: str, question: str, chat_history: list[dict], lang: str = "ko") -> str:
    """Answer a question about the video content."""
    max_chars = 10000
    truncated = transcript[:max_chars]

    if lang == "ko":
        system_content = (
            "너는 영상 내용에 대해 질문에 답변하는 어시스턴트야. "
            "반드시 한국어로 답변해. 질문이 영어여도 한국어로 답변해. "
            "자막에 없는 내용이면 솔직하게 없다고 말해.\n\n"
            f"--- 영상 자막 ---\n{truncated}"
        )
    else:
        system_content = (
            "You are a helpful assistant that answers questions about a video. "
            "Always answer in English. "
            "Base your answers strictly on the transcript provided. "
            "If the answer is not in the transcript, say so honestly.\n\n"
            f"--- Video Transcript ---\n{truncated}"
        )

    messages = [{"role": "system", "content": system_content}]

    for msg in chat_history[-10:]:
        if msg["role"] in ("user", "assistant"):
            messages.append({"role": msg["role"], "content": msg["content"]})

    messages.append({"role": "user", "content": question})

    return _call_llm(messages, max_tokens=800)
