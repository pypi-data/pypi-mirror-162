from typing import TypedDict

__all__ = ("Config",)


class Config(TypedDict):
    uuid: str
    fleet: str
    mqttId: str
    token: str
    version: int
    timestamp: str
    site: str
