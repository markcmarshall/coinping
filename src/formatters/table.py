"""Table formatter for cryptocurrency data output."""
from typing import List

from tabulate import tabulate

from src.formatters.base import Formatter
from src.models import CryptoData


class TableFormatter(Formatter):
    """Format cryptocurrency data as a pretty ASCII table."""

    def format_single(self, crypto_data: CryptoData) -> str:
        """Format a single cryptocurrency data object as a table.

        Args:
            crypto_data: CryptoData object to format

        Returns:
            Formatted table string
        """
        return self.format_multiple([crypto_data])

    def format_multiple(self, crypto_data_list: List[CryptoData]) -> str:
        """Format multiple cryptocurrency data objects as a table.

        Args:
            crypto_data_list: List of CryptoData objects to format

        Returns:
            Formatted table string
        """
        table_data = []

        for crypto in crypto_data_list:
            row = [
                crypto.symbol,
                crypto.name,
                self._format_price(crypto.current_price),
                self._format_change(crypto.change_24h_percent),
                self._format_market_cap(crypto.market_cap),
                self._format_rank(crypto.market_cap_rank),
            ]
            table_data.append(row)

        headers = [
            "Symbol",
            "Name",
            "Price (USD)",
            "24h Change",
            "Market Cap (USD)",
            "Rank",
        ]

        return tabulate(table_data, headers=headers, tablefmt="simple")

    @staticmethod
    def _format_price(price: float) -> str:
        """Format price with currency symbol and thousands separator."""
        if price is None:
            return "N/A"
        return f"${price:,.2f}"

    @staticmethod
    def _format_change(change: float) -> str:
        """Format 24h change percentage."""
        if change is None:
            return "N/A"
        sign = "+" if change >= 0 else ""
        return f"{sign}{change:.2f}%"

    @staticmethod
    def _format_market_cap(market_cap: float) -> str:
        """Format market cap with abbreviations for large numbers."""
        if market_cap is None:
            return "N/A"

        if market_cap >= 1e12:
            return f"${market_cap / 1e12:.2f}T"
        elif market_cap >= 1e9:
            return f"${market_cap / 1e9:.2f}B"
        elif market_cap >= 1e6:
            return f"${market_cap / 1e6:.2f}M"
        else:
            return f"${market_cap:,.2f}"

    @staticmethod
    def _format_rank(rank: int) -> str:
        """Format market cap rank."""
        if rank is None:
            return "N/A"
        return str(rank)
