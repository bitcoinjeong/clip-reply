"""ClipReply API — FastAPI backend."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from config import get_cors_origins
from transcriber import get_transcript, extract_video_id, is_youtube_url
from summarizer import summarize, answer_question

app = FastAPI(title="ClipReply API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Request / Response models ---

class TranscriptRequest(BaseModel):
    url: str

class TranscriptResponse(BaseModel):
    transcript: str
    source: str
    duration: float
    video_id: str | None
    word_count: int

class SummarizeRequest(BaseModel):
    transcript: str
    lang: str = "ko"

class SummarizeResponse(BaseModel):
    summary: str

class ChatRequest(BaseModel):
    transcript: str
    question: str
    chat_history: list[dict] = []
    lang: str = "ko"

class ChatResponse(BaseModel):
    answer: str


# --- Endpoints ---

@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/transcript", response_model=TranscriptResponse)
def api_transcript(req: TranscriptRequest):
    try:
        transcript, source, duration = get_transcript(req.url)
        video_id = extract_video_id(req.url) if is_youtube_url(req.url) else None
        return TranscriptResponse(
            transcript=transcript,
            source=source,
            duration=duration,
            video_id=video_id,
            word_count=len(transcript.split()),
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/summarize", response_model=SummarizeResponse)
def api_summarize(req: SummarizeRequest):
    try:
        summary = summarize(req.transcript, req.lang)
        return SummarizeResponse(summary=summary)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/chat", response_model=ChatResponse)
def api_chat(req: ChatRequest):
    try:
        answer = answer_question(req.transcript, req.question, req.chat_history, req.lang)
        return ChatResponse(answer=answer)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
