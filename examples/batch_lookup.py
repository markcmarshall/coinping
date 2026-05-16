#!/usr/bin/env python
"""Batch lookup example - fetch multiple tokens and save results."""

from src.api import CoinGeckoAPI
from src.formatters import JSONFormatter, TableFormatter

# Create API instance
api = CoinGeckoAPI()

# Define tokens to fetch
tokens = ["BTC", "ETH", "SOL", "ADA", "XRP", "DOGE", "MATIC"]

print(f"Fetching data for {len(tokens)} tokens...")
print()

try:
    # Fetch all tokens
    cryptos = api.fetch_multiple(tokens)

    # Display as table
    print("=== All Tokens ===")
    formatter = TableFormatter()
    print(formatter.format_multiple(cryptos))
    print()

    # Save as JSON
    json_formatter = JSONFormatter()
    json_output = json_formatter.format_multiple(cryptos)

    with open("crypto_data.json", "w") as f:
        f.write(json_output)

    print("Data saved to crypto_data.json")

    # Print some statistics
    print("\n=== Statistics ===")
    avg_price = sum(c.current_price for c in cryptos) / len(cryptos)
    print(f"Average price: ${avg_price:,.2f}")

    gainers = [
        c for c in cryptos
        if c.change_24h_percent is not None and c.change_24h_percent > 0
    ]
    print(f"Gainers (24h): {len(gainers)}/{len(cryptos)}")

    losers = [
        c for c in cryptos
        if c.change_24h_percent is not None and c.change_24h_percent < 0
    ]
    print(f"Losers (24h): {len(losers)}/{len(cryptos)}")

except Exception as e:
    print(f"Error: {e}")
    exit(1)
