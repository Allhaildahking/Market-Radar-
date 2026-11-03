import asyncio
import logging
from aiohttp import web, ClientSession, TCPConnector

from . import config
from .collector import Collector
from .sources import FEEDS
from .storage import Store
from .telegram import Telegram

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
log = logging.getLogger("market_radar")

async def run():
    if not config.TELEGRAM_BOT_TOKEN or not config.TELEGRAM_CHAT_ID:
        raise SystemExit("Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in .env before starting.")

    store = Store(config.DATABASE_PATH)
    connector = TCPConnector(limit=20, ttl_dns_cache=300, keepalive_timeout=30)
    async with ClientSession(connector=connector) as session:
        telegram = Telegram(session, config.TELEGRAM_BOT_TOKEN, config.TELEGRAM_CHAT_ID)
        if config.SEND_STARTUP_MESSAGE:
            try:
                await telegram.startup()
            except Exception:
                log.exception("Could not send startup message")

        collector = Collector(
            session=session,
            store=store,
            telegram=telegram,
            feeds=FEEDS,
            interval=config.POLL_INTERVAL_SECONDS,
            timeout=config.REQUEST_TIMEOUT_SECONDS,
            min_level=config.MIN_ALERT_LEVEL,
            bootstrap_silent=config.BOOTSTRAP_SILENT,
        )

        async def health(_request):
            return web.json_response({
                "status": "ok",
                "service": "market-radar",
                "poll_interval_seconds": config.POLL_INTERVAL_SECONDS,
                "sources": collector.source_health,
            })

        app = web.Application()
        app.router.add_get("/health", health)
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, config.HOST, config.PORT)
        await site.start()
        log.info("Health endpoint listening on %s:%s/health", config.HOST, config.PORT)

        try:
            await collector.run_forever()
        finally:
            await runner.cleanup()
            store.close()

if __name__ == "__main__":
    asyncio.run(run())
