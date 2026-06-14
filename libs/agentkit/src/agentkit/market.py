"""
Canonical market data — single source of truth for the market agent and the
orchestrator's /api/market endpoint. Static mock data; swap for a free API later.
"""

from __future__ import annotations

from typing import Any

QUOTES: dict[str, dict[str, Any]] = {
    "SPX": {"name": "S&P 500", "price": 5247.49, "change_pct": 0.42, "currency": "USD"},
    "AAPL": {"name": "Apple Inc.", "price": 189.30, "change_pct": -0.18, "currency": "USD"},
    "TSLA": {"name": "Tesla Inc.", "price": 175.22, "change_pct": 1.05, "currency": "USD"},
    "BTC": {"name": "Bitcoin", "price": 67_450.00, "change_pct": 2.33, "currency": "USD"},
    "GLD": {"name": "Gold (oz)", "price": 2328.60, "change_pct": 0.15, "currency": "USD"},
    "USDEUR": {"name": "USD/EUR", "price": 0.9285, "change_pct": -0.05, "currency": "EUR"},
}

INDICATORS: dict[str, dict[str, Any]] = {
    "us_gdp_growth": {"name": "US GDP Growth (YoY)", "value": 2.8, "unit": "%", "date": "2024-Q4"},
    "us_inflation": {
        "name": "US CPI Inflation (YoY)",
        "value": 3.1,
        "unit": "%",
        "date": "2024-12",
    },
    "us_fed_rate": {"name": "US Fed Funds Rate", "value": 5.25, "unit": "%", "date": "2024-12"},
    "us_10y_yield": {
        "name": "US 10-Year Treasury Yield",
        "value": 4.55,
        "unit": "%",
        "date": "2024-12",
    },
    "global_growth": {
        "name": "IMF Global Growth Forecast",
        "value": 3.2,
        "unit": "%",
        "date": "2025",
    },
    "vix": {"name": "VIX Volatility Index", "value": 14.8, "unit": "points", "date": "2024-12"},
}


def get_market() -> dict[str, Any]:
    """Return quotes + indicators as JSON-friendly lists for the web/mobile UI."""
    quotes = [
        {"symbol": sym, "name": q["name"], "price": q["price"], "change_pct": q["change_pct"]}
        for sym, q in QUOTES.items()
    ]
    indicators = [
        {"key": k, "name": i["name"], "value": i["value"], "unit": i["unit"], "date": i["date"]}
        for k, i in INDICATORS.items()
    ]
    return {"quotes": quotes, "indicators": indicators}
