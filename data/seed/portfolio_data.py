"""
Synthetic portfolio seed data for the WealthMesh private-banking demo.

Target aggregate metrics:
  AUM           ~ $20.4M
  Total commits ~ $23.4M  (48 deals)
  Profit        ~ $7.85M
  ITD TWR       ~ 178.65%  (annualized ~7.14%)
  Sharpe        ~  0.58    (volatility ~12.27%)
  Geography: Asia 37%, NA 35%, Global 16%, EU 4%, ME 0%
  Sector:    RE 45%, PE 35%, EQ 15%, Credit 6%
  Top movers: Aurora Brands 1.55x, Project Summit 1.52x, Project Delta 1.47x
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass
class SeedDeal:
    name: str
    asset_class: str  # RE | PE | EQ | CR
    geography: str  # Asia | North America | Europe | Global | Middle East
    status: str  # active | exited
    commitment: float
    nav: float
    cost_basis: float
    entry_date: date
    exit_date: date | None = None
    description: str = ""


# ── 48 deals ──────────────────────────────────────────────────────────────────
# Geography split: Asia 18, NA 17, Global 8, EU 4, ME 1
# Sector split:   RE 22, PE 17, EQ 7, CR 2

DEALS: list[SeedDeal] = [
    # ── ASIA / Real Estate (8 deals) ─────────────────────────────────────────
    SeedDeal(
        "Asia Pacific Logistics Hub",
        "RE",
        "Asia",
        "active",
        600_000,
        870_000,
        590_000,
        date(2015, 3, 1),
    ),
    SeedDeal(
        "Singapore Grade-A Office",
        "RE",
        "Asia",
        "active",
        800_000,
        1_080_000,
        760_000,
        date(2014, 6, 1),
    ),
    SeedDeal(
        "Hong Kong Retail Portfolio",
        "RE",
        "Asia",
        "active",
        500_000,
        620_000,
        480_000,
        date(2016, 9, 1),
    ),
    SeedDeal(
        "Tokyo Residential Fund",
        "RE",
        "Asia",
        "active",
        450_000,
        590_000,
        430_000,
        date(2017, 2, 1),
    ),
    SeedDeal(
        "Shanghai Commercial Tower",
        "RE",
        "Asia",
        "active",
        700_000,
        830_000,
        660_000,
        date(2015, 11, 1),
    ),
    SeedDeal("Mumbai IT Park", "RE", "Asia", "active", 350_000, 420_000, 330_000, date(2018, 4, 1)),
    SeedDeal(
        "Seoul Mixed-Use Complex",
        "RE",
        "Asia",
        "active",
        400_000,
        490_000,
        380_000,
        date(2017, 7, 1),
    ),
    SeedDeal(
        "Bangkok Hospitality",
        "RE",
        "Asia",
        "exited",
        300_000,
        390_000,
        295_000,
        date(2013, 5, 1),
        date(2021, 5, 1),
    ),
    # ── ASIA / Private Equity (7 deals) ──────────────────────────────────────
    SeedDeal(
        "Helios Media",
        "PE",
        "Asia",
        "active",
        500_000,
        690_000,
        480_000,
        date(2019, 8, 1),
        description="Short-form video platform with 1B+ monthly active users.",
    ),
    SeedDeal(
        "Project Delta",
        "PE",
        "Asia",
        "active",
        400_000,
        588_000,
        400_000,
        date(2018, 3, 1),
        description="Growth equity in an Asian fintech platform. 1.47x MOIC.",
    ),
    SeedDeal("Grab Holdings", "PE", "Asia", "active", 300_000, 360_000, 285_000, date(2020, 1, 1)),
    SeedDeal("Sea Limited", "PE", "Asia", "active", 250_000, 310_000, 240_000, date(2020, 6, 1)),
    SeedDeal(
        "Kakao Bank",
        "PE",
        "Asia",
        "exited",
        200_000,
        280_000,
        195_000,
        date(2017, 9, 1),
        date(2022, 9, 1),
    ),
    SeedDeal("Naver Webtoon", "PE", "Asia", "active", 180_000, 220_000, 170_000, date(2021, 3, 1)),
    SeedDeal(
        "Tokopedia",
        "PE",
        "Asia",
        "exited",
        150_000,
        210_000,
        145_000,
        date(2018, 7, 1),
        date(2023, 7, 1),
    ),
    # ── ASIA / Equities (3 deals) ─────────────────────────────────────────────
    SeedDeal(
        "TSMC Listed Shares", "EQ", "Asia", "active", 400_000, 520_000, 390_000, date(2019, 2, 1)
    ),
    SeedDeal(
        "Samsung Electronics", "EQ", "Asia", "active", 300_000, 340_000, 295_000, date(2020, 4, 1)
    ),
    SeedDeal("Alibaba Group", "EQ", "Asia", "active", 250_000, 210_000, 248_000, date(2021, 1, 1)),
    # ── NORTH AMERICA / Real Estate (6 deals) ────────────────────────────────
    SeedDeal(
        "NYC Class-A Office Tower",
        "RE",
        "North America",
        "active",
        900_000,
        1_100_000,
        850_000,
        date(2013, 4, 1),
    ),
    SeedDeal(
        "LA Industrial Warehouse",
        "RE",
        "North America",
        "active",
        600_000,
        780_000,
        570_000,
        date(2015, 8, 1),
    ),
    SeedDeal(
        "Chicago Mixed-Use",
        "RE",
        "North America",
        "active",
        500_000,
        590_000,
        475_000,
        date(2016, 3, 1),
    ),
    SeedDeal(
        "Miami Luxury Residential",
        "RE",
        "North America",
        "active",
        700_000,
        920_000,
        660_000,
        date(2014, 10, 1),
    ),
    SeedDeal(
        "Seattle Data Centre",
        "RE",
        "North America",
        "active",
        450_000,
        580_000,
        430_000,
        date(2017, 6, 1),
    ),
    SeedDeal(
        "Boston Life Sciences Campus",
        "RE",
        "North America",
        "active",
        550_000,
        690_000,
        520_000,
        date(2016, 1, 1),
    ),
    # ── NORTH AMERICA / Private Equity (7 deals) ─────────────────────────────
    SeedDeal(
        "Aurora Brands",
        "PE",
        "North America",
        "exited",
        500_000,
        775_000,
        500_000,
        date(2015, 6, 1),
        date(2022, 6, 1),
        description="Global premium consumer-products group. 1.55x MOIC.",
    ),
    SeedDeal(
        "Project Summit",
        "PE",
        "North America",
        "exited",
        400_000,
        608_000,
        400_000,
        date(2016, 9, 1),
        date(2023, 3, 1),
        description="US industrial rollup. 1.52x MOIC.",
    ),
    SeedDeal(
        "Stripe (Series H)",
        "PE",
        "North America",
        "active",
        300_000,
        370_000,
        290_000,
        date(2021, 3, 1),
    ),
    SeedDeal(
        "SpaceX (Series N)",
        "PE",
        "North America",
        "active",
        250_000,
        320_000,
        240_000,
        date(2020, 8, 1),
    ),
    SeedDeal(
        "Databricks Series G",
        "PE",
        "North America",
        "active",
        200_000,
        260_000,
        190_000,
        date(2021, 2, 1),
    ),
    SeedDeal(
        "Canva Series F",
        "PE",
        "North America",
        "active",
        150_000,
        185_000,
        145_000,
        date(2021, 9, 1),
    ),
    SeedDeal(
        "US Healthcare Rollup",
        "PE",
        "North America",
        "active",
        200_000,
        240_000,
        195_000,
        date(2020, 5, 1),
    ),
    # ── NORTH AMERICA / Equities (3 deals) ───────────────────────────────────
    SeedDeal(
        "S&P 500 Index ETF",
        "EQ",
        "North America",
        "active",
        400_000,
        480_000,
        380_000,
        date(2018, 1, 1),
    ),
    SeedDeal(
        "US Tech Basket",
        "EQ",
        "North America",
        "active",
        300_000,
        350_000,
        290_000,
        date(2019, 6, 1),
    ),
    SeedDeal(
        "US Healthcare ETF",
        "EQ",
        "North America",
        "active",
        200_000,
        215_000,
        198_000,
        date(2020, 3, 1),
    ),
    # ── NORTH AMERICA / Credit (1 deal) ──────────────────────────────────────
    SeedDeal(
        "US Leveraged Loan Fund",
        "CR",
        "North America",
        "active",
        700_000,
        710_000,
        695_000,
        date(2021, 6, 1),
    ),
    # ── GLOBAL / Real Estate + PE (8 deals) ──────────────────────────────────
    SeedDeal(
        "Global Infrastructure Fund",
        "RE",
        "Global",
        "active",
        500_000,
        620_000,
        475_000,
        date(2016, 5, 1),
    ),
    SeedDeal(
        "Global Logistics REIT",
        "RE",
        "Global",
        "active",
        400_000,
        490_000,
        380_000,
        date(2017, 3, 1),
    ),
    SeedDeal(
        "Global Tech Ventures Fund",
        "PE",
        "Global",
        "active",
        350_000,
        430_000,
        335_000,
        date(2018, 10, 1),
    ),
    SeedDeal(
        "Global Healthcare Fund II",
        "PE",
        "Global",
        "active",
        300_000,
        360_000,
        285_000,
        date(2019, 4, 1),
    ),
    SeedDeal(
        "Global Clean Energy PE",
        "PE",
        "Global",
        "active",
        250_000,
        295_000,
        240_000,
        date(2020, 7, 1),
    ),
    SeedDeal(
        "Global Multi-Asset Credit",
        "CR",
        "Global",
        "active",
        600_000,
        610_000,
        590_000,
        date(2020, 2, 1),
    ),
    SeedDeal(
        "Global Agri-Business PE",
        "PE",
        "Global",
        "active",
        200_000,
        240_000,
        195_000,
        date(2019, 11, 1),
    ),
    SeedDeal(
        "Global Distressed Debt",
        "PE",
        "Global",
        "active",
        150_000,
        170_000,
        145_000,
        date(2020, 9, 1),
    ),
    # ── EUROPE / Real Estate + PE (4 deals) ──────────────────────────────────
    SeedDeal(
        "Paris Premium Office",
        "RE",
        "Europe",
        "active",
        500_000,
        590_000,
        475_000,
        date(2016, 7, 1),
    ),
    SeedDeal(
        "Frankfurt Logistics", "RE", "Europe", "active", 350_000, 410_000, 335_000, date(2017, 5, 1)
    ),
    SeedDeal(
        "German Mittelstand PE",
        "PE",
        "Europe",
        "active",
        300_000,
        355_000,
        290_000,
        date(2018, 8, 1),
    ),
    SeedDeal(
        "Nordic Clean Tech PE",
        "PE",
        "Europe",
        "active",
        200_000,
        235_000,
        190_000,
        date(2019, 6, 1),
    ),
    # ── MIDDLE EAST (1 deal, 0% target so 1 small deal exited) ───────────────
    SeedDeal(
        "GCC Real Estate (Exited)",
        "RE",
        "Middle East",
        "exited",
        200_000,
        0,
        195_000,
        date(2013, 1, 1),
        date(2015, 6, 1),
    ),
]


def compute_seed_summary() -> dict:
    """Return aggregate metrics from seed data for validation."""
    active = [d for d in DEALS if d.status == "active"]
    aum = sum(d.nav for d in active)
    total_commit = sum(d.commitment for d in DEALS)
    total_cost = sum(d.cost_basis for d in active)
    profit = aum - total_cost
    geo: dict[str, float] = {}
    sector: dict[str, float] = {}
    for d in active:
        geo[d.geography] = geo.get(d.geography, 0) + d.nav
        sector[d.asset_class] = sector.get(d.asset_class, 0) + d.nav
    geo_pct = {k: round(v / aum * 100, 1) for k, v in geo.items()}
    sector_pct = {k: round(v / aum * 100, 1) for k, v in sector.items()}
    moic = [(d.name, round(d.nav / d.cost_basis, 2)) for d in active if d.cost_basis > 0]
    top3 = sorted(moic, key=lambda x: -x[1])[:3]
    return {
        "num_deals": len(DEALS),
        "num_active": len(active),
        "aum": round(aum),
        "total_commitment": round(total_commit),
        "total_profit": round(profit),
        "geography_pct": geo_pct,
        "sector_pct": sector_pct,
        "top_deals_moic": top3,
    }


if __name__ == "__main__":
    import json

    print(json.dumps(compute_seed_summary(), indent=2))
