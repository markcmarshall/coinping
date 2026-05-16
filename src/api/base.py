"""Abstract base class for cryptocurrency API handlers."""
from abc import ABC, abstractmethod
from typing import List

from src.models import CryptoData


class CryptoAPIHandler(ABC):
    """Abstract base class for cryptocurrency data providers."""

    @abstractmethod
    def fetch_token(self, symbol: str) -> CryptoData:
        """Fetch data for a single cryptocurrency token.

        Args:
            symbol: Token symbol (e.g., 'BTC', 'ETH')

        Returns:
            CryptoData object with token information

        Raises:
            TokenNotFoundError: If token is not found
            APIError: If API returns an error
            NetworkError: If network request fails
        """
        pass

    @abstractmethod
    def fetch_multiple(self, symbols: List[str]) -> List[CryptoData]:
        """Fetch data for multiple cryptocurrency tokens.

        Args:
            symbols: List of token symbols

        Returns:
            List of CryptoData objects

        Raises:
            APIError: If API returns an error
            NetworkError: If network request fails
        """
        pass

    @abstractmethod
    def validate_token(self, symbol: str) -> bool:
        """Check if a token symbol exists.

        Args:
            symbol: Token symbol to validate

        Returns:
            True if token exists, False otherwise
        """
        pass

    @abstractmethod
    def get_supported_tokens(self) -> List[str]:
        """Get list of all supported token symbols.

        Returns:
            List of available token symbols
        """
        pass
