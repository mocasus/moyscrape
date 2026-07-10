import os
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent


def load_config() -> dict:
    """Load .env from project root into a flat config dict."""
    load_dotenv(ROOT / ".env")
    return {
        "db": os.getenv("SCRAPE_DB", str(ROOT / "scrapes.db")),
        "proxy": os.getenv("SCRAPE_PROXY"),
        "tg_token": os.getenv("TELEGRAM_BOT_TOKEN"),
        "tg_chat": os.getenv("TELEGRAM_CHAT_ID"),
        "webhook": os.getenv("WEBHOOK_URL"),
        "llm_key": os.getenv("LLM_API_KEY"),
        "llm_base": os.getenv("LLM_BASE_URL", "https://api.openai.com/v1"),
        "llm_model": os.getenv("LLM_MODEL", "gpt-4o-mini"),
    }
