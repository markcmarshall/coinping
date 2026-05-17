"""Tests for CoinGecko API handler."""
import pytest
import responses

from src.api import CoinGeckoAPI
from src.exceptions import TokenNotFoundError


@pytest.fixture
def api():
    """Create a CoinGeckoAPI instance for testing."""
    return CoinGeckoAPI()


def add_search_response(query, coins):
    """Mock CoinGecko search response for a query."""
    responses.add(
        responses.GET,
        "https://api.coingecko.com/api/v3/search",
        match=[responses.matchers.query_param_matcher({"query": query})],
        json={"coins": coins},
        status=200,
    )


def coin_search_result(coin_id, symbol, name, market_cap_rank=None):
    """Build the subset of search result fields used by the API handler."""
    return {
        "id": coin_id,
        "symbol": symbol,
        "name": name,
        "market_cap_rank": market_cap_rank,
    }


def coin_market_result(symbol, name, market_cap_rank):
    """Build the subset of market fields used by the API handler."""
    return {
        "symbol": symbol,
        "name": name,
        "current_price": 100.0,
        "market_cap": 1000000,
        "market_cap_rank": market_cap_rank,
        "price_change_percentage_24h": 1.5,
        "circulating_supply": 1000000,
        "total_supply": 2000000,
        "ath": 200.0,
        "atl": 1.0,
        "last_updated": "2026-05-15T12:00:00Z",
    }


@responses.activate
def test_fetch_token_success(api):
    """Test successful token fetch."""
    add_search_response(
        "BTC",
        [
            coin_search_result("bitcoin", "BTC", "Bitcoin", 1),
        ],
    )

    # Mock the bitcoin data endpoint
    responses.add(
        responses.GET,
        "https://api.coingecko.com/api/v3/coins/bitcoin",
        json={
            "id": "bitcoin",
            "name": "Bitcoin",
            "symbol": "BTC",
            "market_cap_rank": 1,
            "last_updated": "2026-05-15T12:00:00Z",
            "market_data": {
                "current_price": {"usd": 65234.50},
                "market_cap": {"usd": 1285432000000},
                "price_change_percentage_24h": 2.34,
                "circulating_supply": 21000000,
                "total_supply": 21000000,
                "ath": {"usd": 69000.00},
                "atl": {"usd": 100.00},
            },
        },
        status=200,
    )

    crypto = api.fetch_token("BTC")

    assert crypto.symbol == "BTC"
    assert crypto.name == "Bitcoin"
    assert crypto.current_price == 65234.50
    assert crypto.market_cap == 1285432000000
    assert crypto.market_cap_rank == 1
    assert crypto.change_24h_percent == 2.34


@responses.activate
def test_fetch_token_not_found(api):
    """Test token not found error."""
    add_search_response("INVALID_TOKEN", [])

    with pytest.raises(TokenNotFoundError):
        api.fetch_token("INVALID_TOKEN")


@responses.activate
def test_fetch_token_case_insensitive(api):
    """Test that token fetching is case-insensitive."""
    add_search_response(
        "BTC",
        [
            coin_search_result("bitcoin", "BTC", "Bitcoin", 1),
        ],
    )

    responses.add(
        responses.GET,
        "https://api.coingecko.com/api/v3/coins/bitcoin",
        json={
            "id": "bitcoin",
            "name": "Bitcoin",
            "symbol": "BTC",
            "market_cap_rank": 1,
            "last_updated": "2026-05-15T12:00:00Z",
            "market_data": {
                "current_price": {"usd": 65234.50},
                "market_cap": {"usd": 1285432000000},
                "price_change_percentage_24h": 2.34,
                "circulating_supply": 21000000,
                "total_supply": 21000000,
                "ath": {"usd": 69000.00},
                "atl": {"usd": 100.00},
            },
        },
        status=200,
    )

    # Test lowercase
    crypto = api.fetch_token("btc")
    assert crypto.symbol == "BTC"

    # Reset API for next test
    api._supported_tokens = None
    responses.reset()

    add_search_response(
        "BTC",
        [
            coin_search_result("bitcoin", "BTC", "Bitcoin", 1),
        ],
    )

    responses.add(
        responses.GET,
        "https://api.coingecko.com/api/v3/coins/bitcoin",
        json={
            "id": "bitcoin",
            "name": "Bitcoin",
            "symbol": "BTC",
            "market_cap_rank": 1,
            "last_updated": "2026-05-15T12:00:00Z",
            "market_data": {
                "current_price": {"usd": 65234.50},
                "market_cap": {"usd": 1285432000000},
                "price_change_percentage_24h": 2.34,
                "circulating_supply": 21000000,
                "total_supply": 21000000,
                "ath": {"usd": 69000.00},
                "atl": {"usd": 100.00},
            },
        },
        status=200,
    )

    # Test mixed case
    crypto = api.fetch_token("BtC")
    assert crypto.symbol == "BTC"


@responses.activate
def test_validate_token(api):
    """Test token validation."""
    responses.add(
        responses.GET,
        "https://api.coingecko.com/api/v3/coins/list",
        json=[
            {"id": "bitcoin", "symbol": "btc", "name": "Bitcoin"},
            {"id": "ethereum", "symbol": "eth", "name": "Ethereum"},
        ],
        status=200,
    )

    assert api.validate_token("BTC") is True
    assert api.validate_token("btc") is True
    assert api.validate_token("ETH") is True
    assert api.validate_token("INVALID") is False


