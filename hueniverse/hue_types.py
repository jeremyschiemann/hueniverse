from dataclasses import dataclass
from typing import Dict


@dataclass(slots=True, frozen=True)
class DiscoveredBridge:
    id: str
    internalipaddress: str
    port: int


@dataclass(slots=True, frozen=True)
class AppKey:
    username: str
    clientkey: str

    def as_header(self) -> Dict[str, str]:
        return {
            'hue-application-key': self.username,
        }