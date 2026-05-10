"""Client for the AtomicAssets API — NFT data on WAX."""

from __future__ import annotations

from typing import Any

import httpx


class AtomicAssetsClient:
    """Client for querying NFT data via the AtomicAssets API.

    Provides access to assets, collections, templates, and marketplace sales
    on the WAX blockchain.
    """

    def __init__(
        self,
        api_endpoint: str = "https://wax.api.atomicassets.io",
        timeout: float = 30.0,
    ):
        self.api_endpoint = api_endpoint.rstrip("/")
        self.timeout = timeout
        self._client = httpx.Client(timeout=timeout)

    def get_assets(
        self,
        owner: str | None = None,
        collection: str | None = None,
        limit: int = 20,
        page: int = 1,
    ) -> list[dict[str, Any]]:
        """Query NFT assets by owner or collection.

        Args:
            owner: WAX account name to filter by owner
            collection: Collection name to filter by
            limit: Number of results per page (max 100)
            page: Page number

        Returns:
            List of asset objects with metadata, images, and attributes.
        """
        params: dict[str, Any] = {"limit": min(limit, 100), "page": page}
        if owner:
            params["owner"] = owner
        if collection:
            params["collection_name"] = collection

        resp = self._client.get(
            f"{self.api_endpoint}/atomicassets/v1/assets",
            params=params,
        )
        resp.raise_for_status()
        return resp.json().get("data", [])

    def get_asset(self, asset_id: str) -> dict[str, Any] | None:
        """Get a single NFT asset by ID."""
        resp = self._client.get(
            f"{self.api_endpoint}/atomicassets/v1/assets/{asset_id}"
        )
        resp.raise_for_status()
        data = resp.json().get("data")
        return data

    def get_collection(self, collection_name: str) -> dict[str, Any] | None:
        """Get detailed info about an NFT collection."""
        resp = self._client.get(
            f"{self.api_endpoint}/atomicassets/v1/collections/{collection_name}"
        )
        resp.raise_for_status()
        return resp.json().get("data")

    def list_collections(
        self,
        limit: int = 20,
        page: int = 1,
        sort: str = "assets",
        order: str = "desc",
    ) -> list[dict[str, Any]]:
        """Browse NFT collections, sorted by asset count.

        Args:
            limit: Results per page
            page: Page number
            sort: Sort field (assets, volume, name)
            order: asc or desc

        Returns:
            List of collection objects.
        """
        params: dict[str, Any] = {
            "limit": min(limit, 100),
            "page": page,
            "sort": sort,
            "order": order,
        }
        resp = self._client.get(
            f"{self.api_endpoint}/atomicassets/v1/collections",
            params=params,
        )
        resp.raise_for_status()
        return resp.json().get("data", [])

    def get_sales(
        self,
        collection: str | None = None,
        limit: int = 20,
        page: int = 1,
    ) -> list[dict[str, Any]]:
        """Get recent NFT marketplace sales.

        Args:
            collection: Filter by collection name
            limit: Results per page
            page: Page number

        Returns:
            List of sale objects with prices, buyers, sellers.
        """
        params: dict[str, Any] = {
            "limit": min(limit, 100),
            "page": page,
            "order": "desc",
            "sort": "updated_at_time",
        }
        if collection:
            params["collection_name"] = collection

        resp = self._client.get(
            f"{self.api_endpoint}/atomicmarket/v1/sales",
            params=params,
        )
        resp.raise_for_status()
        return resp.json().get("data", [])

    def get_template(
        self, collection_name: str, template_id: str
    ) -> dict[str, Any] | None:
        """Get a specific template from a collection."""
        resp = self._client.get(
            f"{self.api_endpoint}/atomicassets/v1/templates/{collection_name}/{template_id}"
        )
        resp.raise_for_status()
        return resp.json().get("data")

    def get_stats(self) -> dict[str, Any]:
        """Get overall WAX NFT ecosystem statistics."""
        resp = self._client.get(
            f"{self.api_endpoint}/atomicassets/v1/stats"
        )
        resp.raise_for_status()
        return resp.json().get("data", {})

    def close(self):
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
