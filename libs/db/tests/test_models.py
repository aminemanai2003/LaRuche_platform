"""Async DB model tests using in-memory SQLite via aiosqlite."""

from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import Decimal

import pytest
from db.models import (
    AssetClass,
    Base,
    Cashflow,
    CashflowType,
    Client,
    ClientTier,
    Conversation,
    Deal,
    DealStatus,
    Geography,
    Message,
    MessageRole,
    Portfolio,
    User,
    UserRole,
)
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

DATABASE_URL = "sqlite+aiosqlite://"


@pytest.fixture
async def session():
    engine = create_async_engine(DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as s:
        yield s
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


# ── helpers ───────────────────────────────────────────────────────────────────


def _now() -> datetime:
    return datetime.now(UTC)


async def _make_user(session: AsyncSession, email: str = "test@example.com") -> User:
    user = User(email=email, role=UserRole.CLIENT, created_at=_now())
    session.add(user)
    await session.flush()
    return user


async def _make_client(session: AsyncSession, user: User) -> Client:
    client = Client(
        user_id=user.id,
        code="CLT001",
        name="Meridian Family Office",
        tier=ClientTier.UHNWI,
        currency="USD",
        created_at=_now(),
    )
    session.add(client)
    await session.flush()
    return client


async def _make_portfolio(session: AsyncSession, client: Client) -> Portfolio:
    portfolio = Portfolio(
        client_id=client.id,
        name="Main Portfolio",
        currency="USD",
        inception_date=date(2013, 1, 1),
        created_at=_now(),
    )
    session.add(portfolio)
    await session.flush()
    return portfolio


# ── User tests ────────────────────────────────────────────────────────────────


async def test_create_user(session: AsyncSession):
    user = await _make_user(session)
    assert user.id is not None
    assert user.email == "test@example.com"
    assert user.role == UserRole.CLIENT


async def test_user_unique_email(session: AsyncSession):
    await _make_user(session, "dupe@example.com")
    import sqlalchemy.exc

    with pytest.raises((sqlalchemy.exc.IntegrityError, Exception)):
        await _make_user(session, "dupe@example.com")
        await session.flush()


# ── Client tests ──────────────────────────────────────────────────────────────


async def test_create_client(session: AsyncSession):
    user = await _make_user(session)
    client = await _make_client(session, user)
    assert client.id is not None
    assert client.name == "Meridian Family Office"
    assert client.tier == ClientTier.UHNWI


# ── Portfolio tests ───────────────────────────────────────────────────────────


async def test_create_portfolio(session: AsyncSession):
    user = await _make_user(session)
    client = await _make_client(session, user)
    portfolio = await _make_portfolio(session, client)
    assert portfolio.id is not None
    assert portfolio.inception_date == date(2013, 1, 1)


# ── Deal tests ────────────────────────────────────────────────────────────────


async def test_create_deal(session: AsyncSession):
    user = await _make_user(session)
    client = await _make_client(session, user)
    portfolio = await _make_portfolio(session, client)

    deal = Deal(
        portfolio_id=portfolio.id,
        name="Project Delta",
        asset_class=AssetClass.PRIVATE_EQUITY,
        geography=Geography.ASIA,
        status=DealStatus.ACTIVE,
        commitment=Decimal("400000.00"),
        nav=Decimal("588000.00"),
        cost_basis=Decimal("400000.00"),
        entry_date=date(2018, 3, 1),
        description="Growth equity in Asian fintech platform. 1.47x MOIC.",
    )
    session.add(deal)
    await session.flush()

    assert deal.id is not None
    assert deal.nav == Decimal("588000.00")
    moic = float(deal.nav) / float(deal.cost_basis)
    assert abs(moic - 1.47) < 0.01


async def test_deal_exited_status(session: AsyncSession):
    user = await _make_user(session)
    client = await _make_client(session, user)
    portfolio = await _make_portfolio(session, client)

    deal = Deal(
        portfolio_id=portfolio.id,
        name="Aurora Brands",
        asset_class=AssetClass.PRIVATE_EQUITY,
        geography=Geography.NORTH_AMERICA,
        status=DealStatus.EXITED,
        commitment=Decimal("500000.00"),
        nav=Decimal("775000.00"),
        cost_basis=Decimal("500000.00"),
        entry_date=date(2015, 6, 1),
        exit_date=date(2022, 6, 1),
    )
    session.add(deal)
    await session.flush()
    assert deal.status == DealStatus.EXITED
    assert deal.exit_date == date(2022, 6, 1)


# ── Cashflow tests ────────────────────────────────────────────────────────────


async def test_create_cashflow(session: AsyncSession):
    user = await _make_user(session)
    client = await _make_client(session, user)
    portfolio = await _make_portfolio(session, client)
    deal = Deal(
        portfolio_id=portfolio.id,
        name="Test Deal",
        asset_class=AssetClass.REAL_ESTATE,
        geography=Geography.ASIA,
        commitment=Decimal("100000"),
        nav=Decimal("120000"),
        cost_basis=Decimal("100000"),
        entry_date=date(2020, 1, 1),
    )
    session.add(deal)
    await session.flush()

    cf = Cashflow(
        deal_id=deal.id,
        date=date(2020, 1, 1),
        amount=Decimal("100000"),
        type=CashflowType.CONTRIBUTION,
    )
    session.add(cf)
    await session.flush()
    assert cf.id is not None
    assert cf.type == CashflowType.CONTRIBUTION


# ── Conversation + Message tests ──────────────────────────────────────────────


async def test_conversation_and_messages(session: AsyncSession):
    user = await _make_user(session)
    client = await _make_client(session, user)

    conv = Conversation(client_id=client.id, channel="web", created_at=_now())
    session.add(conv)
    await session.flush()

    msg = Message(
        conversation_id=conv.id,
        role=MessageRole.USER,
        content="What is my portfolio AUM?",
        created_at=_now(),
    )
    session.add(msg)
    await session.flush()

    assert msg.id is not None
    assert msg.role == MessageRole.USER


async def test_assistant_message(session: AsyncSession):
    user = await _make_user(session)
    client = await _make_client(session, user)
    conv = Conversation(client_id=client.id, channel="mobile", created_at=_now())
    session.add(conv)
    await session.flush()

    msg = Message(
        conversation_id=conv.id,
        role=MessageRole.ASSISTANT,
        content="Your AUM is $20.4M across 48 deals.",
        agent_id="agent-financial",
        created_at=_now(),
    )
    session.add(msg)
    await session.flush()
    assert msg.agent_id == "agent-financial"
