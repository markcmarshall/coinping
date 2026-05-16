"""Tests for the CoinPing command line interface."""
import json

from click.testing import CliRunner

from coinping import TAGLINE, main
from src.models import CryptoData


class FakeCoinGeckoAPI:
    """Small fake for CLI tests."""

    def fetch_multiple(self, symbols):
        return [
            CryptoData(
                symbol=symbol.upper(),
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
            for symbol in symbols
        ]

    def get_supported_tokens(self):
        return ["BTC", "ETH"]


def test_table_output_includes_logo_and_tagline(monkeypatch):
    """Table output should include the branded banner."""
    monkeypatch.setattr("coinping.CoinGeckoAPI", FakeCoinGeckoAPI)

    result = CliRunner().invoke(main, ["BTC"])

    assert result.exit_code == 0
    assert "____" in result.output
    assert TAGLINE in result.output
    assert "BTC" in result.output


def test_json_output_is_machine_readable_without_banner(monkeypatch):
    """JSON output should not include decorative text."""
    monkeypatch.setattr("coinping.CoinGeckoAPI", FakeCoinGeckoAPI)

    result = CliRunner().invoke(main, ["BTC", "--format", "json"])

    assert result.exit_code == 0
    assert TAGLINE not in result.output
    assert json.loads(result.output)["BTC"]["name"] == "Bitcoin"


def test_list_output_includes_logo_and_tagline(monkeypatch):
    """The supported-token list should include the branded banner."""
    monkeypatch.setattr("coinping.CoinGeckoAPI", FakeCoinGeckoAPI)

    result = CliRunner().invoke(main, ["--list"])

    assert result.exit_code == 0
    assert TAGLINE in result.output
    assert "BTC, ETH" in result.output
