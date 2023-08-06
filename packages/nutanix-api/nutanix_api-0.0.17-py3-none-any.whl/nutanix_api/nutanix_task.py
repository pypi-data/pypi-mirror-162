from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Union

import waiting
from dateutil import parser

from .api_client import NutanixApiClient
from .base_entity import BaseEntity


class TaskStatus(Enum):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    ABORTED = "ABORTED"
    SUSPENDED = "SUSPENDED"
    FAILED = "FAILED"


class NutanixTask(BaseEntity):
    base_route = "tasks"

    def __init__(
        self,
        api_client: NutanixApiClient,
        uuid: str,
        status: str,
        entity_reference_list: List[Dict[str, Any]],
        start_time: str,
        creation_time: str,
        last_update_time: str,
        percentage_complete: int,
        progress_message: str,
        completion_time: str = None,
        **_,
    ) -> None:

        super().__init__(api_client)

        self._uuid: str = uuid
        self._status: TaskStatus = TaskStatus(status)
        self._progress_message: str = progress_message
        self._entity_reference: List[Dict[str, Any]] = entity_reference_list
        self._start_time: datetime = parser.parse(start_time)
        self._creation_time: datetime = parser.parse(creation_time)
        self._completion_time: datetime = parser.parse(completion_time) if completion_time else None
        self._last_update_time: datetime = parser.parse(last_update_time)
        self._percentage_complete: int = int(percentage_complete)

    @property
    def uuid(self) -> str:
        return self._uuid

    @property
    def status(self) -> TaskStatus:
        return self._status

    @property
    def progress_message(self) -> str:
        return self._progress_message

    @property
    def entity_reference(self) -> List[Dict[str, Any]]:
        return self._entity_reference

    @property
    def start_time(self) -> datetime:
        return self._start_time

    @property
    def creation_time(self) -> datetime:
        return self._creation_time

    @property
    def last_update_time(self) -> datetime:
        return self._last_update_time

    @property
    def completion_time(self) -> Union[datetime, None]:
        return self._completion_time

    @property
    def percentage_complete(self) -> int:
        return self._percentage_complete

    @classmethod
    def get(cls, api_client: NutanixApiClient, uuid: str) -> "NutanixTask":
        entity_info = api_client.GET(f"/tasks/{uuid}")
        return cls.get_from_info(api_client, entity_info)

    @classmethod
    def get_from_info(cls, api_client: NutanixApiClient, info: Dict[str, Any]) -> "NutanixTask":
        return cls(api_client, **info)

    @classmethod
    def list_entities(cls, api_client: NutanixApiClient, get_all: bool = True) -> List["NutanixTask"]:
        return super().list_entities(api_client, get_all)

    def wait_to_complete(self, wait_interval: int, timeout: int):
        try:
            waiting.wait(
                lambda: self.get(self._api_client, self._uuid).completion_time is not None,
                timeout_seconds=timeout,
                sleep_seconds=wait_interval,
                waiting_for=self._progress_message,
            )
        except waiting.exceptions.TimeoutExpired as e:
            raise TimeoutError(
                f"The timeout waiting for {' '.join(self._progress_message.split('_'))} task with "
                f"uuid={self._uuid} was expired"
            ) from e
