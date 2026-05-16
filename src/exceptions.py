"""Custom exception classes for cryptocurrency data fetching."""


class CryptoFetcherError(Exception):
    """Base exception for all crypto fetcher errors."""
    pass


class TokenNotFoundError(CryptoFetcherError):
    """Raised when a requested token cannot be found."""
    pass


class APIError(CryptoFetcherError):
    """Raised when the API returns an error response."""
    pass


class NetworkError(CryptoFetcherError):
    """Raised when there's a network connectivity issue."""
    pass
