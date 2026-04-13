"""Video transcript extraction for YouTube (no Streamlit dependency)."""

import re
from youtube_transcript_api import YouTubeTranscriptApi
from config import get_proxy_url


def extract_video_id(url: str) -> str | None:
    """Extract YouTube video ID from various URL formats."""
    patterns = [
        r"(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([a-zA-Z0-9_-]{11})",
        r"youtube\.com/shorts/([a-zA-Z0-9_-]{11})",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def is_youtube_url(url: str) -> bool:
    return bool(re.search(r"(youtube\.com|youtu\.be)", url))


def _build_api() -> YouTubeTranscriptApi:
    """Create YouTubeTranscriptApi with optional proxy."""
    proxy_url = get_proxy_url()
    if proxy_url:
        return YouTubeTranscriptApi(proxies={"https": proxy_url, "http": proxy_url})
    return YouTubeTranscriptApi()


def get_youtube_transcript(video_id: str) -> tuple[str, float]:
    """Fetch YouTube transcript. Returns (text, duration_minutes)."""
    api = _build_api()
    ip_blocked = False

    lang_preferences = [["ko", "en"], ["ko"], ["en"]]

    for langs in lang_preferences:
        try:
            result = api.fetch(video_id=video_id, languages=langs)
            snippets = list(result)
            text = " ".join(s.text for s in snippets).strip()
            if len(text) < 10:
                continue
            duration = snippets[-1].start / 60 if snippets else 0
            return text, duration
        except Exception as e:
            if "blocking" in str(e).lower() or "ip" in str(e).lower():
                ip_blocked = True
            continue

    # Fallback: list available transcripts and fetch the first one
    try:
        transcript_list = api.list(video_id)
        for t in transcript_list:
            try:
                result = api.fetch(video_id=video_id, languages=[t.language_code])
                snippets = list(result)
                text = " ".join(s.text for s in snippets).strip()
                if len(text) >= 10:
                    duration = snippets[-1].start / 60 if snippets else 0
                    return text, duration
            except Exception as e:
                if "blocking" in str(e).lower() or "ip" in str(e).lower():
                    ip_blocked = True
                continue
    except Exception as e:
        if "blocking" in str(e).lower() or "ip" in str(e).lower():
            ip_blocked = True

    if ip_blocked:
        raise ValueError(
            "YouTube is blocking this server's IP address. "
            "A proxy is required for cloud deployment. "
            "Add PROXY_URL to backend/.env"
        )

    raise ValueError("No transcript found. This video may not have subtitles enabled.")


def get_transcript(url: str) -> tuple[str, str, float]:
    """Get transcript from video URL.

    Returns: (transcript_text, source_type, duration_minutes)
    """
    if is_youtube_url(url):
        video_id = extract_video_id(url)
        if not video_id:
            raise ValueError("Could not extract YouTube video ID from the URL.")
        transcript, duration = get_youtube_transcript(video_id)
        return transcript, "youtube", duration

    raise ValueError("Unsupported URL. Please provide a YouTube video link.")
