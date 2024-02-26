from __future__ import annotations

from typing import List

import httpx

from hueniverse.hue_types import DiscoveredBridge, ResourceType, AppKeyResponse, Light

_DISCOVERY_URL = 'https://discovery.meethue.com/'

class AsyncBridge:
    """Represents a Philips Hue bridge."""

    def __init__(
        self,
        ip_address: str,
        app_key: str | None = None,
        id: str | None = None,
        port: int | None = None,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        """Initialize a Bridge instance."""
        self._id = id
        self._ip_address = ip_address
        self._app_key = app_key
        self._port = port

        self._url = f'https://{self.ip_address}/clip/v2//resource'
        self._key_post_url = f'https://{self.ip_address}/api'

        self._client = http_client or httpx.AsyncClient()


    @property
    def ip_address(self) -> str:
        return self._ip_address

    @property
    def id(self) -> str:
        return self._id

    @property
    def app_key(self) -> str | None:
        return self._app_key

    @app_key.setter
    def app_key(self, app_key: str) -> None:
        self._app_key = app_key

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._client.aclose()

    async def _get(self, resource_type: ResourceType, resource_identifier: str | None = None):

        assert self._app_key is not None, 'App key is required for this operation'

        url = (
            f'{self._url}/{resource_type.value}/{resource_identifier}'
           if resource_identifier is not None
           else f'{self._url}/{resource_type.value}'
        )

        response = await self._client.get(
            url=url,
            headers={'hue-application-key': self._app_key},
        )

        response.raise_for_status()
        return response.json()

    async def get_lights(self) -> List[Light]:
        """Get a list of lights connected to the bridge."""

        res = await self._get(ResourceType.LIGHT)
        return [Light(**x) for x in res['data']]


    async def get_light_by_id(self, resource_identifier: str) -> Light | None:
        """Get a light by its resource identifier."""

        res = await self._get(ResourceType.LIGHT, resource_identifier)
        return Light(**res['data'][0]) if res['data'] else None


    async def create_app_key(self, app_name: str, instance_name: str) -> AppKeyResponse:
        """Create app key, for the app to communicate with the bridge"""

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

        return AppKeyResponse(**response_data[0]['success'])


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
        result = await http.get(url=_DISCOVERY_URL)
        result.raise_for_status()
        return [DiscoveredBridge(**item) for item in result.json()]
