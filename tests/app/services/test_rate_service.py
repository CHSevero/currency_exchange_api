"""Tests for the rate service module.

This module contains unit tests for rate service functionality,
including service methods, error handling, and edge cases.
"""
from collections.abc import Generator
from datetime import UTC, datetime
from decimal import Decimal

import pytest
import respx
from httpx import Response

from app.core.config import settings
from app.core.exceptions import ExternalAPIError, InvalidCurrencyError
from app.models.models import ExchangeRate
from app.services.rate_service import RateService


@pytest.fixture
def rate_service() -> RateService:
    """Create a test RateService."""
    return RateService()


@pytest.mark.asyncio
async def test_get_exchange_rate_same_currency(
    rate_service: RateService,
    db_session: Generator
) -> None:
    """Test exchange rate for same currency should be 1."""
    rate = await rate_service.get_exchange_rate("EUR", "EUR", db_session)
    assert rate == Decimal("1")


@pytest.mark.asyncio
async def test_get_exchange_rate_invalid_currency(
    rate_service: RateService,
    db_session: Generator
) -> None:
    """Test invalid currency raises exception."""
    with pytest.raises(InvalidCurrencyError):
        await rate_service.get_exchange_rate("INVALID", "EUR", db_session)


@pytest.mark.asyncio
async def test_get_exchange_rate_successful(
    rate_service: RateService,
    db_session: Generator,
    mock_rates_response: dict[str, Decimal]
) -> None:
    """Test successful exchange rate retrieval."""
    with respx.mock as respx_mock:
        respx_mock.get(f"{settings.EXCHANGE_RATE_API_URL}").mock(
            return_value=Response(200, json=mock_rates_response)
        ).side_effect = lambda r: Response(200, json=mock_rates_response)

        rate = await rate_service.get_exchange_rate("USD", "EUR", db_session)
        assert isinstance(rate, Decimal)
        assert float(rate) == pytest.approx(1 / 1.18, rel=1e-6)


@pytest.mark.asyncio
async def test_get_exchange_rate_api_error(
    rate_service: RateService,
    db_session: Generator
) -> None:
    """Test handling of API errors."""
    with respx.mock as respx_mock:
        respx_mock.get(settings.EXCHANGE_RATE_API_URL).mock(
            return_value=Response(500,json={"error": "Internal Server Error"})
        )

        # First call without cached data should raise exception
        with pytest.raises(ExternalAPIError):
            await rate_service.get_exchange_rate("USD", "EUR", db_session)


@pytest.mark.asyncio
async def test_get_exchange_rate_from_cache(
    rate_service: RateService,
    db_session: Generator,
    mock_rates_response: dict[str, Decimal]
) -> None:
    """Test exchange rate retrieval from cache."""
    with respx.mock as respx_mock:
        # First call to populate cache
        respx_mock.get(settings.EXCHANGE_RATE_API_URL).mock(
            return_value=Response(200, json=mock_rates_response)
        )
        rate1 = await rate_service.get_exchange_rate("USD", "EUR", db_session)

        # Second call should use cache
        rate2 = await rate_service.get_exchange_rate("USD", "EUR", db_session)

        assert rate1 == rate2


@pytest.mark.asyncio
async def test_get_exchange_rate_from_db(
    rate_service: RateService,
    db_session: Generator
) -> None:
    """Test exchange rate retrivel from database."""
    # Add test data to database
    db_rate = ExchangeRate(
        base_currency="EUR",
        rates={"USD": "1.18", "JPY": "129.55", "BRL": "6.35", "EUR": "1.0"},
        last_updated=datetime.now(UTC),
    )
    db_session.add(db_rate)
    db_session.commit()

    with respx.mock as respx_mock:
        # Make API call fail to force DB fallback
        respx_mock.get(settings.EXCHANGE_RATE_API_URL).mock(
            return_value=Response(500, json={"error": "Internal Server Error"})
        )

        # Clear cache to force DB lookup
        rate_service.cache = {}
        rate = await rate_service.get_exchange_rate("USD", "EUR", db_session)
        assert isinstance(rate, Decimal)
        assert float(rate) == pytest.approx(1 / 1.18, rel=1e-6)
