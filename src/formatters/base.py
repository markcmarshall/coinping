"""Abstract base class for output formatters."""
from abc import ABC, abstractmethod
from typing import List

from src.models import CryptoData


class Formatter(ABC):
    """Abstract base class for output formatters."""

    @abstractmethod
    def format_single(self, crypto_data: CryptoData) -> str:
        """Format a single cryptocurrency data object.

        Args:
            crypto_data: CryptoData object to format

        Returns:
            Formatted string representation
        """
        pass

    @abstractmethod
    def format_multiple(self, crypto_data_list: List[CryptoData]) -> str:
        """Format multiple cryptocurrency data objects.

        Args:
            crypto_data_list: List of CryptoData objects to format

        Returns:
            Formatted string representation
        """
        pass
