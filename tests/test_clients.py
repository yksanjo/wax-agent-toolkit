"""Tests for WAX API clients."""

from __future__ import annotations

import pytest
import httpx
from wax_agent_toolkit.clients.wax_rpc import WAXRPCClient
from wax_agent_toolkit.clients.atomic_assets import AtomicAssetsClient
from wax_agent_toolkit.clients.alcor import AlcorClient


class TestWAXRPCClient:
    def test_get_info(self):
        """Test that we can connect to WAX and get chain info."""
        with WAXRPCClient() as client:
            info = client.get_info()
            assert "chain_id" in info
            assert "head_block_num" in info
            assert info["server_version_string"] is not None

    def test_get_account(self):
        """Test fetching a known WAX account."""
        with WAXRPCClient() as client:
            account = client.get_account("yksanjo.wax")
            assert account["account_name"] == "yksanjo.wax"

    def test_get_balance(self):
        """Test balance query returns a number."""
        with WAXRPCClient() as client:
            balance = client.get_balance("yksanjo.wax")
            assert isinstance(balance, float)
            assert balance >= 0


class TestAtomicAssetsClient:
    def test_list_collections(self):
        """Test that we can fetch top collections."""
        with AtomicAssetsClient() as client:
            collections = client.list_collections(limit=5)
            assert len(collections) <= 5
            assert len(collections) > 0
            assert "collection_name" in collections[0]

    def test_get_assets_by_owner(self):
        """Test querying assets by owner."""
        with AtomicAssetsClient() as client:
            assets = client.get_assets(owner="1.wax", limit=3)
            assert len(assets) <= 3

    def test_get_sales(self):
        """Test fetching recent sales."""
        with AtomicAssetsClient() as client:
            sales = client.get_sales(limit=5)
            assert len(sales) <= 5


class TestAlcorClient:
    def test_list_tokens(self):
        """Test that Alcor token list works."""
        with AlcorClient() as client:
            tokens = client.list_tokens()
            assert len(tokens) > 0
            assert any(
                t.get("symbol", "").upper() == "WAXP"
                for t in tokens
            )

    def test_get_waxp_price(self):
        """Test fetching WAXP price."""
        with AlcorClient() as client:
            price = client.get_token_price("WAXP")
            assert price is not None
            assert price > 0
