"""NFTAnalystAgent — AI agent for WAX NFT analysis and monitoring."""

from __future__ import annotations

from typing import Any

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from ..clients.atomic_assets import AtomicAssetsClient


class NFTAnalystAgent:
    """High-level agent for NFT analysis on WAX.

    Provides natural-language-friendly methods for querying
    collections, assets, sales, and generating reports.
    """

    def __init__(self, atomic_endpoint: str | None = None):
        self.atomic = AtomicAssetsClient(api_endpoint=atomic_endpoint or "")

    def get_collection_report(self, collection_name: str) -> str:
        """Generate a human-readable report for an NFT collection.

        Args:
            collection_name: Name of the WAX NFT collection

        Returns:
            Formatted report string with collection details.
        """
        collection = self.atomic.get_collection(collection_name)
        if not collection:
            return f"❌ Collection '{collection_name}' not found."

        data = collection.get("data", collection)
        name = data.get("name", collection_name)
        author = data.get("author", "unknown")
        assets = data.get("assets", "?")
        templates = data.get("templates", "?")
        description = data.get("description", "No description available.")

        # Get recent sales
        sales = self.atomic.get_sales(collection=collection_name, limit=5)

        report = f"""
📦 Collection: {name}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👤 Author: {author}
🖼️  Assets: {assets:,}
📋 Templates: {templates:,}
📝 Description: {description[:200]}

🔄 Recent Sales:
"""
        for sale in sales[:5]:
            sale_data = sale.get("data", sale)
            price = sale_data.get("price", {}).get("amount", "?")
            token_symbol = sale_data.get("price", {}).get("token_symbol", "WAXP")
            buyer = sale_data.get("buyer", "?")
            report += f"  • {price} {token_symbol} — buyer: {buyer}\n"

        return report

    def get_top_collections(self, limit: int = 10) -> str:
        """Get a ranked list of top NFT collections.

        Args:
            limit: Number of collections to return

        Returns:
            Formatted table of top collections.
        """
        collections = self.atomic.list_collections(limit=limit)

        console = Console()
        table = Table(title=f"🏆 Top {limit} WAX NFT Collections")
        table.add_column("#", style="dim")
        table.add_column("Collection", style="cyan")
        table.add_column("Assets", justify="right", style="green")
        table.add_column("Author", style="yellow")

        for i, col in enumerate(collections, 1):
            name = col.get("collection_name", "?")
            assets = f"{col.get('assets', 0):,}"
            author = col.get("author", "?")
            table.add_row(str(i), name, assets, author)

        with console.capture() as capture:
            console.print(table)
        return capture.getvalue()

    def monitor_whale_activity(
        self, collection_name: str, min_price: float = 100.0
    ) -> str:
        """Check for significant sales in a collection.

        Args:
            collection_name: Collection to monitor
            min_price: Minimum price in WAXP to flag as significant

        Returns:
            Report of significant sales found.
        """
        sales = self.atomic.get_sales(collection=collection_name, limit=50)
        significant = []

        for sale in sales:
            sale_data = sale.get("data", sale)
            price_data = sale_data.get("price", {})
            amount = float(price_data.get("amount", 0))
            token_symbol = price_data.get("token_symbol", "WAXP")

            if amount >= min_price:
                significant.append(
                    {
                        "asset": sale_data.get("assets", [{}])[0].get(
                            "name", "Unknown"
                        ),
                        "price": amount,
                        "symbol": token_symbol,
                        "buyer": sale_data.get("buyer", "?"),
                        "seller": sale_data.get("seller", "?"),
                    }
                )

        if not significant:
            return (
                f"🐋 No significant sales (>={min_price} WAXP) found in "
                f"'{collection_name}' recently."
            )

        report = f"🐋 Whale Alert — {collection_name}\n"
        report += "━" * 40 + "\n"
        for s in significant:
            report += (
                f"  • {s['asset']} — {s['price']} {s['symbol']}\n"
                f"    Buyer: {s['buyer']} | Seller: {s['seller']}\n"
            )

        return report
