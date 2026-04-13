"""Video transcript extraction: YouTube via youtube-transcript-api."""

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


def get_youtube_transcript(video_id: str) -> str:
    """Fetch YouTube transcript and return full text."""
    api = YouTubeTranscriptApi()
    try:
        # Try fetching with language preferences
        for langs in [["ko", "en"], ["en"], ["ko"]]:
            try:
                result = api.fetch(video_id=video_id, languages=langs)
                text = " ".join(snippet.text for snippet in result)
                return text
            except Exception:
                continue

        # Fall back: no language filter
        try:
            result = api.fetch(video_id=video_id)
            text = " ".join(snippet.text for snippet in result)
            return text
        except Exception:
            pass

        raise ValueError("No transcript found for this video. It may not have subtitles.")
    except ValueError:
        raise
    except Exception as e:
        error_str = str(e).lower()
        if "disabled" in error_str:
            raise ValueError("This video has transcripts disabled.")
        if "not found" in error_str or "no transcript" in error_str:
            raise ValueError("No transcript found for this video. It may not have subtitles.")
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