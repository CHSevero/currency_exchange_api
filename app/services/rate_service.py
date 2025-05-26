"""Service layer module for handling currency exchange rate operations.

This module provides:
- RateService: Main service class for exchange rate operations
- Exchange rate caching with configurable TTL
- Fallback to database when API is unavailable
- Precision handling for monetary calculations

The service uses an external API for real-time rates and implements
a multi-layer fallback strategy (cache -> database -> error) for reliability.
"""
import logging
from datetime import UTC, datetime, timedelta
from decimal import Decimal, getcontext
from http import HTTPStatus

import httpx
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import ExternalAPIError, InvalidCurrencyError
from app.models import ExchangeRate

# Set decimal precision for monetary calculations
getcontext().prec = 15

logger = logging.getLogger(__name__)


class RateService:
    """Service to handle exchange rate operations."""
    def __init__(self) -> None:
        """Initialize the RateService.

        Uses configuration from settings:
        - EXCHANGE_RATE_API_URL: Base URL for the exchange rate API
        - EXCHANGE_RATE_API_KEY: API key for authentication
        - EXCHANGE_RATE_API_BASE_CURRENCY: Base currency for rate calculations
        - EXCHANGE_RATE_CACHE_TTL: Time-to-live for cached rates in seconds
        """
        self.base_url = settings.EXCHANGE_RATE_API_URL
        self.api_key = settings.EXCHANGE_RATE_API_KEY
        self.base_currency = settings.EXCHANGE_RATE_API_BASE_CURRENCY
        self.ttl = settings.ECHANGE_RATE_CACHE_TTL
        self.cache = {}

    async def get_exchange_rate(self, from_currency: str, to_currency: str, db: Session) -> Decimal:
        """Get exchange rate between two currencies.

        Args:
            from_currency: Source currency code.
            to_currency: Target currency code.
            db: Database session for fallback storage.

        Returns:
            Decimal: Exchange rate from `from_currency` to `to_currency`.

        Raises:
            InvalidCurrencyError: If the currency is not supported.
            ExternalAPIError: If external API call fails.
        """
        # Validate currencies
        for currency in [from_currency, to_currency]:
            if not self.is_valid_currency(currency):
                raise InvalidCurrencyError(currency)

        # Same currency conversion
        if from_currency == to_currency:
            return Decimal("1")

        # Get rates with EUR as base
        rates = self._get_rates(db)

        # Calculate exchange rate
        if from_currency == self.base_currency:
            rate = rates[to_currency]
        elif to_currency == self.base_currency:
            rate = Decimal("1") / rates[from_currency]
        else:
            rate = rates[to_currency] / rates[from_currency]

        # Set a reasonable precision
        return rate.quantize(Decimal("0.000000001"))


    async def _get_rates(self, db: Session) -> dict[str, Decimal]:
        """Get all exchange rates with caching.

        Returns:
            dict: Dictionary with currency codes as keys and rates as values.

        Raises:
            ExternalAPIError: If external API call fails.
        """
        # Check if rates are in cache and not expired
        if self.base_currency in self.cache:
            cached_data = self.cache[self.base_currency]
            if datetime.now(UTC) < cached_data["expires_at"]:
                return cached_data["rates"]

        try:
            # Fetch from external API
            logger.info("Fetching exchange rates from external API")
            rates = await self._fetch_from_external_api()
        except Exception as e:
            logger.exception("Error fetching exchange rates")

            # Try to use cached rates even if expired
            if self.base_currency in self.cache:
                logger.warning("Using expired cached exchange rates")
                return self.cache[self.base_currency]["rates"]

            # Try to use rates from the database
            db_rates = self._get_rates_from_db(db)
            if db_rates:
                logger.warning("Using exchange rates from database")
                return db_rates

            # If all eslse fails, raise an error
            error_msg = f"Failed to get exchange rates:{e!s}"
            raise ExternalAPIError(error_msg) from e
        else:
            # Cache the rates
            self.cache[self.base_currency] = {
                "rates": rates,
                "expires_at": datetime.now(UTC) + timedelta(seconds=self.ttl),
            }

            # Save to database as fallback
            self._save_rates_to_db(db, rates)

            return rates


    async def _fecth_from_external_api(self) -> dict[str, Decimal]:
        """Fetch exchange rates from external API.

        Returns:
            Dictionary with currency codes as keys and rates as values
        """
        params = {"base": self.base_currency, "access_key": self.api_key}

        async with httpx.AsyncClient() as client:
            response = await client.get(self.base_url, params=params)
            if response.status_code != HTTPStatus.OK:
                error_msg = f"API return status code {response.status_code}"
                raise ExternalAPIError(error_msg)

            data = response.json()
            if "rates" not in data:
                error_msg = "Invalid response from exchange rate API"
                raise ExternalAPIError(error_msg)

            # Convert float rates to Decimal
            return {
                currency: Decimal(str(rate)) for currency, rate in data["rates"].items()
            }


    def _save_rates_to_db(self, db: Session, rates: dict[str, Decimal]) -> None:
        """Save exchange rates to database as backup.

        Args:
            db: Database session
            rates: Dictionary with currency codes as keys and rates as values
        """
        try:
            # Convert Decimal to string to ensure proper serialization
            str_rates = {currency: str(rate) for currency, rate in rates.items()}

            exchange_rate = ExchangeRate(
                base_currency=self.base_currency,
                rates=str_rates,
                last_updated=datetime.now(UTC),
            )

            db.add(exchange_rate)
            db.commit()
        except Exception:
            logger.exception("Error saving exchange rates to database")
            db.rollback()


    def _get_rates_from_db(self, db: Session) -> None | dict[str, Decimal]:
        """Get exchange rates from database.

        Args:
            db: Database session

        Returns:
            Optional[Dict[str, Decimal]]: Dictionary with currency codes as keys and rates as values
        """
        try:
            # Get the most recent rates
            exchange_rate = (
                db.query(ExchangeRate)
                .filter(ExchangeRate.base_currency == self.base_currency)
                .order_by(ExchangeRate.last_updated.desc())
                .first()
            )

            if exchange_rate:
                # Convert string rates back to Decimal
                return {
                    currency: Decimal(rate)
                    for currency, rate in exchange_rate.items()
                }

        except Exception:
            logger.exception("Error retrienving exchange rates from database")
