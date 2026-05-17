#!/usr/bin/env python
"""
CoinPing - Fetch cryptocurrency data from CoinGecko API.

Simple CLI tool to get real-time cryptocurrency prices, market cap, and other metrics.
"""
import sys

import click

from src.api import CoinGeckoAPI
from src.api.coingecko import MAX_TOP_TOKENS
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
TAGLINE = "CoinPing - pinging coin data directly into your terminal."


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
    "--top",
    "top_count",
    type=click.IntRange(1, MAX_TOP_TOKENS),
    help=f"Fetch top N tokens by market cap (max {MAX_TOP_TOKENS})",
)
@click.option(
    "--random",
    "random_token",
    is_flag=True,
    help="Fetch a random supported token",
)
@click.version_option(version="1.0.0", prog_name="coinping")
@click.help_option("-h", "--help")
def main(symbols, output_format, top_count, random_token):
    """
    CoinPing - Fetch cryptocurrency data from CoinGecko API.

    \b
    Examples:
      python coinping.py BTC              Single token
      python coinping.py BTC ETH SOL      Multiple tokens
      python coinping.py BTC,ETH,SOL      Comma-separated symbols
      python coinping.py BTC -f json      JSON output
      python coinping.py --top 10         Top market-cap tokens
      python coinping.py --random         Random token

    \b
    Supported formats:
      table  - Pretty ASCII table (default)
      json   - Machine-readable JSON output
    """

    try:
        api = CoinGeckoAPI()

        requested_modes = sum([
            bool(symbols),
            top_count is not None,
            random_token,
        ])

        if requested_modes == 0:
            click.echo("Error: Please provide at least one token symbol")
            click.echo("Examples: python coinping.py BTC")
            click.echo("          python coinping.py BTC ETH SOL")
            click.echo("          python coinping.py --top 10")
            click.echo("          python coinping.py --random")
            click.echo("\nUse --help for more information")
            sys.exit(1)

        if requested_modes > 1:
            click.echo(
                "Error: Provide symbols, --top, or --random, not more than one mode.",
                err=True,
            )
            sys.exit(1)

        crypto_data_list = fetch_crypto_data(api, symbols, top_count, random_token)

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
    except click.ClickException as e:
        e.show()
        sys.exit(e.exit_code)
    except Exception as e:
        click.echo(f"Unexpected error: {str(e)}", err=True)
        sys.exit(1)


def fetch_crypto_data(api, symbols, top_count, random_token):
    """Fetch data for the selected CLI mode."""
    if top_count is not None:
        if top_count > 100:
            click.echo(
                "Warning: large --top requests can consume CoinGecko API quota quickly.",
                err=True,
            )
        return api.fetch_top_tokens(top_count)

    if random_token:
        return [api.fetch_random_token()]

    symbol_list = []
    for symbol_arg in symbols:
        if "," in symbol_arg:
            symbol_list.extend([s.strip() for s in symbol_arg.split(",") if s.strip()])
        else:
            symbol_list.append(symbol_arg.strip())

    if not symbol_list:
        raise click.ClickException("Please provide at least one non-empty token symbol")

    return api.fetch_multiple(symbol_list)


if __name__ == "__main__":
    main()
