"""Application configuration loaded from environment variables."""

import os
from dotenv import load_dotenv

load_dotenv()


def get_llm_config() -> dict:
    """Load LLM config from environment variables."""
    provider = os.getenv("LLM_PROVIDER", "ollama-cloud")
    api_key = os.getenv("LLM_API_KEY", "")
    base_url = os.getenv("LLM_BASE_URL", "https://ollama.com")
    model = os.getenv("LLM_MODEL", "gemma4:31b-cloud")

    if not api_key:
        raise ValueError(
            "LLM_API_KEY not configured. Add it to backend/.env"
        )

    return {
        "provider": provider,
        "api_key": api_key,
        "base_url": base_url.rstrip("/"),
        "model": model,
    }


def get_proxy_url() -> str:
    return os.getenv("PROXY_URL", "")


def get_cors_origins() -> list[str]:
    origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:3001")
    return [o.strip() for o in origins.split(",")]
