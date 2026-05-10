"""CLI entry point for wax-agent-toolkit."""

from __future__ import annotations

import argparse
import sys

from rich.console import Console
from rich.panel import Panel

from .clients.wax_rpc import WAXRPCClient
from .clients.atomic_assets import AtomicAssetsClient
from .clients.alcor import AlcorClient
from .agents.nft_agent import NFTAnalystAgent
from .agents.portfolio_agent import PortfolioAgent

console = Console()


def main():
    parser = argparse.ArgumentParser(
        description="wax-agent-toolkit — AI toolkit for the WAX blockchain",
    )
    parser.add_argument(
        "command",
        choices=[
            "balance",
            "portfolio",
            "nfts",
            "collections",
            "sales",
            "price",
            "whales",
            "info",
        ],
        nargs="?",
        help="Command to run",
    )
    parser.add_argument(
        "account",
        nargs="?",
        help="WAX account name (for balance, portfolio, nfts)",
    )
    parser.add_argument(
        "--collection",
        "-c",
        help="Collection name (for sales, whales)",
    )
    parser.add_argument(
        "--limit",
        "-l",
        type=int,
        default=10,
        help="Result limit (default: 10)",
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        console.print(
            Panel(
                "[bold cyan]wax-agent-toolkit[/]\n\n"
                "Commands:\n"
                "  balance <account>     Check WAXP balance\n"
                "  portfolio <account>   Full portfolio summary\n"
                "  nfts <account>        List NFT holdings\n"
                "  collections           Top NFT collections\n"
                "  sales --collection    Recent sales\n"
                "  price                 WAXP price\n"
                "  whales --collection   Whale alerts\n"
                "  info                  Chain info",
                title="🌐 WAX Blockchain Toolkit",
            )
        )
        return

    try:
        if args.command == "balance":
            if not args.account:
                console.print("[red]❌ Please provide an account name[/]")
                sys.exit(1)
            with WAXRPCClient() as rpc:
                balance = rpc.get_balance(args.account)
                console.print(
                    f"[green]💰 {args.account}: {balance:,.4f} WAXP[/]"
                )

        elif args.command == "portfolio":
            if not args.account:
                console.print("[red]❌ Please provide an account name[/]")
                sys.exit(1)
            agent = PortfolioAgent()
            report = agent.get_portfolio_summary(args.account)
            console.print(Panel(report, title="📊 Portfolio"))

        elif args.command == "nfts":
            if not args.account:
                console.print("[red]❌ Please provide an account name[/]")
                sys.exit(1)
            agent = PortfolioAgent()
            report = agent.get_nft_portfolio(args.account)
            console.print(report)

        elif args.command == "collections":
            agent = NFTAnalystAgent()
            report = agent.get_top_collections(limit=args.limit)
            console.print(report)

        elif args.command == "sales":
            agent = NFTAnalystAgent()
            if args.collection:
                report = agent.get_collection_report(args.collection)
            else:
                with AtomicAssetsClient() as atomic:
                    sales = atomic.get_sales(limit=args.limit)
                    report = "🔄 Recent Sales:\n"
                    for sale in sales:
                        sd = sale.get("data", sale)
                        price = sd.get("price", {}).get("amount", "?")
                        sym = sd.get("price", {}).get("token_symbol", "WAXP")
                        col = sd.get("collection_name", "?")
                        report += f"  • {col} — {price} {sym}\n"
            console.print(report)

        elif args.command == "price":
            with AlcorClient() as alcor:
                price = alcor.get_token_price("WAXP")
                if price:
                    console.print(
                        f"[green]💵 WAXP Price: ${price:.4f}[/]"
                    )
                else:
                    console.print("[red]❌ Could not fetch WAXP price[/]")

        elif args.command == "whales":
            if not args.collection:
                console.print(
                    "[red]❌ Please provide --collection name[/]"
                )
                sys.exit(1)
            agent = NFTAnalystAgent()
            report = agent.monitor_whale_activity(
                args.collection, min_price=100
            )
            console.print(report)

        elif args.command == "info":
            with WAXRPCClient() as rpc:
                info = rpc.get_info()
                console.print(
                    Panel(
                        f"Chain ID: {info.get('chain_id', '?')[:20]}...\n"
                        f"Head Block: {info.get('head_block_num', '?'):,}\n"
                        f"Server: {info.get('server_version_string', '?')}\n"
                        f"Last Irreversible: {info.get('last_irreversible_block_num', '?'):,}",
                        title="⛓️  WAX Chain Info",
                    )
                )

    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/]")
        sys.exit(1)


if __name__ == "__main__":
    main()
