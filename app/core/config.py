import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """

    # API settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Currency Exchange API"
    PROJECT_VERSION: str = "1.0.0"
    PROJECT_DESCRIPTION: str = (
        "Currency Converter API with transaction history tracking"
    )
    PROJECT_DOCS_URL: str = "/docs"
    PROJECT_REDOC_URL: str = "/redoc"

    # Exchange rate settings
    EXCHANGE_RATE_API_URL: str = "http://api.exchangeratesapi.io/latest"
    EXCHANGE_RATE_API_KEY: str = os.getenv("EXCHANGE_RATE_API_KEY", "your_api_key_here")
    EXCHANGE_RATE_API_BASE_CURRENCY: str = "EUR"

    # Cache settings
    ECHANGE_RATE_CACHE_TTL: int = (
        3600  # Time to live for cached exchange rates in seconds
    )

    # Supported currencies
    SUPPORTED_CURRENCIES: list[str] = [
        "USD",
        "EUR",
        "GBP",
        "JPY",
        "AUD",
        "CAD",
        "CHF",
        "CNY",
        "SEK",
        "NZD",
        "BRL",
    ]

    # Database settings
    DATABASE_NAME: str = "currency_converter.db"

    class Config:
        """
        Configuration for Pydantic settings.
        """

        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        use_enum_values = True
        validate_assignment = True


settings = Settings()
