"""Example: NFT Whale Monitor — watch for big sales in real-time.

Run with:
    python -m wax_agent_toolkit.examples.nft_monitor --collection alienworlds --min-price 500
"""

from __future__ import annotations

import argparse
import time

from rich.live import Live
from rich.table import Table
from rich.console import Console

from ..clients.atomic_assets import AtomicAssetsClient


def monitor_sales(collection: str, min_price: float, interval: int = 30):
    """Monitor a collection for sales above min_price."""
    console = Console()
    seen_sales: set[str] = set()

    console.print(
        f"[bold cyan]🐋 Whale Monitor Active[/]\n"
        f"   Collection: {collection}\n"
        f"   Min Price: {min_price} WAXP\n"
        f"   Checking every {interval}s\n"
    )

    with AtomicAssetsClient() as atomic:
        while True:
            try:
                sales = atomic.get_sales(
                    collection=collection, limit=20
                )

                new_sales = []
                for sale in sales:
                    sale_id = sale.get("sale_id", str(time.time()))
                    if sale_id not in seen_sales:
                        seen_sales.add(sale_id)
                        sd = sale.get("data", sale)
                        price = float(
                            sd.get("price", {}).get("amount", 0)
                        )
                        if price >= min_price:
                            new_sales.append(
                                {
                                    "asset": sd.get("assets", [{}])[
                                        0
                                    ].get("name", "Unknown"),
                                    "price": price,
                                    "buyer": sd.get("buyer", "?"),
                                    "seller": sd.get("seller", "?"),
                                }
                            )

                if new_sales:
                    table = Table(
                        title=f"🐋 Whale Sales — {collection}"
                    )
                    table.add_column("Asset", style="cyan")
                    table.add_column("Price", justify="right")
                    table.add_column("Buyer")
                    table.add_column("Seller")

                    for s in new_sales:
                        table.add_row(
                            s["asset"],
                            f"{s['price']:.2f} WAXP",
                            s["buyer"],
                            s["seller"],
                        )
                    console.print(table)

                time.sleep(interval)

            except KeyboardInterrupt:
                console.print("\n[yellow]👋 Monitor stopped[/]")
                break
            except Exception as e:
                console.print(f"[red]❌ Error: {e}[/]")
                time.sleep(interval)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="WAX NFT Whale Monitor"
    )
    parser.add_argument(
        "--collection",
        "-c",
        default="alienworlds",
        help="Collection to monitor",
    )
    parser.add_argument(
        "--min-price",
        "-p",
        type=float,
        default=500,
        help="Minimum price in WAXP to flag",
    )
    parser.add_argument(
        "--interval",
        "-i",
        type=int,
        default=30,
        help="Check interval in seconds",
    )
    args = parser.parse_args()
    monitor_sales(args.collection, args.min_price, args.interval)
