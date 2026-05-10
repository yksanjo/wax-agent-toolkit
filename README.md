# 🧰 WAX Agent Toolkit

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI](https://img.shields.io/badge/PyPI-coming%20soon-orange)](https://pypi.org)
[![PRs Welcome](https://img.shields.io/badge/PRs-Welcome-brightgreen.svg)](https://github.com/yksanjo/wax-agent-toolkit/pulls)

**Python toolkit for building AI agents on the WAX blockchain.** Query NFTs, track portfolios, monitor whale activity, and interact with the WAX ecosystem — all from Python.

> Built for developers building AI agents, trading bots, portfolio trackers, and NFT analytics tools on WAX.

---

## ✨ Features

| Module | What It Does |
|--------|-------------|
| **`WAXRPCClient`** | Account balances, transaction history, chain info, smart contract queries |
| **`AtomicAssetsClient`** | NFT assets, collections, templates, marketplace sales |
| **`AlcorClient`** | Token prices, swap quotes, liquidity pools, market stats |
| **`NFTAnalystAgent`** | Collection reports, top collections ranking, whale sale monitoring |
| **`PortfolioAgent`** | Full portfolio summaries, NFT holdings breakdown, net worth estimation |

---

## 🚀 Quick Start

### Install

```bash
pip install wax-agent-toolkit
```

Or from source:

```bash
git clone https://github.com/yksanjo/wax-agent-toolkit.git
cd wax-agent-toolkit
pip install -e .
```

### CLI Usage

```bash
# Check WAXP balance
wax-agent balance yksanjo.wax

# Full portfolio report
wax-agent portfolio yksanjo.wax

# List NFT holdings
wax-agent nfts 1.wax

# Top NFT collections
wax-agent collections --limit 20

# Recent sales
wax-agent sales --collection alienworlds

# WAXP price
wax-agent price

# Whale alerts
wax-agent whales --collection alienworlds --min-price 500

# Chain info
wax-agent info
```

### Python Usage

```python
from wax_agent_toolkit import WAXRPCClient, AtomicAssetsClient, AlcorClient

# Check a balance
with WAXRPCClient() as wax:
    balance = wax.get_balance("yksanjo.wax")
    print(f"💰 Balance: {balance} WAXP")

# Query NFTs
with AtomicAssetsClient() as atomic:
    nfts = atomic.get_assets(owner="1.wax", limit=5)
    for nft in nfts:
        print(f"🖼️  {nft['name']} — {nft['collection']['collection_name']}")

# Get token price
with AlcorClient() as alcor:
    price = alcor.get_token_price("WAXP")
    print(f"💵 WAXP: ${price:.4f}")
```

### AI Agent Usage

```python
from wax_agent_toolkit import NFTAnalystAgent, PortfolioAgent

# NFT analysis
nft_agent = NFTAnalystAgent()
report = nft_agent.get_collection_report("alienworlds")
print(report)

# Portfolio tracking
portfolio_agent = PortfolioAgent()
summary = portfolio_agent.get_portfolio_summary("yksanjo.wax")
print(summary)
```

---

## 🎯 Example: NFT Whale Monitor

Monitor a collection for big sales in real-time:

```bash
python -m wax_agent_toolkit.examples.nft_monitor \
    --collection alienworlds \
    --min-price 500 \
    --interval 30
```

## 🎯 Example: Portfolio Tracker

Track multiple WAX accounts:

```bash
python -m wax_agent_toolkit.examples.portfolio_tracker \
    --accounts yksanjo.wax,1.wax,test.gm \
    --interval 60
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                   Your AI Agent                      │
│  (Claude, Cursor, custom Python bot, etc.)           │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│              wax-agent-toolkit                        │
│                                                       │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────┐  │
│  │ WAXRPCClient│  │AtomicAssets  │  │AlcorClient │  │
│  │ (balances,  │  │ (NFTs,       │  │ (prices,   │  │
│  │  txns,      │  │  collections,│  │  swaps,    │  │
│  │  contracts) │  │  sales)      │  │  pools)    │  │
│  └──────┬──────┘  └──────┬───────┘  └─────┬──────┘  │
│         │                │                 │         │
│  ┌──────▼────────────────▼─────────────────▼──────┐  │
│  │         High-Level Agents                       │  │
│  │  ┌─────────────────┐  ┌────────────────────┐   │  │
│  │  │ NFTAnalystAgent │  │ PortfolioAgent     │   │  │
│  │  │ (reports,       │  │ (portfolio,        │   │  │
│  │  │  whales,        │  │  net worth,        │   │  │
│  │  │  rankings)      │  │  tracking)         │   │  │
│  │  └─────────────────┘  └────────────────────┘   │  │
│  └─────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
   WAX RPC       AtomicAssets     Alcor DEX
   (on-chain)    (NFT data)       (prices/swaps)
```

---

## 🔗 Related Projects

- [**wax-mcp-server**](https://github.com/yksanjo/wax-mcp-server) — MCP server for WAX (use this with Claude Desktop)
- [**mcp-discovery**](https://github.com/yksanjo/mcp-discovery) — World's largest MCP server index

---

## 📄 License

MIT

---

<div align="center">
  <strong>⭐ Star if you build on WAX — let's grow the ecosystem together!</strong>
  <br>
  <em>Built by <a href="https://github.com/yksanjo">Yoshi Kondo</a> · Music Ai Lab</em>
</div>
