#!/usr/bin/env python
"""
CoinPing - Fetch cryptocurrency data from CoinGecko API.

Simple CLI tool to get real-time cryptocurrency prices, market cap, and other metrics.
"""
import sys

import click

from src.api import CoinGeckoAPI
from src.exceptions import CryptoFetcherError, TokenNotFoundError
from src.formatters import TableFormatter, JSONFormatter


ASCII_LOGO = r"""
   ______      _       ____  _
  / ____/___  (_)___  / __ \(_)___  ____ _
 / /   / __ \/ / __ \/ /_/ / / __ \/ __ `/
/ /___/ /_/ / / / / / ____/ / / / / /_/ /
\____/\____/_/_/ /_/_/   /_/_/ /_/\__, /
                                  /____/
"""
TAGLINE = "CoinPing - pinging coin data into your terminal."


def print_banner() -> None:
    """Print the CoinPing CLI banner."""
    click.echo(ASCII_LOGO.rstrip())
    click.echo(TAGLINE)
    click.echo()


@click.command()
@click.argument("symbols", nargs=-1, required=False)
@click.option(
    "--format",
    "-f",
    "output_format",
    type=click.Choice(["table", "json"]),
    default="table",
    help="Output format: table (default) or json",
)
@click.option(
    "--list",
    "show_list",
    is_flag=True,
    help="Show list of all supported tokens (first 100)",
)
@click.version_option(version="1.0.0", prog_name="coinping")
@click.help_option("-h", "--help")
def main(symbols, output_format, show_list):
    """
    CoinPing - Fetch cryptocurrency data from CoinGecko API.

    \b
    Examples:
      # Single token
      python coinping.py BTC

      # Multiple tokens
      python coinping.py BTC ETH SOL

      # JSON output
      python coinping.py BTC --format json

      # Comma-separated symbols
      python coinping.py BTC,ETH,SOL

    \b
    Supported formats:
      table  - Pretty ASCII table (default)
      json   - Machine-readable JSON output
    """

    try:
        api = CoinGeckoAPI()

        # Handle --list flag
        if show_list:
            tokens = api.get_supported_tokens()
            print_banner()
            click.echo(f"Total supported tokens: {len(tokens)}")
            click.echo(f"\nFirst 100 tokens:")
            click.echo(", ".join(tokens[:100]))
            return

        # Validate input
        if not symbols:
            click.echo("Error: Please provide at least one token symbol")
            click.echo("Examples: python coinping.py BTC")
            click.echo("          python coinping.py BTC ETH SOL")
            click.echo("\nUse --help for more information")
            sys.exit(1)

        # Handle comma-separated symbols
        symbol_list = []
        for symbol_arg in symbols:
            if "," in symbol_arg:
                symbol_list.extend([s.strip() for s in symbol_arg.split(",") if s.strip()])
            else:
                symbol_list.append(symbol_arg.strip())

        if not symbol_list:
            click.echo("Error: Please provide at least one non-empty token symbol", err=True)
            sys.exit(1)

        # Fetch data
        crypto_data_list = api.fetch_multiple(symbol_list)

        # Format and output
        if output_format == "json":
            formatter = JSONFormatter()
        else:
            formatter = TableFormatter()
            print_banner()

        output = formatter.format_multiple(crypto_data_list)
        click.echo(output)

    except TokenNotFoundError as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)
    except CryptoFetcherError as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)
    except KeyboardInterrupt:
        click.echo("\nAborted by user", err=True)
        sys.exit(130)
    except Exception as e:
        click.echo(f"Unexpected error: {str(e)}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
