"""Video transcript extraction for YouTube."""

import re
from youtube_transcript_api import YouTubeTranscriptApi


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


def is_tiktok_url(url: str) -> bool:
    return bool(re.search(r"tiktok\.com", url))


def get_youtube_transcript(video_id: str) -> tuple[str, float]:
    """Fetch YouTube transcript. Returns (text, duration_minutes)."""
    api = YouTubeTranscriptApi()

    lang_preferences = [["ko", "en"], ["en"], ["ko"]]

    for langs in lang_preferences:
        try:
            result = api.fetch(video_id=video_id, languages=langs)
            snippets = list(result)
            text = " ".join(s.text for s in snippets)
            duration = snippets[-1].start / 60 if snippets else 0
            return text, duration
        except Exception:
            continue

    # Fallback: no language filter
    try:
        result = api.fetch(video_id=video_id)
        snippets = list(result)
        text = " ".join(s.text for s in snippets)
        duration = snippets[-1].start / 60 if snippets else 0
        return text, duration
    except Exception:
        pass

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

    if is_tiktok_url(url):
        raise ValueError(
            "TikTok is not yet supported. YouTube URLs are fully supported."
        )

    raise ValueError("Unsupported URL. Please provide a YouTube video link.")
