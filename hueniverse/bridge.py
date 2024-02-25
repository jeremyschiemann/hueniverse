from __future__ import annotations

from typing import List

import httpx

from hueniverse.hue_types import DiscoveredBridge, AppKey

_DISCOVERY_URL = 'https://discovery.meethue.com/'

class AsyncBridge:
    """Represents a Philips Hue bridge."""

    def __init__(
        self,
        ip_address: str,
        id: str | None = None,
        port: int | None = None,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        """Initialize a Bridge instance."""
        self._id = id
        self._ip_address = ip_address
        self._port = port

        self._url = f'https://{self.ip_address}/clip/v2'
        self._key_post_url = f'https://{self.ip_address}/api'

        self._client = http_client or httpx.AsyncClient()


    @property
    def ip_address(self) -> str:
        return self._ip_address

    @property
    def id(self) -> str:
        return self._id

    @property
    def port(self) -> int:
        return self._port

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._client.aclose()


    async def create_app_key(self, app_name: str, instance_name: str) -> AppKey:
        """Create app key and save it in instance."""

        response = await self._client.post(
            url=self._key_post_url,
            json={
                'devicetype': f'{app_name}#{instance_name}',
                'generateclientkey': True,
            },
        )
        response.raise_for_status()
        response_data = response.json()

        if 'error' in response_data[0]:
            raise PermissionError(response_data[0]['error']['description'])

        return AppKey(**response_data[0]['success'])


    @classmethod
    async def from_discover(cls, http_client: httpx.AsyncClient) -> List[AsyncBridge]:
        """Create Bridge instances from discovered bridges."""
        return [
            cls(id=bridge.id, ip_address=bridge.internalipaddress, port=bridge.port, http_client=http_client)
            for bridge in await cls.discover(http_client)
        ]

    @classmethod
    async def from_discover_single(cls, http_client: httpx.AsyncClient) -> AsyncBridge | None:
        """Create a single Bridge instance from the first discovered bridge."""
        discovered_bridges = await cls.discover(http_client)

        if not discovered_bridges:
            return None

        return cls(
            id=discovered_bridges[0].id,
            ip_address=discovered_bridges[0].internalipaddress,
            port=discovered_bridges[0].port,
            http_client=http_client,
        )


    @staticmethod
    async def discover(http_client: httpx.AsyncClient | None = None) -> List[DiscoveredBridge]:
        """Discover Philips Hue bridges on the local network."""
        http = http_client or httpx.AsyncClient()
        result = await http.get(_DISCOVERY_URL)
        result.raise_for_status()
        await http.aclose()
        return [DiscoveredBridge(**item) for item in result.json()]


    @staticmethod
    def hue_app