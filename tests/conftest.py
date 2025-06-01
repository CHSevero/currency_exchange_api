"""Test configuration and shared fixtures for the Currency Exchange API.

This module contains pytest fixtures and configuration settings that are shared across multiple
test files. It includes setup and teardown functions for test database connections, API clients,
and other utilities.
"""

from collections.abc import Generator
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, set_engine
from app.main import app


@pytest.fixture
def client() -> TestClient:
    """"Fixture for creating a test client for the FastAPI application."""
    with TestClient(app) as client:
        yield client


@pytest.fixture
def engine() -> Generator:
    """Create a new test database engine for each test."""
    test_engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    Base.metadata.create_all(bind=test_engine)
    set_engine(test_engine)
    yield test_engine

    Base.metadata.drop_all(bind=test_engine)
    test_engine.dispose()


@pytest.fixture
def db_session(engine: Engine) -> Generator:
    """Create a test database session."""
    session = sessionmaker(bind=engine)
    session = session()
    yield session
    session.rollback()
    session.close()


@pytest.fixture
def mock_rates_response() -> dict[str, Decimal]:
    """Mock response from exchange rates API."""
    return {
        "base": "EUR",
        "rates": {"USD": 1.18, "JPY": 129.55, "BRL": 6.35, "EUR": 1.0},
        "success": True,
        "timestamp": 1620000000,
    }


@pytest.fixture
def test_data() -> dict:
    """Common test data."""
    return {
        "user_id": "test_user",
        "from_currency": "USD",
        "to_currency": "EUR",
        "amount": "100.00",
        "exchange_rate": "0.85",
        "base_currency": "EUR",
        "rates": {"USD": "1.18", "JPY": "129.55", "BRL": "6.35"},
    }
