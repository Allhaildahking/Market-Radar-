import os
from dotenv import load_dotenv

load_dotenv()

def env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()
POLL_INTERVAL_SECONDS = max(5, int(os.getenv("POLL_INTERVAL_SECONDS", "10")))
REQUEST_TIMEOUT_SECONDS = max(3, int(os.getenv("REQUEST_TIMEOUT_SECONDS", "8")))
MIN_ALERT_LEVEL = os.getenv("MIN_ALERT_LEVEL", "MEDIUM").upper()
BOOTSTRAP_SILENT = env_bool("BOOTSTRAP_SILENT", True)
SEND_STARTUP_MESSAGE = env_bool("SEND_STARTUP_MESSAGE", True)
DATABASE_PATH = os.getenv("DATABASE_PATH", "data/market_radar.sqlite3")
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8080"))
USER_AGENT = os.getenv("USER_AGENT", "MarketRadar/0.1")
