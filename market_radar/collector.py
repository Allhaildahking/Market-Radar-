import asyncio
import hashlib
import logging
import time
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

import aiohttp
import feedparser

from .classifier import classify, LEVELS
from .telegram import format_alert

log = logging.getLogger("market_radar")

def iso_from_entry(entry):
    parsed = entry.get("published_parsed") or entry.get("updated_parsed")
    if parsed:
        import calendar
        stamp = calendar.timegm(parsed)
        return datetime.fromtimestamp(stamp, timezone.utc)
    raw = entry.get("published") or entry.get("updated")
    if raw:
        try:
            dt = parsedate_to_datetime(raw)
            return dt.astimezone(timezone.utc)
        except Exception:
            pass
    return None

def clean_text(value: str, limit=500) -> str:
    import re
    from html import unescape
    value = re.sub(r"<[^>]+>", " ", value or "")
    value = unescape(value)
    return re.sub(r"\\s+", " ", value).strip()[:limit]

def normalize(source: str, entry: dict) -> dict | None:
    title = clean_text(entry.get("title", ""), 350)
    link = (entry.get("link") or "").strip()
    if not title or not link:
        return None
    summary = clean_text(entry.get("summary", ""), 500)
    published_dt = iso_from_entry(entry)
    published = published_dt.isoformat() if published_dt else None
    identity = entry.get("id") or entry.get("guid") or link
    item_id = hashlib.sha256(f"{source}|{identity}".encode()).hexdigest()
    result = classify(title, summary)
    now = datetime.now(timezone.utc)
    delay = None
    if published_dt:
        seconds = max(0, (now - published_dt).total_seconds())
        delay = f"{seconds:.1f}s"
    return {
        "id": item_id, "source": source, "title": title, "summary": summary,
        "link": link, "published": published, "detected": now.isoformat(),
        "delay": delay, "level": result.level, "assets": result.assets,
        "reason": result.reason,
    }

class Collector:
    def __init__(self, session, store, telegram, feeds, interval, timeout,
                 min_level="MEDIUM", bootstrap_silent=True):
        self.session = session
        self.store = store
        self.telegram = telegram
        self.feeds = feeds
        self.interval = interval
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.min_level = LEVELS.get(min_level, 2)
        self.bootstrap_silent = bootstrap_silent
        self.bootstrapped = set()
        self.source_health = {}

    async def poll_one(self, feed):
        name, url = feed["name"], feed["url"]
        headers = self.store.source_headers(name)
        headers["User-Agent"] = "MarketRadar/0.1 (RSS reader)"
        started = time.perf_counter()
        try:
            async with self.session.get(url, headers=headers, timeout=self.timeout) as response:
                if response.status == 304:
                    self.store.update_source(name, success=True)
                    self.source_health[name] = {"status": "ok", "last_ms": round((time.perf_counter()-started)*1000)}
                    return
                response.raise_for_status()
                body = await response.read()
                parsed = feedparser.parse(body)
                self.store.update_source(
                    name,
                    etag=response.headers.get("ETag"),
                    modified=response.headers.get("Last-Modified"),
                    success=True,
                )
            entries = parsed.entries
            if name not in self.bootstrapped and self.bootstrap_silent:
                for entry in entries:
                    item = normalize(name, entry)
                    if item and not self.store.has_seen(item["id"]):
                        self.store.save_item(item)
                self.bootstrapped.add(name)
                log.info("Seeded %s existing items from %s", len(entries), name)
            else:
                self.bootstrapped.add(name)
                for entry in reversed(entries):
                    item = normalize(name, entry)
                    if not item or self.store.has_seen(item["id"]):
                        continue
                    self.store.save_item(item)
                    if LEVELS[item["level"]] >= self.min_level:
                        await self.telegram.send(format_alert(item))
            self.source_health[name] = {
                "status": "ok",
                "last_ms": round((time.perf_counter()-started)*1000),
                "entries": len(entries),
            }
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            log.warning("Feed %s failed: %s", name, exc)
            self.store.update_source(name, error=str(exc)[:250])
            self.source_health[name] = {"status": "error", "error": str(exc)[:180]}

    async def run_forever(self):
        log.info("Starting %d feeds; interval=%ss", len(self.feeds), self.interval)
        while True:
            started = time.perf_counter()
            await asyncio.gather(*(self.poll_one(feed) for feed in self.feeds))
            elapsed = time.perf_counter() - started
            await asyncio.sleep(max(0.5, self.interval - elapsed))
