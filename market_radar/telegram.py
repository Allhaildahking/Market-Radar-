import aiohttp
from html import escape

class Telegram:
    def __init__(self, session: aiohttp.ClientSession, token: str, chat_id: str):
        self.session = session
        self.base = f"https://api.telegram.org/bot{token}"
        self.chat_id = chat_id

    async def send(self, text: str):
        if not self.chat_id or not self.base:
            return
        url = f"{self.base}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
        }
        async with self.session.post(url, json=payload) as response:
            body = await response.text()
            if response.status >= 300:
                raise RuntimeError(f"Telegram HTTP {response.status}: {body[:300]}")

    async def startup(self):
        await self.send("🟢 <b>MARKET RADAR ONLINE</b>\nCollector started. Monitoring configured feeds.")

def format_alert(item: dict) -> str:
    title = escape(item["title"][:350])
    source = escape(item["source"])
    level = escape(item["level"])
    assets = escape(", ".join(item["assets"]))
    reason = escape(item["reason"])
    link = escape(item["link"], quote=True)
    published = escape(item.get("published") or "Not supplied by source")
    detected = escape(item["detected"])
    delay = escape(item.get("delay") or "Unavailable")
    emoji = {"CRITICAL": "🚨", "HIGH": "🔴", "MEDIUM": "🟠", "LOW": "⚪"}.get(level, "📰")
    return (
        f"{emoji} <b>MARKET RADAR · {level}</b>\n\n"
        f"<b>{title}</b>\n\n"
        f"<b>Potentially relevant:</b> {assets}\n"
        f"<b>Why flagged:</b> {reason}\n\n"
        f"<b>Source:</b> {source}\n"
        f"<b>Published:</b> {published}\n"
        f"<b>Detected:</b> {detected}\n"
        f"<b>Feed-to-detection:</b> {delay}\n"
        f'<a href="{link}">Open original source</a>\n\n'
        "<i>Impact tags are screening hints, not trade signals.</i>"
    )
