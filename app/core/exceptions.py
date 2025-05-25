"""Custom exception for Currency Converter API.

This module defines the exception hierarchy used throughout the application.
- CurrencyConverterError: Base exception class.
- InvalidCurrencyError: for invalid currency codes.
- ExternalAPIError: for external API failures.
- InvalidAmountError: for invalid amount values.
- UserNotFoundError: for user lookup failures.
"""

class CurrencyConverterError(Exception):
    """Base exception for Currency Converter API."""
    def __init__(self, message: str, status_code: int = 500) -> None:
        """Initialize CurrencyConverterException.

        Args:
            message: The error message to be displayed
            status_code: HTTP status code for the error. Defaults to 500.
        """
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class InvalidCurrencyError(CurrencyConverterError):
    """Exception raised when currency code is invalid."""
    def __init__(self, currency_code: str) -> None:
        """Initialize InvalidCurrencyError.

        Args:
            currency_code: The invalid currency code that caused the exception.
        """
        message = f"Invalid currency code: {currency_code}"
        super().__init__(message, status_code=400)


class ExternalAPIError(CurrencyConverterError):
    """Exception raised when external API call fails."""
    def __init__(self, message: str = "External API call failed") -> None:
        """Initialize ExternalAPIError.

        Args:
            message: Custom error message for the API failure. Defaults to "External API call failed".
        """
        super().__init__(message, status_code=503)


class InvalidAmountError(CurrencyConverterError):
    """Exception raised when amount is invalid."""
    def __init__(self, amount: float) -> None:
        """Initialize InvalidAmountError.

        Args:
            amount: The invalid amount value that caused the exception.
        """
        message = f"Invalid amount: {amount}"
        super().__init__(message, status_code=400)


class UserNotFoundError(CurrencyConverterError):
    """Exception raised when user is not found."""
    def __init__(self, user_id: str) -> None:
        """Initialize UserNotFoundError.

        Args:
            user_id: The ID of the user that was not found.
        """
        message = f"User not found: {user_id}"
        super().__init__(message, status_code=404)
