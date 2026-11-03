# MARKET RADAR

A speed-first, free-first market-news collector that sends concise alerts to a Telegram channel.

**Important:** This starter uses RSS/Atom feeds with conditional HTTP requests. It is not an institutional newswire and cannot guarantee sub-second detection. The collector checks configured feeds every 10 seconds by default, but upstream publishers may update their feeds much later. The `detected_at` timestamp lets you measure our own collection delay.

## What is implemented

- Concurrent feed polling with `ETag` / `Last-Modified` support
- SQLite deduplication and persistence
- Basic impact classification and asset tagging
- Telegram channel delivery (text only; let Telegram handle phone sound)
- Original source URL, publication time, detection time and measured delay
- `/health` endpoint
- Startup notification and silent first-run backfill to avoid flooding
- No AI call in the hot path: classification stays fast and deterministic

## Architecture

```text
RSS / Atom feeds
      |
      v
Concurrent async collector (10s default)
      |
      v
Normalize + classify + deduplicate
      |
      +----> SQLite event store
      |
      v
Telegram Bot API
      |
      v
Your Telegram channel -> Android high-priority notification
```

For genuinely faster feeds, add a WebSocket / webhook adapter. Do not pretend a 10-second RSS poll is a 50ms institutional feed.

## Quick start (Windows, macOS, Linux, Termux)

1. Install Python 3.11 or newer.
2. Create a Telegram bot with `@BotFather`.
3. Add the bot to your private Telegram channel as an administrator with permission to post messages.
4. Copy `.env.example` to `.env` and fill in the token and channel ID.
5. Install and run:

```bash
python -m venv .venv
# Windows:
.venv\\Scripts\\activate
# macOS/Linux/Termux:
source .venv/bin/activate

pip install -r requirements.txt
python -m market_radar
```

Open `http://127.0.0.1:8080/health` to confirm the process is alive.

### Get your channel ID

- Create a private Telegram channel and add your bot as an administrator.
- Post a message in the channel.
- Use a Telegram bot-update viewer or a small `getUpdates` helper to identify the channel ID. Channel IDs commonly look like `-100...`.
- Never paste your bot token into a public issue, chat, screenshot, or GitHub commit.

## Configuration

See `.env.example`.

- `POLL_INTERVAL_SECONDS=10`: fast polling can still be delayed by upstream RSS refresh cadence. Start at 10; don't hammer providers at 1 second.
- `BOOTSTRAP_SILENT=true`: first launch stores currently visible headlines without sending a backlog.
- `SEND_STARTUP_MESSAGE=true`: sends a one-time startup confirmation.
- `MIN_ALERT_LEVEL=MEDIUM`: choose `LOW`, `MEDIUM`, `HIGH`, or `CRITICAL`.
- `DATABASE_PATH=data/market_radar.sqlite3`

## Feed sources

The initial list is deliberately small and mostly official / publisher feeds. Feed URLs can change or become rate-limited; monitor `/health` and logs.

- Federal Reserve press releases
- US Treasury press releases
- SEC press releases
- European Central Bank press releases
- CoinDesk RSS
- Cointelegraph RSS

Add more feeds in `market_radar/sources.py`. Prefer official feeds, exchange announcements, regulator releases and publisher-provided feeds. Respect terms of service and rate limits.

## Latency measurement

Every alert includes:
- `Published`: timestamp supplied by the publisher/feed (may be missing or inaccurate)
- `Detected`: when this collector first saw the item
- `Feed-to-detection`: measured difference when a publication timestamp exists

This does **not** measure the time from the original announcement to the publisher's feed. For a fair benchmark, compare the same event across original source timestamps and our detection timestamp over many events.

## Free hosting reality

A continuously connected collector needs a process that stays awake. Free serverless cron often runs on a schedule (commonly one minute or longer), and free web hosts may sleep. Those are poor fits for a speed-first alert system.

Free-first deployment options:
1. Run on an always-on Windows PC / spare machine while testing.
2. Investigate an Oracle Cloud Always Free VM if available to your account and region; availability and signup verification vary.
3. Use free cloud hosting only after checking sleep, background-worker and usage restrictions.

GitHub Actions is excellent for tests and builds, but scheduled workflows are not a low-latency always-on worker.

## Roadmap

- [ ] Validate all RSS endpoints and record per-source freshness
- [ ] Add exchange-native WebSocket adapters (where public and permitted)
- [ ] Add official webhook adapters where offered
- [ ] Add X / Truth Social adapters only through lawful, documented access
- [ ] Add source health scoring and reconnect/backoff
- [ ] Add optional AI explanation as a second message, never blocking the first alert
- [ ] Add market price confirmation (separate data source)
- [ ] Add alert replay and latency dashboard

## Safety

Market Radar reports information, not trade instructions. A headline's likely impact can reverse or be priced in already. Verify important events at the original source and confirm with live price action before trading.
