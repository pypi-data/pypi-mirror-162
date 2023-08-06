import warnings
from enum import Enum
from http import HTTPStatus
from typing import Any, Callable, Dict, Union

import requests
from requests import Session
from urllib3.exceptions import InsecureRequestWarning

from .exceptions import RequestError


class NutanixSession:
    def __init__(self, username: str, password: str, insecure: bool = True):
        session = requests.Session()
        session.auth = (username, password)
        session.verify = False
        session.headers.update({"Content-Type": "application/json; charset=utf-8"})
        self._session = session
        self._insecure = insecure

    def __enter__(self) -> Session:
        if self._insecure:
            warnings.simplefilter("ignore", InsecureRequestWarning)
        return self._session

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._insecure:
            warnings.simplefilter("default", InsecureRequestWarning)

        self._session.close()
        if exc_val:
            raise exc_val

        return self


class ApiVersion(Enum):
    V1 = "v1"
    V2 = "v2"
    V3 = "v3"


class NutanixApiClient:
    BASE_URL_FORMAT = "https://{address}:{port}"  # noqa FS003
    V1_URL_FORMAT = BASE_URL_FORMAT + "/PrismGateway/services/rest/v1/"
    V2_URL_FORMAT = BASE_URL_FORMAT + "/PrismGateway/services/rest/v2.0/"
    V3_URL_FORMAT = BASE_URL_FORMAT + "/api/nutanix/v3/"

    DEFAULT_REQUEST_TIMEOUT = 60

    def __init__(self, username: str, password: str, port: Union[str, int], address: str):
        self._username = username
        self._password = password
        self._port = int(port)
        self._endpoint = address

    def _get_base_url(self, api_version: ApiVersion):
        fmt = ""

        if api_version == ApiVersion.V1:
            fmt = self.V1_URL_FORMAT

        elif api_version == ApiVersion.V2:
            fmt = self.V2_URL_FORMAT

        if api_version == ApiVersion.V3:
            fmt = self.V3_URL_FORMAT

        return fmt.format(address=self._endpoint, port=self._port)

    @classmethod
    def _request(
        cls, url: str, method: Callable, body: Dict[str, Any] = None, offset: int = 0, timeout=DEFAULT_REQUEST_TIMEOUT
    ):
        if body is not None and offset != 0:
            body["offset"] = offset
        server_response = method(url, timeout=timeout) if body is None else method(url, json=body)

        if server_response.status_code == HTTPStatus.NOT_FOUND:
            raise RequestError(f"404 - Nothing matches the given URI {url}")

        if server_response.status_code != HTTPStatus.OK and server_response.status_code != HTTPStatus.ACCEPTED:
            raise RequestError(str((server_response.json())))

        return server_response.json()

    def GET(self, relative_url: str, api_version: ApiVersion = ApiVersion.V3) -> Union[Dict[str, Any], None]:  # noqa
        with NutanixSession(self._username, self._password) as session:
            return self._request(self._get_base_url(api_version) + relative_url, session.get)

    def POST(  # noqa
        self, relative_url: str, body: dict = None, offset: int = 0, api_version: ApiVersion = ApiVersion.V3
    ) -> Union[Dict[str, Any], None]:
        with NutanixSession(self._username, self._password) as session:
            return self._request(self._get_base_url(api_version) + relative_url, session.post, body or {}, offset)

    def PUT(  # noqa
        self, relative_url: str, body: dict = None, offset: int = 0, api_version: ApiVersion = ApiVersion.V3
    ) -> Union[Dict[str, Any], None]:
        with NutanixSession(self._username, self._password) as session:
            return self._request(self._get_base_url(api_version) + relative_url, session.put, body or {}, offset)
