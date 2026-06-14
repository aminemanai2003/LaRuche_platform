"""
MCP tools for the Financial Assistant agent.

All numbers come from the single canonical portfolio in agentkit.portfolio,
which the metrics library computes from calibrated inputs — so the figures the
agent reports match the orchestrator API, the dashboards, and the demo exactly.
"""

from __future__ import annotations

from typing import Any

from agentkit.mcp.tool import MCPTool, ToolResult
from agentkit.portfolio import GEO as _GEO
from agentkit.portfolio import SECTOR as _SECTOR
from agentkit.portfolio import TOP_DEALS as _TOP_DEALS
from agentkit.portfolio import get_metrics as _get_metrics

# ── MCP Tools ─────────────────────────────────────────────────────────────────


class PortfolioSummaryTool(MCPTool):
    @property
    def name(self) -> str:
        return "portfolio.summary"

    @property
    def description(self) -> str:
        return "Return high-level portfolio summary: AUM, TWR, profit, number of deals."

    @property
    def input_schema(self) -> dict[str, Any]:
        return {"type": "object", "properties": {}, "required": []}

    async def execute(self, **_kwargs: Any) -> ToolResult:
        m = _get_metrics()
        content = (
            f"Portfolio Summary:\n"
            f"  AUM: {m['aum_fmt']} ({m['num_deals']} deals)\n"
            f"  Total Profit: {m['profit_fmt']}\n"
            f"  ITD TWR: {m['twr_pct']:.2f}%\n"
            f"  Annualized Return: {m['annualized_pct']:.2f}%\n"
            f"  IRR: {m['irr_pct']:.2f}%\n"
            f"  Sharpe Ratio: {m['sharpe']:.2f}\n"
            f"  Volatility: {m['volatility_pct']:.2f}%"
        )
        return ToolResult(content=content)


class MetricsComputeTool(MCPTool):
    @property
    def name(self) -> str:
        return "metrics.compute"

    @property
    def description(self) -> str:
        return "Compute specific portfolio metrics: aum, twr, irr, sharpe, volatility, annualized."

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "metric": {
                    "type": "string",
                    "enum": ["aum", "twr", "irr", "sharpe", "volatility", "annualized", "all"],
                }
            },
            "required": ["metric"],
        }

    async def execute(self, metric: str = "all", **_kwargs: Any) -> ToolResult:
        m = _get_metrics()
        if metric == "aum":
            return ToolResult(content=f"AUM: {m['aum_fmt']}")
        if metric == "twr":
            return ToolResult(content=f"ITD TWR: {m['twr_pct']:.2f}%")
        if metric == "irr":
            return ToolResult(content=f"IRR: {m['irr_pct']:.2f}%" if m["irr_pct"] else "IRR: N/A")
        if metric == "sharpe":
            return ToolResult(content=f"Sharpe Ratio: {m['sharpe']:.2f}")
        if metric == "volatility":
            return ToolResult(content=f"Volatility: {m['volatility_pct']:.2f}%")
        if metric == "annualized":
            return ToolResult(content=f"Annualized Return: {m['annualized_pct']:.2f}%")
        # all
        return ToolResult(
            content=(
                f"AUM: {m['aum_fmt']} | TWR: {m['twr_pct']:.2f}% | "
                f"Annualized: {m['annualized_pct']:.2f}% | IRR: {m['irr_pct']:.2f}% | "
                f"Sharpe: {m['sharpe']:.2f} | Volatility: {m['volatility_pct']:.2f}%"
            )
        )


class GeographyBreakdownTool(MCPTool):
    @property
    def name(self) -> str:
        return "portfolio.geo_breakdown"

    @property
    def description(self) -> str:
        return "Return portfolio allocation by geography."

    @property
    def input_schema(self) -> dict[str, Any]:
        return {"type": "object", "properties": {}, "required": []}

    async def execute(self, **_kwargs: Any) -> ToolResult:
        lines = [f"  {k}: {v:.0f}%" for k, v in _GEO.items()]
        return ToolResult(content="Geographic breakdown:\n" + "\n".join(lines))


class SectorBreakdownTool(MCPTool):
    @property
    def name(self) -> str:
        return "portfolio.sector_breakdown"

    @property
    def description(self) -> str:
        return "Return portfolio allocation by asset class / sector."

    @property
    def input_schema(self) -> dict[str, Any]:
        return {"type": "object", "properties": {}, "required": []}

    async def execute(self, **_kwargs: Any) -> ToolResult:
        lines = [f"  {k}: {v:.0f}%" for k, v in _SECTOR.items()]
        return ToolResult(content="Sector / Asset-class breakdown:\n" + "\n".join(lines))


class TopDealsTool(MCPTool):
    @property
    def name(self) -> str:
        return "portfolio.top_deals"

    @property
    def description(self) -> str:
        return "Return the top deals ranked by MOIC."

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {"limit": {"type": "integer", "default": 5}},
            "required": [],
        }

    async def execute(self, limit: int = 5, **_kwargs: Any) -> ToolResult:
        top = _TOP_DEALS[:limit]
        lines = [
            f"  {i + 1}. {d['name']} — {d['moic']}x MOIC ({d['asset_class']}, {d['status']})"
            for i, d in enumerate(top)
        ]
        return ToolResult(content="Top deals by MOIC:\n" + "\n".join(lines))
