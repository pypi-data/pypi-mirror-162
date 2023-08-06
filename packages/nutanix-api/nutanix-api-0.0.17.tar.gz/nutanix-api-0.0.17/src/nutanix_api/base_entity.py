from abc import ABC, abstractmethod
from typing import Any, Dict, List

from .api_client import NutanixApiClient


class BaseEntity(ABC):
    WAIT_INTERVAL = 3
    UPDATE_WAIT_TIMEOUT = 300

    base_route = ""  # Need to override on each Inheriting class

    def __init__(self, api_client: NutanixApiClient) -> None:
        self._api_client = api_client

    @property
    @abstractmethod
    def uuid(self):
        pass

    @classmethod
    def __assert_base_route(cls):
        assert cls.base_route, f"base_route cant be unset on {cls.__name__}"

    @classmethod
    def get(cls, api_client: NutanixApiClient, uuid: str) -> "BaseEntity":
        cls.__assert_base_route()
        entity_info = api_client.GET(f"/{cls.base_route}/{uuid}")
        return cls.get_from_info(api_client, entity_info)

    @classmethod
    @abstractmethod
    def get_from_info(cls, api_client: NutanixApiClient, info: Dict[str, Any]) -> "BaseEntity":
        pass

    @classmethod
    def list_entities(cls, api_client: NutanixApiClient, get_all: bool = True) -> List[Dict[str, Any]]:
        response = None
        entities = []
        offset = 0

        cls.__assert_base_route()
        while response is None or len(entities) < response["metadata"]["total_matches"]:
            response = api_client.POST(f"/{cls.base_route}/list", offset=offset)
            entities += response["entities"]
            offset = response["metadata"].get("length", 0)

            if not get_all or offset == 0:
                break

        return entities
