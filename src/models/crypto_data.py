"""Data class for cryptocurrency information."""
from dataclasses import dataclass
from typing import Optional


@dataclass
class CryptoData:
    """Represents cryptocurrency data from the API."""

    symbol: str
    name: str
    current_price: float
    market_cap: Optional[float]
    market_cap_rank: Optional[int]
    change_24h_percent: Optional[float]
    circulating_supply: Optional[float]
    total_supply: Optional[float]
    ath: Optional[float]
    atl: Optional[float]
    last_updated: str

    def __str__(self) -> str:
        """Return a formatted string representation."""
        change = (
            "N/A"
            if self.change_24h_percent is None
            else f"{self.change_24h_percent:+.2f}%"
        )
        return (
            f"{self.symbol} ({self.name}) - ${self.current_price:,.2f} "
            f"({change})"
        )

    def __repr__(self) -> str:
        """Return detailed string representation."""
        return (
            f"CryptoData(symbol={self.symbol!r}, name={self.name!r}, "
            f"current_price={self.current_price}, market_cap={self.market_cap}, "
            f"market_cap_rank={self.market_cap_rank}, "
            f"change_24h_percent={self.change_24h_percent})"
        )
