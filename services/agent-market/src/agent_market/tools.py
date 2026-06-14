"""MCP tools for the Market-Data agent — backed by canonical agentkit.market data."""

from __future__ import annotations

from typing import Any

from agentkit.market import INDICATORS as _INDICATORS
from agentkit.market import QUOTES as _QUOTES
from agentkit.mcp.tool import MCPTool, ToolResult


class MarketQuoteTool(MCPTool):
    @property
    def name(self) -> str:
        return "market.quote"

    @property
    def description(self) -> str:
        return "Get current market price and daily change for a symbol."

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {"symbol": {"type": "string", "description": "e.g. SPX, AAPL, BTC"}},
            "required": ["symbol"],
        }

    async def execute(self, symbol: str = "SPX", **_kwargs: Any) -> ToolResult:
        key = symbol.upper()
        q = _QUOTES.get(key)
        if not q:
            return ToolResult(error=f"Symbol '{symbol}' not found")
        sign = "+" if q["change_pct"] >= 0 else ""
        content = (
            f"{q['name']} ({key}): {q['currency']} {q['price']:,.2f}  "
            f"({sign}{q['change_pct']:.2f}% today)"
        )
        return ToolResult(content=content)


class EconIndicatorTool(MCPTool):
    @property
    def name(self) -> str:
        return "econ.indicator"

    @property
    def description(self) -> str:
        return "Get an economic indicator value."

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "indicator": {
                    "type": "string",
                    "enum": list(_INDICATORS.keys()),
                    "description": "Economic indicator key",
                }
            },
            "required": ["indicator"],
        }

    async def execute(self, indicator: str = "us_gdp_growth", **_kwargs: Any) -> ToolResult:
        ind = _INDICATORS.get(indicator)
        if not ind:
            return ToolResult(error=f"Indicator '{indicator}' not found")
        content = f"{ind['name']}: {ind['value']}{ind['unit']}  (as of {ind['date']})"
        return ToolResult(content=content)


class MarketOverviewTool(MCPTool):
    @property
    def name(self) -> str:
        return "market.overview"

    @property
    def description(self) -> str:
        return "Return a summary of key market indices and economic conditions."

    @property
    def input_schema(self) -> dict[str, Any]:
        return {"type": "object", "properties": {}, "required": []}

    async def execute(self, **_kwargs: Any) -> ToolResult:
        lines = [
            f"  S&P 500: {_QUOTES['SPX']['price']:,.2f}  ({_QUOTES['SPX']['change_pct']:+.2f}%)",
            f"  Gold: ${_QUOTES['GLD']['price']:,.2f}/oz",
            f"  BTC: ${_QUOTES['BTC']['price']:,.0f}",
            f"  Fed Rate: {_INDICATORS['us_fed_rate']['value']}%",
            f"  10Y Yield: {_INDICATORS['us_10y_yield']['value']}%",
            f"  US Inflation: {_INDICATORS['us_inflation']['value']}%",
            f"  VIX: {_INDICATORS['vix']['value']}",
        ]
        return ToolResult(content="Market Overview:\n" + "\n".join(lines))
