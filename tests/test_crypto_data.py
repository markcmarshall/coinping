"""Tests for CryptoData model."""
import pytest

from src.models import CryptoData


def test_crypto_data_creation():
    """Test creating a CryptoData object."""
    crypto = CryptoData(
        symbol="BTC",
        name="Bitcoin",
        current_price=65234.50,
        market_cap=1285432000000,
        market_cap_rank=1,
        change_24h_percent=2.34,
        circulating_supply=21000000,
        total_supply=21000000,
        ath=69000.00,
        atl=100.00,
        last_updated="2026-05-15T12:00:00Z",
    )

    assert crypto.symbol == "BTC"
    assert crypto.name == "Bitcoin"
    assert crypto.current_price == 65234.50
    assert crypto.market_cap == 1285432000000
    assert crypto.change_24h_percent == 2.34


def test_crypto_data_str_representation():
    """Test string representation of CryptoData."""
    crypto = CryptoData(
        symbol="ETH",
        name="Ethereum",
        current_price=3428.75,
        market_cap=411234000000,
        market_cap_rank=2,
        change_24h_percent=1.12,
        circulating_supply=120000000,
        total_supply=120000000,
        ath=4800.00,
        atl=0.50,
        last_updated="2026-05-15T12:00:00Z",
    )

    str_repr = str(crypto)
    assert "ETH" in str_repr
    assert "Ethereum" in str_repr
    assert "$3,428.75" in str_repr
    assert "+1.12%" in str_repr


def test_crypto_data_with_none_values():
    """Test CryptoData with None values for optional fields."""
    crypto = CryptoData(
        symbol="NEW",
        name="New Coin",
        current_price=1.50,
        market_cap=None,
        market_cap_rank=None,
        change_24h_percent=None,
        circulating_supply=None,
        total_supply=None,
        ath=None,
        atl=None,
        last_updated="2026-05-15T12:00:00Z",
    )

    assert crypto.market_cap is None
    assert crypto.market_cap_rank is None
    assert crypto.change_24h_percent is None
    assert "N/A" in str(crypto)


def test_crypto_data_repr():
    """Test repr of CryptoData."""
    crypto = CryptoData(
        symbol="BTC",
        name="Bitcoin",
        current_price=65234.50,
        market_cap=1285432000000,
        market_cap_rank=1,
        change_24h_percent=2.34,
        circulating_supply=21000000,
        total_supply=21000000,
        ath=69000.00,
        atl=100.00,
        last_updated="2026-05-15T12:00:00Z",
    )

    repr_str = repr(crypto)
    assert "CryptoData" in repr_str
    assert "BTC" in repr_str
    assert "Bitcoin" in repr_str
