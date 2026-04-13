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

- **Frontend**: Next.js + TypeScript + Tailwind CSS
- **Backend**: FastAPI (Python)
- **LLM**: Ollama Cloud (gemma4:31b-cloud) / Groq / OpenAI / local Ollama
- **Transcript**: youtube-transcript-api

## Project Structure

```
clip-reply/
├── frontend/                 # Next.js (TypeScript + Tailwind)
│   ├── app/                  # App Router pages
│   ├── components/           # React components
│   ├── lib/                  # API client
│   └── .env.example          # Frontend env template
├── backend/                  # FastAPI
│   ├── main.py               # API endpoints
│   ├── transcriber.py        # YouTube transcript extraction
│   ├── summarizer.py         # LLM summarization & Q&A
│   ├── config.py             # Environment config
│   └── .env.example          # Backend env template
├── app.py                    # Legacy Streamlit app
└── README.md
```

## Quick Start

### 1. Clone

```bash
git clone https://github.com/bitcoinjeong/clip-reply.git
cd clip-reply
```

### 2. Backend setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # Edit .env and add your API key
uvicorn main:app --port 8001
```

API runs at `http://localhost:8001`. Test: `curl http://localhost:8001/api/health`

### 3. Frontend setup (new terminal)

```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev -- --port 3001
```

App opens at `http://localhost:3001`.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| POST | `/api/transcript` | Extract transcript from YouTube URL |
| POST | `/api/summarize` | Generate AI summary from transcript |
| POST | `/api/chat` | Q&A about video content |

## LLM Options

| Provider | LLM_PROVIDER | Base URL | Model | Cost |
|----------|-------------|----------|-------|------|
| **Ollama Cloud** | `ollama-cloud` | `https://ollama.com` | `gemma4:31b-cloud` | Free |
| Groq | `openai` | `https://api.groq.com/openai/v1` | `llama-3.3-70b-versatile` | Free tier |
| OpenAI | `openai` | `https://api.openai.com/v1` | `gpt-4o-mini` | Paid |
| Ollama (local) | `openai` | `http://localhost:11434/v1` | `llama3.1` | Free (local) |

## Deploy

**Backend** (Railway / Render):
- Set environment variables from `backend/.env.example`
- Start command: `uvicorn main:app --host 0.0.0.0 --port 8000`

**Frontend** (Vercel):
- Connect `frontend/` directory
- Set `NEXT_PUBLIC_API_URL` to your backend URL

## Pricing Plan

- **Free**: 3 videos/day
- **Pro $9/mo**: Unlimited + long videos + PDF export
