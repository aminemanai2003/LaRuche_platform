"""
Seed script — loads the 48-deal synthetic portfolio into the database.

Usage:
    uv run python data/seed/seed_portfolio.py

Requires a running Postgres (docker-compose.dev.yml) and the DB package installed.
Creates: 1 user, 1 client, 1 portfolio, 48 deals, 48 contribution cashflows.
"""

from __future__ import annotations

import asyncio
import os
import sys
from datetime import UTC, datetime
from decimal import Decimal

# Allow running from project root without install
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../libs/db/src"))

from db.models import (
    AssetClass,
    Cashflow,
    CashflowType,
    Client,
    ClientTier,
    Deal,
    DealStatus,
    Geography,
    Portfolio,
    User,
    UserRole,
)
from db.session import get_session, init_db
from portfolio_data import DEALS, SeedDeal

_ASSET_CLASS_MAP = {
    "RE": AssetClass.REAL_ESTATE,
    "PE": AssetClass.PRIVATE_EQUITY,
    "EQ": AssetClass.EQUITIES,
    "CR": AssetClass.CREDIT,
}

_GEOGRAPHY_MAP = {
    "Asia": Geography.ASIA,
    "North America": Geography.NORTH_AMERICA,
    "Europe": Geography.EUROPE,
    "Global": Geography.GLOBAL,
    "Middle East": Geography.MIDDLE_EAST,
}


def _now() -> datetime:
    return datetime.now(UTC)


def _deal_row(seed: SeedDeal, portfolio_id: str) -> Deal:
    return Deal(
        portfolio_id=portfolio_id,
        name=seed.name,
        asset_class=_ASSET_CLASS_MAP[seed.asset_class],
        geography=_GEOGRAPHY_MAP[seed.geography],
        status=DealStatus.EXITED if seed.status == "exited" else DealStatus.ACTIVE,
        commitment=Decimal(str(seed.commitment)),
        nav=Decimal(str(seed.nav)),
        cost_basis=Decimal(str(seed.cost_basis)),
        entry_date=seed.entry_date,
        exit_date=seed.exit_date,
        description=seed.description or None,
    )


async def seed() -> None:
    init_db()

    async for session in get_session():
        # User
        # keycloak_id matches the fixed user id in infra/keycloak/realm-wealth.json,
        # so a Keycloak login (sub) maps deterministically to this client's portfolio.
        user = User(
            email="client@wealthmesh.local",
            keycloak_id="00000000-0000-0000-0000-000000000002",
            role=UserRole.CLIENT,
            created_at=_now(),
        )
        session.add(user)
        await session.flush()

        # Client
        client = Client(
            user_id=user.id,
            code="CLT-001",
            name="Meridian Family Office",
            tier=ClientTier.UHNWI,
            currency="USD",
            created_at=_now(),
        )
        session.add(client)
        await session.flush()

        # Portfolio (inception 2013-01-01 — earliest deal)
        portfolio = Portfolio(
            client_id=client.id,
            name="Meridian Core Portfolio",
            currency="USD",
            inception_date=DEALS[0].entry_date,
            created_at=_now(),
        )
        session.add(portfolio)
        await session.flush()

        # Deals + contribution cashflows
        for seed_deal in DEALS:
            deal = _deal_row(seed_deal, portfolio.id)
            session.add(deal)
            await session.flush()

            cf = Cashflow(
                deal_id=deal.id,
                date=seed_deal.entry_date,
                amount=Decimal(str(seed_deal.commitment)),
                type=CashflowType.CONTRIBUTION,
            )
            session.add(cf)

        await session.commit()
        print(f"Seeded: 1 user, 1 client, 1 portfolio, {len(DEALS)} deals")
        break


if __name__ == "__main__":
    asyncio.run(seed())
