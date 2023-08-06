from abc import ABC, abstractmethod
from typing import Any, Dict

import waiting

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

    @property
    def entity_version(self):
        return self._metadata.get("entity_version")

    def get_info(self) -> Dict[str, Any]:
        return {"metadata": self._metadata}


class Entity(ApiInfo, ABC):
    WAIT_INTERVAL = 3
    UPDATE_WAIT_TIMEOUT = 300

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

    @property
    def entity_version(self) -> str:
        return self.metadata.entity_version

    def get_info(self) -> Dict[str, Any]:
        return {**self._spec.get_info(), **self._metadata.get_info(), **self._status.get_info()}

    def get_info_for_update(self) -> Dict[str, Any]:
        return {**self._spec.get_info(), **self._metadata.get_info()}

    @classmethod
    def __assert_base_route(cls):
        assert cls.base_route, f"base_route cant be unset on {cls.__name__}"

    @classmethod
    def get(cls, api_client: NutanixApiClient, uuid: str) -> "Entity":
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

    def load(self, uuid: str) -> "Entity":
        vm = self.get(self._api_client, uuid)
        self._spec = vm.spec
        self._metadata = vm.metadata
        self._status = vm.status
        return self

    @classmethod
    def get_from_info(cls, api_client: NutanixApiClient, info: Dict[str, Any]) -> "Entity":
        return cls(
            api_client,
            status=info.get("status", {}),
            spec=info.get("spec", {}),
            metadata=info.get("metadata", {}),
        )

    def _wait_for_update(self, wait_interval: int, timeout: int):
        try:
            waiting.wait(
                lambda: self.get(self._api_client, self.uuid).entity_version > self.entity_version,
                timeout_seconds=timeout,
                sleep_seconds=wait_interval,
            )
        except waiting.exceptions.TimeoutExpired as e:
            raise TimeoutError(
                f"The timeout waiting for updating {self.__class__.__name__} " f"uuid={self.uuid} was expired"
            ) from e

    def update_entity(self, wait: bool = True, wait_interval: int = WAIT_INTERVAL, timeout: int = UPDATE_WAIT_TIMEOUT):
        body = self.get_info_for_update()
        result = self._api_client.PUT(f"/{self.base_route}/{self.uuid}", body=body)
        self._spec._spec = result["spec"]
        self._status._status = result["status"]
        self._metadata._metadata = result["metadata"]

        if wait:
            self._wait_for_update(wait_interval, timeout)

        return result
