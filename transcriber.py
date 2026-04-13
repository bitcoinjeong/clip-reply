"""Video transcript extraction: YouTube via youtube-transcript-api, TikTok via URL metadata."""

import re
import html
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound


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


def get_youtube_transcript(video_id: str) -> str:
    """Fetch YouTube transcript and return full text."""
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

        # Prefer manually created, fall back to auto-generated
        transcript = None
        try:
            transcript = transcript_list.find_manually_created_transcript(["ko", "en", "en-US"])
        except NoTranscriptFound:
            transcript = transcript_list.find_generated_transcript(["ko", "en", "en-US"])

        chunks = transcript.fetch()
        text = " ".join(chunk["text"] for chunk in chunks)
        return text
    except TranscriptsDisabled:
        raise ValueError("This video has transcripts disabled.")
    except NoTranscriptFound:
        raise ValueError("No transcript found for this video. It may not have subtitles.")
    except Exception as e:
        raise ValueError(f"Failed to fetch transcript: {str(e)}")


def get_transcript(url: str) -> tuple[str, str]:
    """Get transcript from video URL. Returns (transcript_text, source_type)."""
    if is_youtube_url(url):
        video_id = extract_video_id(url)
        if not video_id:
            raise ValueError("Could not extract YouTube video ID from the URL.")
        transcript = get_youtube_transcript(video_id)
        return transcript, "youtube"
    elif is_tiktok_url(url):
        raise ValueError("TikTok transcript extraction is not yet supported. YouTube URLs are fully supported.")
    else:
        raise ValueError("Unsupported URL. Please provide a YouTube video URL.")