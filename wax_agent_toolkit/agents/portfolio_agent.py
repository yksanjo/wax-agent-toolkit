"""PortfolioAgent — AI agent for WAX portfolio tracking and analysis."""

from __future__ import annotations

from typing import Any

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from ..clients.wax_rpc import WAXRPCClient
from ..clients.atomic_assets import AtomicAssetsClient
from ..clients.alcor import AlcorClient


class PortfolioAgent:
    """High-level agent for tracking WAX portfolios.

    Combines on-chain data, NFT holdings, and DEX prices
    to give a complete picture of a WAX account's value.
    """

    def __init__(
        self,
        rpc_endpoint: str | None = None,
        atomic_endpoint: str | None = None,
        alcor_endpoint: str | None = None,
    ):
        self.rpc = WAXRPCClient(rpc_endpoint or "https://wax.greymass.com")
        self.atomic = AtomicAssetsClient(api_endpoint=atomic_endpoint or "")
        self.alcor = AlcorClient(api_endpoint=alcor_endpoint or "")

    def get_portfolio_summary(self, account_name: str) -> str:
        """Get a complete portfolio summary for a WAX account.

        Args:
            account_name: WAX account name

        Returns:
            Formatted portfolio report with balances, NFTs, and estimated value.
        """
        # Get WAXP balance
        waxp_balance = self.rpc.get_balance(account_name)

        # Get WAXP price
        waxp_price = self.alcor.get_token_price("WAXP")
        usd_value = waxp_balance * waxp_price if waxp_price else 0

        # Get NFT holdings
        nfts = self.atomic.get_assets(owner=account_name, limit=100)
        nft_count = len(nfts)

        # Get recent transactions
        txns = self.rpc.get_transactions(account_name, limit=5)

        # Get chain info
        info = self.rpc.get_info()
        head_block = info.get("head_block_num", "?")

        report = f"""
📊 WAX Portfolio Report — {account_name}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⛓️  Chain: WAX Mainnet
🔢 Head Block: {head_block:,}

💰 WAXP Balance: {waxp_balance:,.4f} WAXP
💵 USD Value: ${usd_value:,.2f} (at ${waxp_price:.4f}/WAXP)

🖼️  NFT Holdings: {nft_count} assets

🔄 Recent Transactions:
"""
        for txn in txns[:5]:
            action = txn.get("action_trace", {})
            act = action.get("act", {})
            name = act.get("name", "?")
            data = act.get("data", {})
            if name == "transfer":
                from_acct = data.get("from", "?")
                to_acct = data.get("to", "?")
                quantity = data.get("quantity", "?")
                memo = data.get("memo", "")
                report += f"  • {name}: {quantity} ({from_acct} → {to_acct}) {memo}\n"
            else:
                report += f"  • {name}\n"

        return report

    def get_nft_portfolio(self, account_name: str) -> str:
        """Get detailed NFT portfolio for an account.

        Args:
            account_name: WAX account name

        Returns:
            Formatted table of NFT holdings by collection.
        """
        nfts = self.atomic.get_assets(owner=account_name, limit=200)

        # Group by collection
        collections: dict[str, list[dict[str, Any]]] = {}
        for nft in nfts:
            col_name = (
                nft.get("collection", {})
                .get("collection_name", "Unknown")
            )
            if col_name not in collections:
                collections[col_name] = []
            collections[col_name].append(nft)

        console = Console()
        table = Table(title=f"🖼️  NFT Portfolio — {account_name}")
        table.add_column("Collection", style="cyan")
        table.add_column("Count", justify="right", style="green")
        table.add_column("Rarest Template", style="yellow")

        for col_name, items in sorted(
            collections.items(), key=lambda x: -len(x[1])
        ):
            # Find the rarest template (lowest supply)
            rarest = "N/A"
            for item in items[:10]:
                template = item.get("template", {})
                supply = template.get("issued_supply", 0)
                if supply:
                    rarest = f"#{template.get('template_id', '?')} ({supply} issued)"

            table.add_row(
                col_name,
                str(len(items)),
                rarest,
            )

        with console.capture() as capture:
            console.print(table)
        return capture.getvalue()

    def estimate_net_worth(self, account_name: str) -> str:
        """Estimate the total net worth of a WAX account.

        Combines WAXP balance + estimated NFT floor values.

        Args:
            account_name: WAX account name

        Returns:
            Estimated net worth breakdown.
        """
        waxp_balance = self.rpc.get_balance(account_name)
        waxp_price = self.alcor.get_token_price("WAXP")
        waxp_usd = waxp_balance * waxp_price if waxp_price else 0

        nfts = self.atomic.get_assets(owner=account_name, limit=200)
        nft_count = len(nfts)

        report = f"""
💰 Net Worth Estimate — {account_name}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💎 WAXP: {waxp_balance:,.4f} (${waxp_usd:,.2f})
🖼️  NFTs: {nft_count} assets (floor value not included — requires marketplace API)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Estimated Total: ${waxp_usd:,.2f}+ (NFTs excluded)
"""
        return report
