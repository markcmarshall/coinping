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

    def fetch_top_tokens(self, limit):
        return [
            CryptoData(
                symbol=f"TOP{index}",
                name=f"Top Coin {index}",
                current_price=float(index),
                market_cap=1000000 * index,
                market_cap_rank=index,
                change_24h_percent=1.0,
                circulating_supply=1000000,
                total_supply=2000000,
                ath=10.0,
                atl=0.1,
                last_updated="2026-05-15T12:00:00Z",
            )
            for index in range(1, limit + 1)
        ]

    def fetch_random_token(self):
        return CryptoData(
            symbol="RND",
            name="Random Coin",
            current_price=1.23,
            market_cap=123000000,
            market_cap_rank=321,
            change_24h_percent=None,
            circulating_supply=1000000,
            total_supply=2000000,
            ath=5.0,
            atl=0.01,
            last_updated="2026-05-15T12:00:00Z",
        )


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


def test_top_output_includes_requested_count(monkeypatch):
    """Top-token output should fetch the requested number of coins."""
    monkeypatch.setattr("coinping.CoinGeckoAPI", FakeCoinGeckoAPI)

    result = CliRunner().invoke(main, ["--top", "3"])

    assert result.exit_code == 0
    assert TAGLINE in result.output
    assert "TOP1" in result.output
    assert "TOP3" in result.output


def test_top_output_warns_for_large_requests(monkeypatch):
    """Large top-token requests should warn about API quota."""
    monkeypatch.setattr("coinping.CoinGeckoAPI", FakeCoinGeckoAPI)

    result = CliRunner().invoke(main, ["--top", "101"])

    assert result.exit_code == 0
    assert "consume CoinGecko API quota quickly" in result.output


def test_random_output_fetches_random_token(monkeypatch):
    """Random mode should fetch a single arbitrary token."""
    monkeypatch.setattr("coinping.CoinGeckoAPI", FakeCoinGeckoAPI)

    result = CliRunner().invoke(main, ["--random"])

    assert result.exit_code == 0
    assert TAGLINE in result.output
    assert "RND" in result.output
    assert "Random Coin" in result.output


def test_modes_are_mutually_exclusive(monkeypatch):
    """Users should choose exactly one fetch mode."""
    monkeypatch.setattr("coinping.CoinGeckoAPI", FakeCoinGeckoAPI)

    result = CliRunner().invoke(main, ["BTC", "--random"])

    assert result.exit_code == 1
    assert "not more than one mode" in result.output
