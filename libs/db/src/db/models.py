"""SQLAlchemy ORM models for the Agentic Mesh wealth-management domain."""

from __future__ import annotations

import enum
import uuid
from datetime import UTC, date, datetime
from decimal import Decimal

from sqlalchemy import (
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def _uuid() -> str:
    return str(uuid.uuid4())


def _now() -> datetime:
    return datetime.now(UTC)


class Base(DeclarativeBase):
    pass


# ── Enumerations ──────────────────────────────────────────────────────────────


class UserRole(str, enum.Enum):
    CLIENT = "client"
    ADVISOR = "advisor"
    ADMIN = "admin"


class ClientTier(str, enum.Enum):
    HNWI = "HNWI"
    UHNWI = "UHNWI"


class AssetClass(str, enum.Enum):
    REAL_ESTATE = "RE"
    PRIVATE_EQUITY = "PE"
    EQUITIES = "EQ"
    CREDIT = "CR"


class Geography(str, enum.Enum):
    ASIA = "Asia"
    NORTH_AMERICA = "North America"
    EUROPE = "Europe"
    GLOBAL = "Global"
    MIDDLE_EAST = "Middle East"


class DealStatus(str, enum.Enum):
    ACTIVE = "active"
    EXITED = "exited"


class CashflowType(str, enum.Enum):
    CONTRIBUTION = "contribution"
    DISTRIBUTION = "distribution"
    NAV = "nav"


class MessageRole(str, enum.Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


# ── Tables ────────────────────────────────────────────────────────────────────


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    keycloak_id: Mapped[str | None] = mapped_column(String(36), unique=True)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.CLIENT)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    client: Mapped[Client | None] = relationship("Client", back_populates="user", uselist=False)


class Client(Base):
    __tablename__ = "clients"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    tier: Mapped[ClientTier] = mapped_column(Enum(ClientTier), default=ClientTier.HNWI)
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    user: Mapped[User] = relationship("User", back_populates="client")
    portfolios: Mapped[list[Portfolio]] = relationship("Portfolio", back_populates="client")
    conversations: Mapped[list[Conversation]] = relationship(
        "Conversation", back_populates="client"
    )


class Portfolio(Base):
    __tablename__ = "portfolios"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    client_id: Mapped[str] = mapped_column(ForeignKey("clients.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    inception_date: Mapped[date] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    client: Mapped[Client] = relationship("Client", back_populates="portfolios")
    deals: Mapped[list[Deal]] = relationship("Deal", back_populates="portfolio")


class Deal(Base):
    __tablename__ = "deals"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    portfolio_id: Mapped[str] = mapped_column(ForeignKey("portfolios.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    asset_class: Mapped[AssetClass] = mapped_column(Enum(AssetClass), nullable=False)
    geography: Mapped[Geography] = mapped_column(Enum(Geography), nullable=False)
    status: Mapped[DealStatus] = mapped_column(Enum(DealStatus), default=DealStatus.ACTIVE)
    commitment: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    nav: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    cost_basis: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    entry_date: Mapped[date] = mapped_column(Date, nullable=False)
    exit_date: Mapped[date | None] = mapped_column(Date)
    description: Mapped[str | None] = mapped_column(Text)

    portfolio: Mapped[Portfolio] = relationship("Portfolio", back_populates="deals")
    cashflows: Mapped[list[Cashflow]] = relationship("Cashflow", back_populates="deal")


class Cashflow(Base):
    __tablename__ = "cashflows"
    __table_args__ = (UniqueConstraint("deal_id", "date", "type", name="uq_cashflow"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    deal_id: Mapped[str] = mapped_column(ForeignKey("deals.id"), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    type: Mapped[CashflowType] = mapped_column(Enum(CashflowType), nullable=False)

    deal: Mapped[Deal] = relationship("Deal", back_populates="cashflows")


class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    client_id: Mapped[str] = mapped_column(ForeignKey("clients.id"), nullable=False)
    channel: Mapped[str] = mapped_column(String(20), default="web")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    client: Mapped[Client] = relationship("Client", back_populates="conversations")
    messages: Mapped[list[Message]] = relationship("Message", back_populates="conversation")


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    conversation_id: Mapped[str] = mapped_column(ForeignKey("conversations.id"), nullable=False)
    role: Mapped[MessageRole] = mapped_column(Enum(MessageRole), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    agent_id: Mapped[str | None] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    conversation: Mapped[Conversation] = relationship("Conversation", back_populates="messages")
