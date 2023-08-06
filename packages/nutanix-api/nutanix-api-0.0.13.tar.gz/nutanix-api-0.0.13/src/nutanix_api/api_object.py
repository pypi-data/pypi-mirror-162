from abc import ABC, abstractmethod
from typing import Any, Dict

from .api_client import NutanixApiClient


class ApiInfo(ABC):
    @abstractmethod
    def get_info(self) -> Dict[str, Any]:
        pass


class Status(ApiInfo):
    def __init__(self, status: Dict[str, Any]) -> None:
        self._status = status

    @property
    def resources(self) -> Dict[str, Any]:
        return self._status.get("resources", {})

    def get_info(self) -> Dict[str, Any]:
        return {"status": self._status}


class Spec(ApiInfo):
    def __init__(self, spec: Dict[str, Any]) -> None:
        self._spec = spec

    @property
    def name(self) -> str:
        return self._spec.get("name", "")

    def get_info(self) -> Dict[str, Any]:
        return {"spec": self._spec}

    @property
    def resources(self) -> Dict[str, Any]:
        return self._spec.get("resources", {})


class Metadata(ApiInfo):
    def __init__(self, metadata: Dict[str, Any]) -> None:
        self._metadata = metadata

    @property
    def uuid(self) -> str:
        return self._metadata.get("uuid")

    def get_info(self) -> Dict[str, Any]:
        return {"metadata": self._metadata}


class V3ApiObject(ABC):
    base_route = ""  # Need to override on each Inheriting class

    def __init__(self, api_client: NutanixApiClient, status: Status, spec: Spec, metadata: Metadata) -> None:
        self._api_client = api_client
        self._status: Status = status
        self._spec: Spec = spec
        self._metadata: Metadata = metadata

    @property
    def status(self) -> Status:
        return self._status

    @property
    def spec(self) -> Spec:
        return self._spec

    @property
    def metadata(self) -> Metadata:
        return self._metadata

    @property
    def name(self) -> str:
        return self.spec.name

    @property
    def uuid(self) -> str:
        return self.metadata.uuid

    def get_info(self) -> Dict[str, Any]:
        return {**self._spec.get_info(), **self._metadata.get_info(), **self._status.get_info()}

    @classmethod
    def __assert_base_route(cls):
        assert cls.base_route, f"base_route cant be unset on {cls.__name__}"

    @classmethod
    def get(cls, api_client: NutanixApiClient, uuid: str) -> "V3ApiObject":
        cls.__assert_base_route()
        vm_info = api_client.GET(f"/{cls.base_route}/{uuid}")
        return cls.get_from_info(api_client, vm_info)

    @classmethod
    def list_entities(cls, api_client: NutanixApiClient, get_all: bool = True):
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

        return [cls.get_from_info(api_client, info) for info in entities]

    def load(self, uuid: str) -> "V3ApiObject":
        vm = self.get(self._api_client, uuid)
        self._spec = vm.spec
        self._metadata = vm.metadata
        self._status = vm.status
        return self

    @classmethod
    def get_from_info(cls, api_client: NutanixApiClient, info: Dict[str, Any]) -> "V3ApiObject":
        return cls(
            api_client,
            status=info.get("status", {}),
            spec=info.get("spec", {}),
            metadata=info.get("metadata", {}),
        )
