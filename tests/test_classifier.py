from market_radar.classifier import classify

def test_cpi_tags_gold_and_dollar():
    result = classify("US CPI inflation rises more than expected")
    assert result.level in {"HIGH", "CRITICAL"}
    assert "GOLD / XAUUSD" in result.assets
    assert "USD / DXY" in result.assets

def test_crypto_tags_crypto():
    result = classify("Bitcoin ETF sees major inflows")
    assert "CRYPTO" in result.assets

def test_plain_story_is_low():
    result = classify("A company opens a new office")
    assert result.level == "LOW"
