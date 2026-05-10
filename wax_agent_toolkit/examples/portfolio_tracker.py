"""Example: Portfolio Tracker — monitor a list of WAX accounts.

Run with:
    python -m wax_agent_toolkit.examples.portfolio_tracker --accounts account1,account2
"""

from __future__ import annotations

import argparse
import time

from rich.live import Live
from rich.table import Table
from rich.console import Console

from ..clients.wax_rpc import WAXRPCClient
from ..clients.atomic_assets import AtomicAssetsClient
from ..clients.alcor import AlcorClient


def track_portfolios(accounts: list[str], interval: int = 60):
    """Track WAXP balance and NFT count for a list of accounts."""
    console = Console()

    with Live(refresh_per_second=1 / interval) as live:
        while True:
            table = Table(
                title=f"📊 WAX Portfolio Tracker — {time.strftime('%H:%M:%S')}"
            )
            table.add_column("Account", style="cyan")
            table.add_column("WAXP Balance", justify="right")
            table.add_column("USD Value", justify="right")
            table.add_column("NFTs", justify="right")

            with WAXRPCClient() as rpc:
                with AtomicAssetsClient() as atomic:
                    with AlcorClient() as alcor:
                        waxp_price = alcor.get_token_price("WAXP") or 0

                        for account in accounts:
                            try:
                                balance = rpc.get_balance(account)
                                usd = balance * waxp_price
                                nfts = atomic.get_assets(
                                    owner=account, limit=1
                                )
                                # Get actual count via stats
                                nft_count = len(
                                    atomic.get_assets(
                                        owner=account, limit=100
                                    )
                                )

                                table.add_row(
                                    account,
                                    f"{balance:,.4f}",
                                    f"${usd:,.2f}",
                                    str(nft_count),
                                )
                            except Exception as e:
                                table.add_row(
                                    account,
                                    "[red]Error[/]",
                                    str(e)[:20],
                                    "?",
                                )

            live.update(table)
            time.sleep(interval)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="WAX Portfolio Tracker"
    )
    parser.add_argument(
        "--accounts",
        "-a",
        required=True,
        help="Comma-separated list of WAX accounts",
    )
    parser.add_argument(
        "--interval",
        "-i",
        type=int,
        default=60,
        help="Refresh interval in seconds",
    )
    args = parser.parse_args()
    accounts = [a.strip() for a in args.accounts.split(",")]
    track_portfolios(accounts, args.interval)
