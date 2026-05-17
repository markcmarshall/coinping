# CoinPing

A simple, easy-to-use Python CLI tool to fetch real-time cryptocurrency data from the CoinGecko API.

## Features

- 🪙 **Multi-token support** - Fetch data for any cryptocurrency
- 📊 **Multiple output formats** - Table (pretty ASCII) or JSON output
- ⚡ **Fast & reliable** - Retry logic with exponential backoff
- 🛡️ **Error handling** - Clear error messages and graceful failure
- 🔓 **No API key required** - Uses free CoinGecko API (no registration needed)
- 📦 **Modular design** - Easy to extend with additional data sources

## Installation

### Prerequisites

- Python 3.7+
- pip (Python package manager)

### Setup

1. Clone or download this repository:
   ```bash
   cd CoinPing
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Make the script executable (optional):
   ```bash
   chmod +x coinping.py
   ```

## Quick Start

### Basic Usage

```bash
# Fetch a single token
python coinping.py BTC

# Fetch multiple tokens
python coinping.py BTC ETH SOL

# Fetch with comma-separated symbols
python coinping.py BTC,ETH,SOL

# JSON output
python coinping.py BTC --format json

# Fetch top market-cap tokens
python coinping.py --top 10

# Fetch a random token
python coinping.py --random
```

### Example Output

**Table Format (default):**
```
   ______      _       ____  _
  / ____/___  (_)___  / __ \(_)___  ____ _
 / /   / __ \/ / __ \/ /_/ / / __ \/ __ `/
/ /___/ /_/ / / / / / ____/ / / / / /_/ /
\____/\____/_/_/ /_/_/   /_/_/ /_/\__, /
                                  /____/
CoinPing - pinging coin data directly into your terminal.

Symbol    Name       Price (USD)    24h Change    ATH (USD)    Down From ATH    Market Cap (USD)    Rank
------    --------   -----------    ----------    ---------    -------------    ----------------    -----
BTC       Bitcoin    $65,234.50     +2.34%        $69,000.00   5.46%            $1,285.43B          1
ETH       Ethereum   $3,428.75      +1.12%        $4,800.00    28.57%           $411.23B            2
SOL       Solana     $142.50        +5.67%        $260.00      45.19%           $61.23B             5
```

**JSON Format:**
JSON output omits the banner so it remains machine-readable.

```json
{
  "BTC": {
    "name": "Bitcoin",
    "current_price": 65234.50,
    "market_cap": 1285432000000,
    "market_cap_rank": 1,
    "change_24h_percent": 2.34,
    "circulating_supply": 21000000,
    "total_supply": 21000000,
    "ath": 69000.00,
    "atl": 100.00,
    "last_updated": "2026-05-15T12:00:00Z"
  }
}
```

## Command Reference

```bash
python coinping.py [OPTIONS] [SYMBOLS]...
```

### Arguments

- `SYMBOLS` - Token symbols to fetch (e.g., BTC, ETH, SOL)
  - Can provide multiple symbols separated by spaces or commas
  - Case-insensitive (btc, BTC, Btc all work)

### Options

```
--format, -f [table|json]    Output format (default: table)
--top INTEGER                 Fetch top N tokens by market cap (max 500)
--random                      Fetch a random supported token
-h, --help                    Show help message
--version                     Show version
```

### Examples

```bash
# Single token
python coinping.py BTC

# Multiple tokens (space-separated)
python coinping.py BTC ETH DOGE

# Multiple tokens (comma-separated)
python coinping.py BTC,ETH,DOGE

# JSON output
python coinping.py BTC --format json

# Top 10 tokens by market cap
python coinping.py --top 10

# Random token
python coinping.py --random

# Show help
python coinping.py --help
```

## API Information

### Data Provided

Table output shows:

- **Symbol** - Token symbol (BTC, ETH, etc.)
- **Name** - Full name (Bitcoin, Ethereum, etc.)
- **Price (USD)** - Current price in USD
- **24h Change** - 24-hour price change percentage
- **ATH (USD)** - All-time high price
- **Down From ATH** - Percentage below all-time high
- **Market Cap (USD)** - Total market capitalization
- **Rank** - Market-cap rank

