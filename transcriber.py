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
    errors = []

    lang_preferences = [["ko", "en"], ["ko"], ["en"]]

    for langs in lang_preferences:
        try:
            result = api.fetch(video_id=video_id, languages=langs)
            snippets = list(result)
            text = " ".join(s.text for s in snippets).strip()
            if len(text) < 10:
                errors.append(f"langs={langs}: too short ({len(text)} chars)")
                continue
            duration = snippets[-1].start / 60 if snippets else 0
            return text, duration
        except Exception as e:
            errors.append(f"langs={langs}: {e}")
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
                errors.append(f"fallback lang={t.language_code}: too short ({len(text)} chars)")
            except Exception as e:
                errors.append(f"fallback lang={t.language_code}: {e}")
                continue
    except Exception as e:
        errors.append(f"list(): {e}")

    error_detail = "; ".join(errors[-3:]) if errors else "unknown"
    raise ValueError(f"No transcript found ({error_detail})")


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
