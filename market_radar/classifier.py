from dataclasses import dataclass

LEVELS = {"LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}

@dataclass
class Classification:
    level: str
    score: int
    assets: list[str]
    reason: str

RULES = [
    (4, ["emergency rate", "unexpected rate", "rate cut", "rate hike", "default", "invasion", "missile strike", "military strike", "bank collapse", "market halt", "capital controls"]),
    (3, ["federal reserve", "fomc", "interest rate", "inflation", "cpi", "pce", "nonfarm", "payroll", "unemployment", "ecb", "boj", "boe", "central bank", "sanction", "ceasefire", "opec", "treasury yield", "debt ceiling"]),
    (2, ["gold", "bullion", "xauusd", "bitcoin", "btc", "ethereum", "crypto", "oil", "crude", "dollar", "dxy", "forex", "earnings", "sec", "etf", "exchange"]),
]

ASSET_TERMS = {
    "GOLD / XAUUSD": ["gold", "bullion", "xauusd", "precious metal", "inflation", "cpi", "pce", "federal reserve", "fed", "interest rate", "fomc", "treasury yield"],
    "USD / DXY": ["dollar", "dxy", "federal reserve", "fed", "cpi", "pce", "payroll", "treasury yield"],
    "FOREX": ["forex", "fx", "eurusd", "gbpusd", "usdjpy", "ecb", "boj", "boe"],
    "CRYPTO": ["bitcoin", "btc", "ethereum", "eth", "crypto", "binance", "stablecoin", "token"],
    "OIL / ENERGY": ["oil", "crude", "opec", "brent", "wti", "natural gas"],
    "EQUITIES": ["stock", "shares", "nasdaq", "s&p", "dow", "earnings", "sec", "nvidia", "apple", "microsoft"],
}

def classify(title: str, summary: str = "") -> Classification:
    text = f"{title} {summary}".lower()
    score = 1
    matched = []
    for points, terms in RULES:
        found = [term for term in terms if term in text]
        if found:
            score = max(score, points)
            matched.extend(found[:3])

    assets = [
        asset for asset, terms in ASSET_TERMS.items()
        if any(term in text for term in terms)
    ]
    if not assets:
        assets = ["GENERAL MARKETS"]

    level = next(name for name, value in LEVELS.items() if value == score)
    reason = ", ".join(dict.fromkeys(matched)) if matched else "General market headline"
    return Classification(level=level, score=score, assets=assets, reason=reason)
