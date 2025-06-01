"""SQLAlchemy models for Currency Converter API.

This module defines the database models used in the application.
- Transaction: Stores currency conversion transactions.
- ExchangeRate: Stores exchange rates as backup data.
"""
from datetime import UTC, datetime

from sqlalchemy import JSON, Column, DateTime, Integer, Numeric, String

from app.core.database import Base


class Transaction(Base):
    """SQLAlchemy model for currency conversion transaction."""

    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    source_currency = Column(String(3))
    target_currency = Column(String(3))
    source_amount = Column(Numeric(18, 2))
    target_amount = Column(Numeric(18, 2))
    exchange_rate = Column(Numeric(18, 2))
    timestamp = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC)
    )


class ExchangeRate(Base):
    """SQLAlchemy model for exchange rates as backup."""

    __tablename__ = "exchange_rates"

    id = Column(Integer, primary_key=True, index=True)
    base_currency = Column(String(3))
    rates = Column(JSON)
    last_updated = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC)
    )
