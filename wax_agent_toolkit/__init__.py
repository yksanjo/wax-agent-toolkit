"""wax-agent-toolkit — Python toolkit for building AI agents on the WAX blockchain."""

__version__ = "0.1.0"

from .clients.wax_rpc import WAXRPCClient
from .clients.atomic_assets import AtomicAssetsClient
from .clients.alcor import AlcorClient
from .agents.nft_agent import NFTAnalystAgent
from .agents.portfolio_agent import PortfolioAgent

__all__ = [
    "WAXRPCClient",
    "AtomicAssetsClient",
    "AlcorClient",
    "NFTAnalystAgent",
    "PortfolioAgent",
]
