# ClipReply

Paste a video link. Get the summary. Ask anything about it.

AI-powered video summarization and Q&A. Supports YouTube videos with transcripts.

## Features

- YouTube video transcript extraction
- AI-generated bullet-point summaries
- Interactive Q&A about video content
- Free tier: 3 videos/day

## Setup

```bash
pip install -r requirements.txt
```

Add your API key to `.streamlit/secrets.toml`:
```toml
OLLAMA_API_KEY = "your-key-here"
```

## Run

```bash
streamlit run app.py
```

## Deploy

Deploy to Streamlit Cloud by connecting your GitHub repo and adding the OLLAMA_API_KEY secret.