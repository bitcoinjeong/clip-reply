# ClipReply

AI-powered video summarization and Q&A. Paste a YouTube link, get a summary in seconds, then ask follow-up questions.

## Features

- YouTube transcript extraction (auto-detect Korean/English)
- AI-generated structured summaries (TL;DR + bullet points + keywords)
- Interactive Q&A chat about video content
- Bilingual output (Korean / English)
- Summary download (.txt)
- Embedded video player
- Free tier: 3 videos/day

## Tech Stack

- **Frontend**: Streamlit
- **LLM**: Ollama Cloud (gemma4:31b-cloud) / Groq / OpenAI / local Ollama
- **Transcript**: youtube-transcript-api

## Quick Start

### 1. Clone & setup

```bash
git clone https://github.com/bitcoinjeong/clip-reply.git
cd clip-reply
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure secrets

```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

Edit `.streamlit/secrets.toml` and fill in your API key. See [LLM Options](#llm-options) below for provider choices.

### 3. Run

```bash
streamlit run app.py
```

App opens at `http://localhost:8501`.

## LLM Options

| Provider | LLM_PROVIDER | Base URL | Model | Cost |
|----------|-------------|----------|-------|------|
| **Ollama Cloud** | `ollama-cloud` | `https://ollama.com` | `gemma4:31b-cloud` | Free |
| Groq | `openai` | `https://api.groq.com/openai/v1` | `llama-3.3-70b-versatile` | Free tier |
| OpenAI | `openai` | `https://api.openai.com/v1` | `gpt-4o-mini` | Paid |
| Ollama (local) | `openai` | `http://localhost:11434/v1` | `llama3.1` | Free (local) |

## Project Structure

```
clip-reply/
├── app.py                        # Main Streamlit application
├── transcriber.py                # YouTube transcript extraction
├── summarizer.py                 # LLM summarization & Q&A
├── requirements.txt              # Python dependencies
├── .streamlit/
│   ├── secrets.toml.example      # Secrets template (copy to secrets.toml)
│   └── secrets.toml              # Your secrets (git-ignored)
└── README.md
```

## Deploy to Streamlit Cloud

1. Push to GitHub
2. Connect repo on [share.streamlit.io](https://share.streamlit.io)
3. In Streamlit Cloud dashboard, add secrets:
   - `LLM_PROVIDER`
   - `LLM_API_KEY`
   - `LLM_BASE_URL`
   - `LLM_MODEL`
   - `PROXY_URL` (required - YouTube blocks cloud IPs, use [Webshare](https://www.webshare.io) free tier)

## Pricing Plan

- **Free**: 3 videos/day
- **Pro $9/mo**: Unlimited + long videos + PDF export
