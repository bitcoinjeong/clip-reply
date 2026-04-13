# ClipReply

AI-powered video summarization and Q&A. Paste a YouTube link, get a summary in seconds, then ask follow-up questions.

## Features

- YouTube transcript extraction (auto-detect Korean/English)
- AI-generated structured summaries (TL;DR + bullet points + keywords)
- Interactive Q&A chat about video content
- Summary download (.txt)
- Embedded video player
- Free tier: 3 videos/day

## Tech Stack

- **Frontend**: Streamlit
- **LLM**: Ollama Cloud (gemma4:31b-cloud) / Groq / OpenAI / local Ollama
- **Transcript**: youtube-transcript-api

## Quick Start

```bash
pip install -r requirements.txt
```

Configure `.streamlit/secrets.toml`:

```toml
# Ollama Cloud + gemma4 (default)
LLM_PROVIDER = "ollama-cloud"
LLM_API_KEY = "your-ollama-cloud-api-key"
LLM_BASE_URL = "https://ollama.com"
LLM_MODEL = "gemma4:31b-cloud"
```

Run:

```bash
streamlit run app.py
```

## LLM Options

| Provider | LLM_PROVIDER | Base URL | Model |
|----------|-------------|----------|-------|
| **Ollama Cloud** | `ollama-cloud` | `https://ollama.com` | `gemma4:31b-cloud` |
| Groq | `openai` | `https://api.groq.com/openai/v1` | `llama-3.3-70b-versatile` |
| OpenAI | `openai` | `https://api.openai.com/v1` | `gpt-4o-mini` |
| Ollama (local) | `openai` | `http://localhost:11434/v1` | `llama3.1` |

## Deploy

Deploy to Streamlit Cloud:
1. Push to GitHub
2. Connect repo on [share.streamlit.io](https://share.streamlit.io)
3. Add `LLM_API_KEY`, `LLM_BASE_URL`, `LLM_MODEL` in Streamlit Cloud secrets

## Pricing Plan

- **Free**: 3 videos/day
- **Pro $9/mo**: Unlimited + long videos + PDF export
