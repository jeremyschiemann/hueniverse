from __future__ import annotations

import ssl
from typing import List, Dict, Any
from cryptography.x509 import load_pem_x509_certificate
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
        port: int = 443,
    ) -> None:
        """Initialize a Bridge instance."""
        self._id = id
        self._ip_address = ip_address
        self._app_key = app_key
        self._port = port

        self._url = f'https://{self.ip_address}/clip/v2/resource'

        self._uses_self_signed_cert = False

        if port and ip_address:
            server_cert = ssl.get_server_certificate((ip_address, port)).encode('utf-8')
            cert = load_pem_x509_certificate(server_cert)
            if cert.issuer == cert.subject:
                self._uses_self_signed_cert = True
            subject_cn = [x.rfc4514_string() for x in cert.subject.rdns if x.rfc4514_string().startswith('CN')][0]
            if not subject_cn.endswith(id):
                raise AssertionError('Bridge ID does not match certificate CN.')

        self._client = httpx.AsyncClient(
            verify=not self._uses_self_signed_cert,
            #cert='./hueniverse/signify.pem',
        )


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



    async def put_resource(
        self,
        resource_type: ResourceType,
        resource_identifier: str,
        data: Dict[str, Any],
    ):
        assert self._app_key is not None, 'App key is required for this operation'

        url = f'{self._url}/{resource_type.value}/{resource_identifier}'

        response = await self._client.put(
            url=url,
            headers={'hue-application-key': self._app_key},
            json=data,
        )
        response.raise_for_status()
        return response.json()


    async def _get_resource(
        self,
        resource_type: ResourceType,
        resource_identifier: str | None = None,
    ) -> List[Dict[str, Any]]:

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

        json_response = response.json()

        if json_response['errors']:
            raise ConnectionError(json_response['errors'])

        return json_response['data']

    async def get_lights(self) -> List[Light]:
        """Get a list of lights connected to the bridge."""

        return [Light(bridge=self, **x) for x in await self._get_resource(ResourceType.LIGHT)]


    async def get_light_by_id(self, resource_identifier: str) -> Light:
        """Get a light by its resource identifier."""

        res = await self._get_resource(ResourceType.LIGHT, resource_identifier)
        return Light(**res[0])


    async def create_app_key(self, app_name: str, instance_name: str) -> AppKeyResponse:
        """Create app key, for the app to communicate with the bridge"""

        response = await self._client.post(
            url=f'https://{self.ip_address}/api',
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
    def from_discover(cls) -> List[AsyncBridge]:
        """Create Bridge instances from discovered bridges."""
        return [
            cls(id=bridge.id, ip_address=bridge.internalipaddress, port=bridge.port)
            for bridge in cls.discover()
        ]

    @classmethod
    def from_discover_single(cls) -> AsyncBridge | None:
        """Create a single Bridge instance from the first discovered bridge."""
        discovered_bridges = cls.discover()

        if not discovered_bridges:
            return None

        return cls(
            id=discovered_bridges[0].id,
            ip_address=discovered_bridges[0].internalipaddress,
            port=discovered_bridges[0].port,
        )


    @staticmethod
    def discover() -> List[DiscoveredBridge]:
        """Discover Philips Hue bridges on the local network."""
        result = httpx.get(url=_DISCOVERY_URL)
        result.raise_for_status()
        return [DiscoveredBridge(**item) for item in result.json()]
