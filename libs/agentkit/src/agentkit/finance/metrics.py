"""
Portfolio financial metrics.

All functions are pure (no DB calls) — they take plain Python data
so they're fast, testable, and model-agnostic.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import NamedTuple

# ── Small data containers (no SQLAlchemy dependency) ─────────────────────────


class DealSnapshot(NamedTuple):
    nav: Decimal
    cost_basis: Decimal
    commitment: Decimal
    status: str  # "active" | "exited"


class CashflowRow(NamedTuple):
    date: date
    amount: float  # positive = outflow (investment), negative = inflow (distribution)


@dataclass
class PortfolioMetrics:
    aum: Decimal
    twr: float  # time-weighted return, e.g. 1.7865 = 178.65%
    twr_pct: float  # twr * 100
    annualized_return: float  # e.g. 0.0714 = 7.14%
    annualized_pct: float
    irr: float | None  # internal rate of return
    irr_pct: float | None
    sharpe: float
    volatility: float  # annualized std dev of returns
    total_profit: Decimal
    years: float  # inception-to-date years


# ── Core calculations ─────────────────────────────────────────────────────────


def compute_aum(deals: list[DealSnapshot]) -> Decimal:
    """Sum of NAV for all active deals."""
    return sum((d.nav for d in deals if d.status == "active"), Decimal(0))


def holding_period_years(inception: date, as_of: date | None = None) -> float:
    end = as_of or date.today()
    return (end - inception).days / 365.25


def compute_twr(period_returns: list[float]) -> float:
    """
    Time-Weighted Return from a list of sub-period HPRs.
    Each element is the HPR for that period, e.g. 0.05 = 5% gain.
    """
    result = 1.0
    for r in period_returns:
        result *= 1.0 + r
    return result - 1.0


def compute_annualized_return(twr: float, years: float) -> float:
    """Convert ITD TWR to annualized rate."""
    if years <= 0:
        return 0.0
    return float((1.0 + twr) ** (1.0 / years)) - 1.0


def compute_volatility(period_returns: list[float], periods_per_year: float = 12.0) -> float:
    """
    Annualized volatility (std dev * sqrt(periods_per_year)).
    Expects at least 2 data points.
    """
    n = len(period_returns)
    if n < 2:
        return 0.0
    mean = sum(period_returns) / n
    variance = sum((r - mean) ** 2 for r in period_returns) / (n - 1)
    return math.sqrt(variance * periods_per_year)


def compute_sharpe(
    annualized_return: float,
    volatility: float,
    risk_free: float = 0.03,
) -> float:
    """Sharpe ratio = (return - risk_free) / volatility."""
    if volatility == 0:
        return 0.0
    return (annualized_return - risk_free) / volatility


def compute_irr(cashflows: list[CashflowRow], guess: float = 0.1) -> float | None:
    """
    IRR via Newton-Raphson.
    cashflows: list of (date, amount) where amount > 0 = outflow (you invest),
               amount < 0 = inflow (you receive).
    Returns annual IRR or None if not converged.
    """
    if not cashflows:
        return None

    sorted_cf = sorted(cashflows, key=lambda c: c.date)
    t0 = sorted_cf[0].date
    # Time in years from first cashflow
    times = [(c.date - t0).days / 365.25 for c in sorted_cf]
    amounts = [c.amount for c in sorted_cf]

    def npv(rate: float) -> float:
        return float(sum(a / (1.0 + rate) ** t for a, t in zip(amounts, times, strict=False)))

    def dnpv(rate: float) -> float:
        return float(
            sum(-t * a / (1.0 + rate) ** (t + 1) for a, t in zip(amounts, times, strict=False))
        )

    rate = guess
    for _ in range(100):
        f = npv(rate)
        df = dnpv(rate)
        if abs(df) < 1e-12:
            break
        rate_new = rate - f / df
        if abs(rate_new - rate) < 1e-8:
            return rate_new
        rate = rate_new

    return rate if abs(npv(rate)) < 1.0 else None


def compute_portfolio_metrics(
    deals: list[DealSnapshot],
    period_returns: list[float],
    cashflows: list[CashflowRow],
    inception: date,
    risk_free: float = 0.03,
    as_of: date | None = None,
) -> PortfolioMetrics:
    """Compute all metrics in one call."""
    aum = compute_aum(deals)
    total_cost = sum(d.cost_basis for d in deals if d.status == "active")
    profit = aum - total_cost

    years = holding_period_years(inception, as_of)
    twr = compute_twr(period_returns)
    ann = compute_annualized_return(twr, years)
    vol = compute_volatility(period_returns)
    sharpe = compute_sharpe(ann, vol, risk_free)
    irr = compute_irr(cashflows)

    return PortfolioMetrics(
        aum=aum,
        twr=twr,
        twr_pct=round(twr * 100, 2),
        annualized_return=ann,
        annualized_pct=round(ann * 100, 2),
        irr=irr,
        irr_pct=round(irr * 100, 2) if irr is not None else None,
        sharpe=round(sharpe, 2),
        volatility=round(vol * 100, 2),
        total_profit=profit,
        years=round(years, 1),
    )
