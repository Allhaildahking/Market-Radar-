"""Feed registry. Prefer official feeds and publisher-provided RSS/Atom endpoints."""

FEEDS = [
    {
        "name": "Federal Reserve",
        "url": "https://www.federalreserve.gov/feeds/press_all.xml",
        "category": "central_bank",
    },
    {
        "name": "US Treasury",
        "url": "https://home.treasury.gov/news/press-releases/rss",
        "category": "government",
    },
    {
        "name": "US SEC",
        "url": "https://www.sec.gov/news/pressreleases.rss",
        "category": "regulator",
    },
    {
        "name": "European Central Bank",
        "url": "https://www.ecb.europa.eu/rss/press.html",
        "category": "central_bank",
    },
    {
        "name": "CoinDesk",
        "url": "https://www.coindesk.com/arc/outboundfeeds/rss/",
        "category": "crypto_media",
    },
    {
        "name": "Cointelegraph",
        "url": "https://cointelegraph.com/rss",
        "category": "crypto_media",
    },
]
