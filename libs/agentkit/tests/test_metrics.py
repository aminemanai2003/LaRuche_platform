"""Unit tests for agentkit.finance.metrics — all values hand-computed."""

from __future__ import annotations

import math
from datetime import date
from decimal import Decimal

from agentkit.finance.metrics import (
    CashflowRow,
    DealSnapshot,
    compute_annualized_return,
    compute_aum,
    compute_irr,
    compute_portfolio_metrics,
    compute_sharpe,
    compute_twr,
    compute_volatility,
    holding_period_years,
)

# ── AUM ───────────────────────────────────────────────────────────────────────


def test_aum_active_only():
    deals = [
        DealSnapshot(Decimal("1000"), Decimal("900"), Decimal("1000"), "active"),
        DealSnapshot(Decimal("500"), Decimal("450"), Decimal("500"), "exited"),
        DealSnapshot(Decimal("750"), Decimal("700"), Decimal("750"), "active"),
    ]
    assert compute_aum(deals) == Decimal("1750")


def test_aum_empty():
    assert compute_aum([]) == Decimal("0")


def test_aum_all_exited():
    deals = [DealSnapshot(Decimal("1000"), Decimal("900"), Decimal("1000"), "exited")]
    assert compute_aum(deals) == Decimal("0")


# ── TWR ───────────────────────────────────────────────────────────────────────


def test_twr_simple():
    # (1.10)(0.95)(1.08) - 1 = 1.1286 - 1 = 0.1286
    result = compute_twr([0.10, -0.05, 0.08])
    assert abs(result - (1.10 * 0.95 * 1.08 - 1.0)) < 1e-9


def test_twr_single_period():
    assert abs(compute_twr([0.20]) - 0.20) < 1e-9


def test_twr_empty():
    assert compute_twr([]) == 0.0


def test_twr_all_flat():
    assert compute_twr([0.0, 0.0, 0.0]) == 0.0


# ── Annualized return ─────────────────────────────────────────────────────────


def test_annualized_return_178pct_over_13_years():
    # 178.65% TWR over 13 years -> annualized = (2.7865)^(1/13) - 1 ~ 8.2%
    twr = 1.7865
    years = 13.0
    ann = compute_annualized_return(twr, years)
    expected = (1.0 + twr) ** (1.0 / years) - 1.0
    assert abs(ann - expected) < 1e-9
    assert 0.07 < ann < 0.10  # between 7% and 10%


def test_annualized_return_zero_years():
    assert compute_annualized_return(1.0, 0) == 0.0


# ── Volatility ────────────────────────────────────────────────────────────────


def test_volatility_known_values():
    # returns = [0.05, -0.03, 0.07, -0.01, 0.04]
    returns = [0.05, -0.03, 0.07, -0.01, 0.04]
    mean = sum(returns) / len(returns)
    var = sum((r - mean) ** 2 for r in returns) / (len(returns) - 1)
    expected = math.sqrt(var * 12)  # default periods_per_year=12
    result = compute_volatility(returns)
    assert abs(result - expected) < 1e-9


def test_volatility_single_point():
    assert compute_volatility([0.05]) == 0.0


def test_volatility_empty():
    assert compute_volatility([]) == 0.0


# ── Sharpe ───────────────────────────────────────────────────────────────────


def test_sharpe_known():
    # annualized return 10%, vol 12%, risk-free 3% -> (0.10-0.03)/0.12 = 0.5833
    result = compute_sharpe(0.10, 0.12, 0.03)
    assert abs(result - (0.07 / 0.12)) < 1e-9


def test_sharpe_zero_volatility():
    assert compute_sharpe(0.10, 0.0) == 0.0


# ── IRR ───────────────────────────────────────────────────────────────────────


def test_irr_simple():
    # Invest 1000 on year 0, receive 1200 on year 1 -> IRR = 20%
    cfs = [
        CashflowRow(date(2020, 1, 1), 1000.0),  # outflow (invest)
        CashflowRow(date(2021, 1, 1), -1200.0),  # inflow (receive)
    ]
    result = compute_irr(cfs)
    assert result is not None
    assert abs(result - 0.20) < 0.01


def test_irr_empty():
    assert compute_irr([]) is None


def test_irr_two_year():
    # Invest 1000, get 0 at year 1, get 1210 at year 2 -> IRR = 10%
    cfs = [
        CashflowRow(date(2020, 1, 1), 1000.0),
        CashflowRow(date(2021, 1, 1), 0.0),
        CashflowRow(date(2022, 1, 1), -1210.0),
    ]
    result = compute_irr(cfs)
    assert result is not None
    assert abs(result - 0.10) < 0.01


# ── Holding period ────────────────────────────────────────────────────────────


def test_holding_period_1_year():
    start = date(2020, 1, 1)
    end = date(2021, 1, 1)
    years = holding_period_years(start, end)
    assert abs(years - 1.0) < 0.01


# ── compute_portfolio_metrics integration ─────────────────────────────────────


def test_portfolio_metrics_smoke():
    deals = [
        DealSnapshot(Decimal("10_000"), Decimal("8_000"), Decimal("10_000"), "active"),
        DealSnapshot(Decimal("5_000"), Decimal("4_500"), Decimal("5_000"), "active"),
    ]
    period_returns = [0.05, -0.02, 0.08, 0.03, -0.01, 0.06, 0.04, -0.03, 0.07, 0.02, 0.05, 0.01]
    cashflows = [
        CashflowRow(date(2022, 1, 1), 10_000.0),
        CashflowRow(date(2022, 6, 1), 5_000.0),
        CashflowRow(date(2023, 1, 1), -15_000.0),
    ]
    m = compute_portfolio_metrics(
        deals, period_returns, cashflows, date(2022, 1, 1), as_of=date(2023, 1, 1)
    )
    assert m.aum == Decimal("15_000")
    assert m.twr_pct > 0
    assert m.sharpe != 0
    assert m.years > 0
