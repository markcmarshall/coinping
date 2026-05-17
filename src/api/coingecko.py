"""CoinGecko API implementation for cryptocurrency data."""
import random
import time
from typing import List, Optional, Dict, Any

import requests

from src.api.base import CryptoAPIHandler
from src.config import COINGECKO_API_BASE, API_TIMEOUT, RETRY_ATTEMPTS, RETRY_BACKOFF
from src.exceptions import APIError, NetworkError, TokenNotFoundError
from src.models import CryptoData


MAX_TOP_TOKENS = 500
COINS_MARKETS_PAGE_SIZE = 250


class CoinGeckoAPI(CryptoAPIHandler):
    """CoinGecko API handler for fetching cryptocurrency data."""

    def __init__(self):
        """Initialize CoinGecko API handler."""
        self.base_url = COINGECKO_API_BASE
        self.timeout = API_TIMEOUT
        self.retry_attempts = RETRY_ATTEMPTS
        self.retry_backoff = RETRY_BACKOFF
        self._supported_tokens: Optional[Dict[str, str]] = None

    def _search_coin(self, query: str) -> List[Dict[str, Any]]:
        """Search for a coin by symbol or name using CoinGecko's search endpoint.

        Args:
            query: Search query (symbol or name, case-insensitive)

        Returns:
            List of matching coins, ranked by relevance/popularity

        Raises:
            NetworkError: If request fails
        """
        params = {"query": query}

        try:
            data = self._get_request("/search", params=params)
            coins = data.get("coins", [])
            return coins
        except NetworkError:
            raise
        except Exception as e:
            raise NetworkError(f"Search failed: {str(e)}") from e

    @staticmethod
    def _select_best_search_result(symbol: str, coins: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Select the best exact-symbol match from CoinGecko search results."""
        symbol_upper = symbol.upper()
        exact_matches = [
            coin for coin in coins
            if coin.get("symbol", "").upper() == symbol_upper
        ]

        if not exact_matches:
            return None

        return min(
            exact_matches,
            key=lambda coin: (
                coin.get("market_cap_rank") is None,
                coin.get("market_cap_rank") or float("inf"),
            ),
        )

    def _get_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict:
        """Make a GET request to the CoinGecko API with retry logic.

        Args:
            endpoint: API endpoint (without base URL)
            params: Query parameters

        Returns:
            JSON response as dictionary

        Raises:
            NetworkError: If request fails after retries
            APIError: If API returns an error status
        """
        url = f"{self.base_url}{endpoint}"
        last_exception = None

        for attempt in range(self.retry_attempts):
            try:
                response = requests.get(url, params=params, timeout=self.timeout)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.Timeout as e:
                last_exception = e
                if attempt < self.retry_attempts - 1:
                    wait_time = self.retry_backoff ** attempt
                    time.sleep(wait_time)
            except requests.exceptions.ConnectionError as e:
                last_exception = e
                if attempt < self.retry_attempts - 1:
                    wait_time = self.retry_backoff ** attempt
                    time.sleep(wait_time)
            except requests.exceptions.HTTPError as e:
                if response.status_code >= 500:
                    last_exception = e
                    if attempt < self.retry_attempts - 1:
                        wait_time = self.retry_backoff ** attempt
                        time.sleep(wait_time)
                else:
                    raise APIError(f"API Error: {response.status_code} - {response.text}") from e
            except requests.exceptions.RequestException as e:
                raise NetworkError(f"Network error: {str(e)}") from e

        raise NetworkError(f"Failed to connect after {self.retry_attempts} attempts: {str(last_exception)}")

    def _load_supported_tokens(self) -> None:
        """Load list of all supported tokens from CoinGecko."""
        if self._supported_tokens is not None:
            return

        try:
            data = self._get_request("/coins/list")
            self._supported_tokens = {coin["symbol"].upper(): coin["id"] for coin in data}
        except Exception as e:
            raise APIError(f"Failed to load supported tokens: {str(e)}") from e

    def _load_supported_coins(self) -> List[Dict[str, Any]]:
        """Load list of all supported coins from CoinGecko."""
        try:
            return self._get_request("/coins/list")
        except Exception as e:
            raise APIError(f"Failed to load supported coins: {str(e)}") from e

    def validate_token(self, symbol: str) -> bool:
        """Check if a token symbol exists.

        Args:
            symbol: Token symbol to validate (case-insensitive)

        Returns:
            True if token exists, False otherwise
        """
        self._load_supported_tokens()
        return symbol.upper() in self._supported_tokens

    def get_supported_tokens(self) -> List[str]:
        """Get list of all supported token symbols.

        Returns:
            List of available token symbols
        """
        self._load_supported_tokens()
        return sorted(list(self._supported_tokens.keys()))

    def fetch_token(self, symbol: str) -> CryptoData:
        """Fetch data for a single cryptocurrency token.

        Args:
            symbol: Token symbol (e.g., 'BTC', 'ETH', case-insensitive)

        Returns:
            CryptoData object with token information

        Raises:
            TokenNotFoundError: If token is not found
            APIError: If API returns an error
            NetworkError: If network request fails
        """
        symbol_upper = symbol.upper()

        # Search returns ranked results; filter to exact symbols first so names
        # like "Bitcoin Cash" do not satisfy a BTC lookup.
        search_results = self._search_coin(symbol_upper)
        selected_coin = self._select_best_search_result(symbol_upper, search_results)

        if selected_coin is None:
            raise TokenNotFoundError(
                f"Token '{symbol}' not found. "
                f"Please check the spelling and try again."
            )

        coin_id = selected_coin.get("id")
        if not coin_id:
            raise APIError(f"Invalid search result for token '{symbol}'")

        return self._fetch_by_id(coin_id, symbol_upper)

    def fetch_multiple(self, symbols: List[str]) -> List[CryptoData]:
        """Fetch data for multiple cryptocurrency tokens.

        Args:
            symbols: List of token symbols (case-insensitive)

        Returns:
            List of CryptoData objects

        Raises:
            TokenNotFoundError: If any token is not found
            APIError: If API returns an error
            NetworkError: If network request fails
        """
        results = []
        for symbol in symbols:
            results.append(self.fetch_token(symbol))
        return results

    def fetch_top_tokens(self, limit: int) -> List[CryptoData]:
        """Fetch top cryptocurrencies by market cap.

        Args:
            limit: Number of ranked tokens to retrieve, up to MAX_TOP_TOKENS

        Returns:
            List of CryptoData objects ordered by market cap descending

        Raises:
            ValueError: If limit is outside the supported range
            APIError: If API returns an error
            NetworkError: If network request fails
        """
        if limit < 1 or limit > MAX_TOP_TOKENS:
            raise ValueError(f"Top token limit must be between 1 and {MAX_TOP_TOKENS}")

        results = []
        page = 1

        while len(results) < limit:
            per_page = min(COINS_MARKETS_PAGE_SIZE, limit - len(results))
            data = self._get_request(
                "/coins/markets",
                params={
                    "vs_currency": "usd",
                    "order": "market_cap_desc",
                    "per_page": per_page,
                    "page": page,
                    "sparkline": False,
                },
            )

            if not data:
                break

            results.extend(self._crypto_data_from_market_data(coin) for coin in data)
            page += 1

        return results[:limit]

    def fetch_random_token(self) -> CryptoData:
        """Fetch data for a random supported cryptocurrency."""
        coins = self._load_supported_coins()
        if not coins:
            raise TokenNotFoundError("No supported tokens found.")

        coin = random.choice(coins)
        coin_id = coin.get("id")
        if not coin_id:
            raise APIError("Invalid coin list response: missing coin id")

        symbol = coin.get("symbol", coin_id).upper()
        return self._fetch_by_id(coin_id, symbol)

    def _fetch_by_id(self, coin_id: str, symbol: str) -> CryptoData:
        """Fetch cryptocurrency data by CoinGecko coin ID.

        Args:
            coin_id: CoinGecko coin ID
            symbol: Original symbol for reference

        Returns:
            CryptoData object

        Raises:
            APIError: If API returns an error
            NetworkError: If network request fails
        """
        params = {
            "localization": False,
            "market_data": True,
            "community_data": False,
            "developer_data": False,
            "sparkline": False,
        }

        data = self._get_request(f"/coins/{coin_id}", params=params)

        try:
            market_data = data.get("market_data", {})
            return self._crypto_data_from_coin_detail(data, market_data, symbol)
        except (KeyError, TypeError) as e:
            raise APIError(f"Invalid API response format: {str(e)}") from e

    @staticmethod
    def _crypto_data_from_coin_detail(
        data: Dict[str, Any],
        market_data: Dict[str, Any],
        symbol: str,
    ) -> CryptoData:
        """Build CryptoData from the /coins/{id} endpoint."""
        return CryptoData(
            symbol=symbol,
            name=data.get("name", "Unknown"),
            current_price=market_data.get("current_price", {}).get("usd", 0.0),
            market_cap=market_data.get("market_cap", {}).get("usd"),
            market_cap_rank=data.get("market_cap_rank"),
            change_24h_percent=market_data.get("price_change_percentage_24h"),
            circulating_supply=market_data.get("circulating_supply"),
            total_supply=market_data.get("total_supply"),
            ath=market_data.get("ath", {}).get("usd"),
            atl=market_data.get("atl", {}).get("usd"),
            last_updated=data.get("last_updated", "Unknown"),
        )

    @staticmethod
    def _crypto_data_from_market_data(data: Dict[str, Any]) -> CryptoData:
        """Build CryptoData from the /coins/markets endpoint."""
        return CryptoData(
            symbol=data.get("symbol", "UNKNOWN").upper(),
            name=data.get("name", "Unknown"),
            current_price=data.get("current_price") or 0.0,
            market_cap=data.get("market_cap"),
            market_cap_rank=data.get("market_cap_rank"),
            change_24h_percent=data.get("price_change_percentage_24h"),
            circulating_supply=data.get("circulating_supply"),
            total_supply=data.get("total_supply"),
            ath=data.get("ath"),
            atl=data.get("atl"),
            last_updated=data.get("last_updated", "Unknown"),
        )