@responses.activate
def test_get_supported_tokens(api):
    """Test getting list of supported tokens."""
    responses.add(
        responses.GET,
        "https://api.coingecko.com/api/v3/coins/list",
        json=[
            {"id": "bitcoin", "symbol": "btc", "name": "Bitcoin"},
            {"id": "ethereum", "symbol": "eth", "name": "Ethereum"},
            {"id": "solana", "symbol": "sol", "name": "Solana"},
        ],
        status=200,
    )

    tokens = api.get_supported_tokens()

    assert "BTC" in tokens
    assert "ETH" in tokens
    assert "SOL" in tokens
    assert len(tokens) == 3


@responses.activate
def test_fetch_multiple_tokens(api):
    """Test fetching multiple tokens."""
    add_search_response(
        "BTC",
        [
            coin_search_result("bitcoin", "BTC", "Bitcoin", 1),
        ],
    )
    add_search_response(
        "ETH",
        [
            coin_search_result("ethereum", "ETH", "Ethereum", 2),
        ],
    )

    # Mock Bitcoin response
    responses.add(
        responses.GET,
        "https://api.coingecko.com/api/v3/coins/bitcoin",
        json={
            "id": "bitcoin",
            "name": "Bitcoin",
            "symbol": "BTC",
            "market_cap_rank": 1,
            "last_updated": "2026-05-15T12:00:00Z",
            "market_data": {
                "current_price": {"usd": 65234.50},
                "market_cap": {"usd": 1285432000000},
                "price_change_percentage_24h": 2.34,
                "circulating_supply": 21000000,
                "total_supply": 21000000,
                "ath": {"usd": 69000.00},
                "atl": {"usd": 100.00},
            },
        },
        status=200,
    )

    # Mock Ethereum response
    responses.add(
        responses.GET,
        "https://api.coingecko.com/api/v3/coins/ethereum",
        json={
            "id": "ethereum",
            "name": "Ethereum",
            "symbol": "ETH",
            "market_cap_rank": 2,
            "last_updated": "2026-05-15T12:00:00Z",
            "market_data": {
                "current_price": {"usd": 3428.75},
                "market_cap": {"usd": 411234000000},
                "price_change_percentage_24h": 1.12,
                "circulating_supply": 120000000,
                "total_supply": 120000000,
                "ath": {"usd": 4800.00},
                "atl": {"usd": 0.50},
            },
        },
        status=200,
    )

    cryptos = api.fetch_multiple(["BTC", "ETH"])

    assert len(cryptos) == 2
    assert cryptos[0].symbol == "BTC"
    assert cryptos[1].symbol == "ETH"


@responses.activate
def test_fetch_token_prefers_exact_symbol_by_market_cap_rank(api):
    """Test that ambiguous search results pick the highest-ranked exact symbol."""
    add_search_response(
        "BTC",
        [
            coin_search_result("bitcoin-cash", "BCH", "Bitcoin Cash", 20),
            coin_search_result("bitcoin-2", "BTC", "Bitcoin Clone", 500),
            coin_search_result("bitcoin", "BTC", "Bitcoin", 1),
        ],
    )

    responses.add(
        responses.GET,
        "https://api.coingecko.com/api/v3/coins/bitcoin",
        json={
            "id": "bitcoin",
            "name": "Bitcoin",
            "symbol": "BTC",
            "market_cap_rank": 1,
            "last_updated": "2026-05-15T12:00:00Z",
            "market_data": {
                "current_price": {"usd": 65234.50},
                "market_cap": {"usd": 1285432000000},
                "price_change_percentage_24h": 2.34,
                "circulating_supply": 21000000,
                "total_supply": 21000000,
                "ath": {"usd": 69000.00},
                "atl": {"usd": 100.00},
            },
        },
        status=200,
    )

    crypto = api.fetch_token("BTC")

    assert crypto.name == "Bitcoin"


@responses.activate
def test_fetch_top_tokens(api):
    """Test fetching top tokens by market cap."""
    responses.add(
        responses.GET,
        "https://api.coingecko.com/api/v3/coins/markets",
        json=[
            coin_market_result("btc", "Bitcoin", 1),
            coin_market_result("eth", "Ethereum", 2),
            coin_market_result("sol", "Solana", 3),
        ],
        status=200,
    )

    cryptos = api.fetch_top_tokens(3)

    assert [crypto.symbol for crypto in cryptos] == ["BTC", "ETH", "SOL"]
    assert [crypto.market_cap_rank for crypto in cryptos] == [1, 2, 3]


def test_fetch_top_tokens_rejects_invalid_limit(api):
    """Test top-token limit validation."""
    with pytest.raises(ValueError):
        api.fetch_top_tokens(501)


@responses.activate
def test_fetch_random_token(api, monkeypatch):
    """Test fetching a random supported token."""
    monkeypatch.setattr(
        "src.api.coingecko.random.choice",
        lambda coins: coins[1],
    )
    responses.add(
        responses.GET,
        "https://api.coingecko.com/api/v3/coins/list",
        json=[
            {"id": "bitcoin", "symbol": "btc", "name": "Bitcoin"},
            {"id": "ethereum", "symbol": "eth", "name": "Ethereum"},
        ],
        status=200,
    )
    responses.add(
        responses.GET,
        "https://api.coingecko.com/api/v3/coins/ethereum",
        json={
            "id": "ethereum",
            "name": "Ethereum",
            "symbol": "ETH",
            "market_cap_rank": 2,
            "last_updated": "2026-05-15T12:00:00Z",
            "market_data": {
                "current_price": {"usd": 3428.75},
                "market_cap": {"usd": 411234000000},
                "price_change_percentage_24h": 1.12,
                "circulating_supply": 120000000,
                "total_supply": 120000000,
                "ath": {"usd": 4800.00},
                "atl": {"usd": 0.50},
            },
        },
        status=200,
    )

    crypto = api.fetch_random_token()

    assert crypto.symbol == "ETH"
    assert crypto.name == "Ethereum"
