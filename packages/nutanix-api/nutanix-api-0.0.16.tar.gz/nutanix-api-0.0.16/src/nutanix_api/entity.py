from abc import ABC, abstractmethod
from typing import Any, Dict, List

from .api_client import NutanixApiClient
from .base_entity import BaseEntity
from .nutanix_task import NutanixTask


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


class Entity(BaseEntity, ApiInfo, ABC):
    WAIT_INTERVAL = 3
    UPDATE_WAIT_TIMEOUT = 300

    base_route = ""  # Need to override on each Inheriting class

    def __init__(self, api_client: NutanixApiClient, status: Status, spec: Spec, metadata: Metadata) -> None:
        super().__init__(api_client)
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
    def list_entities(cls, api_client: NutanixApiClient, get_all: bool = True) -> List["Entity"]:
        entities = super().list_entities(api_client, get_all)
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

    def update_entity(self, wait: bool = True, wait_interval: int = WAIT_INTERVAL, timeout: int = UPDATE_WAIT_TIMEOUT):
        body = self.get_info_for_update()
        result = self._api_client.PUT(f"/{self.base_route}/{self.uuid}", body=body)
        self._spec._spec = result["spec"]
        self._status._status = result["status"]
        self._metadata._metadata = result["metadata"]

        task = NutanixTask.get(self._api_client, result["status"].get("execution_context", {}).get("task_uuid"))
        if wait:
            task.wait_to_complete(wait_interval=wait_interval, timeout=timeout)

        return result