JSON output uses each token symbol as the top-level key and includes:

- **name** - Full name (Bitcoin, Ethereum, etc.)
- **current_price** - Current price in USD
- **market_cap** - Total market capitalization
- **market_cap_rank** - Position by market cap
- **change_24h_percent** - 24-hour price change percentage
- **circulating_supply** - Number of coins in circulation
- **total_supply** - Total coin supply reported by CoinGecko
- **ath** - All-time high price
- **atl** - All-time low price
- **last_updated** - Last update timestamp

### Bulk and Random Fetches

Use `--top N` to retrieve the top tokens by market cap. Requests are capped at 500 tokens, and requests above 100 print a quota warning.

Use `--random` to retrieve one arbitrary CoinGecko-supported coin.

### API Source

- **Provider**: CoinGecko
- **API Base**: `https://api.coingecko.com/api/v3`
- **Lookup**: Uses `/search` for ranked exact-symbol matching, then `/coins/{id}` for market data
- **Top Tokens**: Uses `/coins/markets` ordered by market cap
- **Random Token**: Uses `/coins/list` to choose an arbitrary coin ID, then `/coins/{id}` for market data
- **Rate Limit**: Free public API limits apply
- **Authentication**: Not required
- **Documentation**: [CoinGecko API Docs](https://www.coingecko.com/api/documentation)

### Why CoinGecko?

We chose CoinGecko as the default data source because:

| Feature | CoinGecko | CoinMarketCap | Binance |
|---------|-----------|---------------|---------|
| API Key Required | ❌ No | ✅ Yes | ❌ No |
| Free Rate Limit | 10-50/min | 333/month | Generous |
| Tokens Supported | 14,000+ | 10,000+ | Spot pairs only |
| Setup Complexity | ⚡ Zero | 📝 Registration | ⚡ Zero |
| Data Quality | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

**Note**: The code is modular and extensible. If you have a CoinMarketCap API key and want to use that instead, you can easily add support by creating a new API handler class.

## Library Usage

You can also use the crypto fetcher as a Python library:

```python
from src.api import CoinGeckoAPI
from src.formatters import TableFormatter

# Create API instance
api = CoinGeckoAPI()

# Fetch a single token
btc = api.fetch_token("BTC")
print(f"Bitcoin price: ${btc.current_price:,.2f}")
print(f"24h change: {btc.change_24h_percent:+.2f}%")

# Fetch multiple tokens
cryptos = api.fetch_multiple(["BTC", "ETH", "SOL"])

# Format output
formatter = TableFormatter()
print(formatter.format_multiple(cryptos))
```

See `examples/` directory for more usage examples.

## Running Tests

```bash
# Run all tests
pytest tests/

# If you are setting up a fresh development environment
pip install -r requirements-dev.txt

# Run with verbose output
pytest tests/ -v

# Run specific test file
pytest tests/test_crypto_data.py

# Run with coverage report
pytest tests/ --cov=src
```

## Troubleshooting

### "Token not found" Error

**Problem:** You get `Error: Token 'XYZ' not found`

**Solution:** The token symbol doesn't exist on CoinGecko. Try:
- Check spelling (case-insensitive, so BTc, BTC, btc all work)
- Some tokens may use different symbols than expected (e.g., DOGE, not DOG)

### Network Timeout

**Problem:** `Failed to connect after 3 attempts`

**Solution:**
- Check your internet connection
- Try again (the API may be temporarily unavailable)
- The script retries automatically up to 3 times

### "Connection refused" Error

**Problem:** Cannot reach CoinGecko API

**Solution:**
- Check your internet connection
- CoinGecko may be temporarily unavailable (rare)
- Try a different token to verify connection
- Check firewall/proxy settings if behind corporate network

### "Invalid API response format"

**Problem:** Unexpected error from API

**Solution:**
- This is rare and usually means the API changed its response format
- Try again later
- If persists, report an issue with the token symbol you used

## Project Structure

```
CoinPing/
├── README.md                      # This file
├── requirements.txt               # Python dependencies
├── coinping.py             # Main CLI entry point
├── src/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── base.py               # Abstract API handler
│   │   └── coingecko.py          # CoinGecko implementation
│   ├── models/
│   │   ├── __init__.py
│   │   └── crypto_data.py        # Data structure
│   ├── formatters/
│   │   ├── __init__.py
│   │   ├── base.py               # Abstract formatter
│   │   ├── table.py              # ASCII table output
│   │   └── json.py               # JSON output
│   ├── exceptions.py             # Custom exceptions
│   └── config.py                 # Configuration constants
├── tests/
│   ├── __init__.py
│   ├── test_crypto_data.py       # Data model tests
│   └── test_api_coingecko.py     # API tests
└── examples/
    ├── simple_usage.py           # Basic usage example
    └── batch_lookup.py           # Multiple tokens example
```

## Configuration

### Environment Variables

Environment variables are not currently required. If additional API providers are added later, provider-specific settings can be introduced then:

```env
# CoinMarketCap API (if using that instead)
COINMARKETCAP_API_KEY=your_api_key_here
```

## Development

### Adding a New API Source

1. Create a new file: `src/api/yourapi.py`
2. Inherit from `CryptoAPIHandler`
3. Implement required methods:
   - `fetch_token(symbol)`
   - `fetch_multiple(symbols)`
   - `validate_token(symbol)`
   - `get_supported_tokens()`
4. Update `src/api/__init__.py` to export your handler

### Adding a New Output Format

1. Create a new file: `src/formatters/yourformat.py`
2. Inherit from `Formatter`
3. Implement:
   - `format_single(crypto_data)`
   - `format_multiple(crypto_data_list)`
4. Update `src/formatters/__init__.py`
5. Update `coinping.py` to include your format in the `--format` option

## Performance Notes

- **Symbol lookup**: ~1-2 seconds per token
- **Top-token lookup**: Uses bulk market data requests, up to 250 tokens per API call
- **Random lookup**: Uses one coin-list request plus one coin-detail request
- **Batch symbol operations**: Fetches symbols sequentially to keep behavior simple

## Rate Limits

- CoinGecko free API: 10-50 calls/minute
- Symbol lookup: 1 search call + 1 detail call per token
- Top-token lookup: 1 market-data call per 250 tokens requested
- Random lookup: 1 coin-list call + 1 detail call
- Large `--top` requests can consume API quota quickly; CoinPing caps this mode at 500 tokens

## Common Issues & Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| Command not found | Python not in PATH | Add Python to PATH or use full path |
| Module not found | Dependencies not installed | Run `pip install -r requirements.txt` |
| SSL Certificate error | Network/firewall issue | Check connection or update certificates |
| Token not found | Invalid symbol | Check spelling or try a more common ticker |

## Future Enhancements

Possible improvements for future versions:

- Support for multiple API sources (CoinMarketCap, Binance)
- Caching layer for rate limit avoidance
- Historical price tracking
- Async/concurrent batch operations
- Portfolio value calculations
- Price alert system
- CSV export format
- Web dashboard (Flask/FastAPI)

## Contributing

Found a bug or have a feature request? Feel free to:
1. Check existing issues
2. Create a detailed bug report or feature request
3. Include steps to reproduce for bugs

## License

This project is provided as-is for educational and personal use.

## Support

For issues or questions:
1. Check the [Troubleshooting](#troubleshooting) section above
2. Review the [examples/](examples/) directory for usage patterns
3. Check the CoinGecko API documentation for data field explanations

## Version History

### v1.0.0 (2026-05-15)
- Initial release
- CoinGecko API integration
- Table and JSON output formats
- CLI with Click framework
- Comprehensive error handling
- Unit tests
- Documentation

---

**Happy crypto tracking!** 🚀

For more information on CoinGecko API, visit: https://www.coingecko.com/api/documentation
