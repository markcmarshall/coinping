"""JSON formatter for cryptocurrency data output."""
import json
from typing import List

from src.formatters.base import Formatter
from src.models import CryptoData


class JSONFormatter(Formatter):
    """Format cryptocurrency data as JSON."""

    def format_single(self, crypto_data: CryptoData) -> str:
        """Format a single cryptocurrency data object as JSON.

        Args:
            crypto_data: CryptoData object to format

        Returns:
            JSON string representation
        """
        return self.format_multiple([crypto_data])

    def format_multiple(self, crypto_data_list: List[CryptoData]) -> str:
        """Format multiple cryptocurrency data objects as JSON.

        Args:
            crypto_data_list: List of CryptoData objects to format

        Returns:
            JSON string representation
        """
        data = {}

        for crypto in crypto_data_list:
            data[crypto.symbol] = {
                "name": crypto.name,
                "current_price": crypto.current_price,
                "market_cap": crypto.market_cap,
                "market_cap_rank": crypto.market_cap_rank,
                "change_24h_percent": crypto.change_24h_percent,
                "circulating_supply": crypto.circulating_supply,
                "total_supply": crypto.total_supply,
                "ath": crypto.ath,
                "atl": crypto.atl,
                "last_updated": crypto.last_updated,
            }

        return json.dumps(data, indent=2)
