"""Client for the Alcor DEX — token swaps and liquidity on WAX."""

from __future__ import annotations

from typing import Any

import httpx


class AlcorClient:
    """Client for interacting with the Alcor DEX on WAX.

    Provides token prices, swap rates, liquidity pool data,
    and market information.
    """

    def __init__(
        self,
        api_endpoint: str = "https://api.alcor.exchange",
        timeout: float = 30.0,
    ):
        self.api_endpoint = api_endpoint.rstrip("/")
        self.timeout = timeout
        self._client = httpx.Client(timeout=timeout)

    def list_tokens(self) -> list[dict[str, Any]]:
        """Get all listed tokens on Alcor with prices."""
        resp = self._client.get(f"{self.api_endpoint}/v1/tokens")
        resp.raise_for_status()
        return resp.json()

    def get_token_price(self, symbol: str) -> float | None:
        """Get the current USD price of a token by symbol.

        Args:
            symbol: Token symbol (e.g., 'WAXP', 'TACO', 'NEFTY')

        Returns:
            Price in USD, or None if token not found.
        """
        tokens = self.list_tokens()
        for token in tokens:
            if token.get("symbol", "").upper() == symbol.upper():
                price = token.get("price")
                if price:
                    return float(price)
        return None

    def get_pools(self, limit: int = 20) -> list[dict[str, Any]]:
        """Get liquidity pools with stats."""
        resp = self._client.get(
            f"{self.api_endpoint}/v1/pools",
            params={"limit": min(limit, 100)},
        )
        resp.raise_for_status()
        return resp.json()

    def get_swap_quote(
        self,
        from_token: str,
        to_token: str,
        amount: float,
    ) -> dict[str, Any] | None:
        """Get a swap quote between two tokens.

        Args:
            from_token: Source token symbol
            to_token: Target token symbol
            amount: Amount of source token to swap

        Returns:
            Quote with expected output and price impact, or None.
        """
        params = {
            "from": from_token.upper(),
            "to": to_token.upper(),
            "amount": str(amount),
        }
        resp = self._client.get(
            f"{self.api_endpoint}/v1/swap/quote",
            params=params,
        )
        if resp.status_code == 200:
            return resp.json()
        return None

    def get_market_stats(self) -> dict[str, Any]:
        """Get overall market statistics."""
        resp = self._client.get(f"{self.api_endpoint}/v1/market/stats")
        resp.raise_for_status()
        return resp.json()

    def close(self):
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
