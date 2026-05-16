#!/usr/bin/env python
"""Simple usage example for cryptocurrency fetcher."""

from src.api import CoinGeckoAPI
from src.formatters import TableFormatter

# Create API instance
api = CoinGeckoAPI()

# Fetch a single token
print("=== Fetching Bitcoin ===")
btc = api.fetch_token("BTC")
print(f"Symbol: {btc.symbol}")
print(f"Name: {btc.name}")
print(f"Price: ${btc.current_price:,.2f}")
print(f"Market Cap: ${btc.market_cap:,.0f}")
print(f"24h Change: {btc.change_24h_percent:+.2f}%")
print()

# Fetch multiple tokens
print("=== Fetching Multiple Tokens ===")
cryptos = api.fetch_multiple(["BTC", "ETH", "SOL"])

# Format as table
formatter = TableFormatter()
print(formatter.format_multiple(cryptos))
