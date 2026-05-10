"""Low-level WAX RPC client for chain interactions."""

from __future__ import annotations

import json
from typing import Any

import httpx


class WAXRPCClient:
    """Client for interacting with the WAX blockchain via RPC.

    Handles account queries, balance checks, transaction history,
    and smart contract interactions.
    """

    def __init__(
        self,
        rpc_endpoint: str = "https://wax.greymass.com",
        timeout: float = 30.0,
    ):
        self.rpc_endpoint = rpc_endpoint.rstrip("/")
        self.timeout = timeout
        self._client = httpx.Client(timeout=timeout)

    def get_info(self) -> dict[str, Any]:
        """Get chain information (head block, chain ID, etc.)."""
        resp = self._client.post(f"{self.rpc_endpoint}/v1/chain/get_info")
        resp.raise_for_status()
        return resp.json()

    def get_account(self, account_name: str) -> dict[str, Any]:
        """Get detailed account information."""
        resp = self._client.post(
            f"{self.rpc_endpoint}/v1/chain/get_account",
            json={"account_name": account_name},
        )
        resp.raise_for_status()
        return resp.json()

    def get_balance(self, account_name: str, symbol: str = "WAXP") -> float:
        """Get token balance for an account.

        Args:
            account_name: WAX account name (e.g., 'yksanjo.wax')
            symbol: Token symbol to query (default: WAXP)

        Returns:
            Balance as a float, or 0.0 if token not found.
        """
        account = self.get_account(account_name)
        for token in account.get("core_liquid_balance", ""):
            if symbol in token:
                return float(token.split()[0])
        return 0.0

    def get_currency_balance(
        self,
        account_name: str,
        symbol: str = "WAXP",
        contract: str = "eosio.token",
    ) -> list[str]:
        """Get currency balance from a specific contract."""
        resp = self._client.post(
            f"{self.rpc_endpoint}/v1/chain/get_currency_balance",
            json={
                "code": contract,
                "account": account_name,
                "symbol": symbol,
            },
        )
        resp.raise_for_status()
        return resp.json()

    def get_transactions(
        self, account_name: str, limit: int = 10
    ) -> list[dict[str, Any]]:
        """Get recent transactions for an account.

        Uses the history API to fetch recent actions.
        """
        resp = self._client.post(
            f"{self.rpc_endpoint}/v1/history/get_actions",
            json={
                "account_name": account_name,
                "pos": -1,
                "offset": -limit,
            },
        )
        resp.raise_for_status()
        data = resp.json()
        return data.get("actions", [])

    def get_table_rows(
        self,
        contract: str,
        table: str,
        scope: str,
        limit: int = 10,
        lower_bound: str | None = None,
        upper_bound: str | None = None,
    ) -> list[dict[str, Any]]:
        """Query a smart contract table."""
        params: dict[str, Any] = {
            "code": contract,
            "table": table,
            "scope": scope,
            "limit": limit,
            "json": True,
        }
        if lower_bound:
            params["lower_bound"] = lower_bound
        if upper_bound:
            params["upper_bound"] = upper_bound

        resp = self._client.post(
            f"{self.rpc_endpoint}/v1/chain/get_table_rows",
            json=params,
        )
        resp.raise_for_status()
        return resp.json().get("rows", [])

    def close(self):
        """Close the HTTP client."""
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
