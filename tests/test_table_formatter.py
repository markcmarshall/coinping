"""Tests for table output formatting."""
from src.formatters import TableFormatter
from src.models import CryptoData


def make_crypto_data(current_price=75.0, ath=100.0):
    """Create sample crypto data for formatter tests."""
    return CryptoData(
        symbol="TST",
        name="Test Coin",
        current_price=current_price,
        market_cap=1000000000,
        market_cap_rank=42,
        change_24h_percent=1.25,
        circulating_supply=1000000,
        total_supply=2000000,
        ath=ath,
        atl=1.0,
        last_updated="2026-05-15T12:00:00Z",
    )


def test_table_output_includes_ath_and_drawdown():
    """Table output should include ATH and percentage below ATH."""
    output = TableFormatter().format_single(make_crypto_data())

    assert "ATH (USD)" in output
    assert "Down From ATH" in output
    assert "$100.00" in output
    assert "25.00%" in output


def test_ath_drawdown_is_zero_when_current_price_exceeds_ath():
    """ATH drawdown should not display a negative percentage."""
    output = TableFormatter().format_single(make_crypto_data(current_price=125.0))

    assert "0.00%" in output


def test_ath_drawdown_is_na_when_ath_is_missing():
    """Missing ATH should render as N/A."""
    output = TableFormatter().format_single(make_crypto_data(ath=None))

    assert "N/A" in output
