"""Configuration and constants for the cryptocurrency fetcher."""

DEFAULT_API = "coingecko"
API_TIMEOUT = 5  # seconds
RETRY_ATTEMPTS = 3
RETRY_BACKOFF = 1.5  # exponential backoff factor

COINGECKO_API_BASE = "https://api.coingecko.com/api/v3"

# Price formatting
CURRENCY = "usd"
PRICE_FORMAT = ".2f"
