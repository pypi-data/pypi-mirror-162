from enum import Enum
from typing import Any, Dict, List

from .api_client import NutanixApiClient
from .entity import Entity, Metadata, Spec, Status


class SubnetType(Enum):
    OVERLAY = "OVERLAY"
    VLAN = "VLAN"


class SubnetMetadata(Metadata):
    def __init__(self, metadata: Dict[str, Any]) -> None:
        super().__init__(metadata)


class SubnetSpec(Spec):
    def __init__(self, spec: Dict[str, Any]) -> None:
        super().__init__(spec)

    @property
    def subnet_type(self) -> str:
        return self.resources.get("subnet_type")

    @property
    def ip_config(self) -> Dict[str, Any]:
        return self.resources.get("ip_config", {})

    @property
    def default_gateway_ip(self) -> str:
        return self.ip_config.get("default_gateway_ip")

    @property
    def dhcp_server_address(self) -> Dict[str, str]:
        return self.ip_config.get("dhcp_server_address")

    @property
    def pool_list(self) -> List[Dict[str, str]]:
        return self.ip_config.get("pool_list")

    @property
    def prefix_length(self) -> int:
        return self.ip_config.get("prefix_length")

    @property
    def vlan_id(self) -> int:
        return self.ip_config.get("vlan_id")

    @property
    def subnet_ip(self) -> str:
        return self.ip_config.get("subnet_ip")

    @property
    def dhcp_options(self) -> Dict[str, List[str]]:
        return self.ip_config.get("dhcp_options")


class SubnetStatus(Status):
    def __init__(self, status: Dict[str, Any]) -> None:
        super().__init__(status)


class NutanixSubnet(Entity):
    status: SubnetStatus
    spec: SubnetSpec
    metadata: SubnetMetadata

    base_route = "subnets"

    def __init__(self, api_client: NutanixApiClient, **kwargs) -> None:
        super().__init__(
            api_client,
            SubnetStatus(kwargs.get("status", {})),
            SubnetSpec(kwargs.get("spec", {})),
            SubnetMetadata(kwargs.get("metadata", {})),
        )

    @classmethod
    def list_entities(cls, api_client: NutanixApiClient, get_all: bool = True) -> List["NutanixSubnet"]:
        return super().list_entities(api_client, get_all)

    @property
    def subnet_type(self) -> str:
        return self.spec.subnet_type

    @property
    def ip_config(self) -> Dict[str, Any]:
        return self.spec.ip_config

    @property
    def default_gateway_ip(self) -> str:
        return self.spec.default_gateway_ip

    @property
    def dhcp_server_address(self) -> Dict[str, str]:
        return self.spec.dhcp_server_address

    @property
    def pool_list(self) -> List[Dict[str, str]]:
        return self.spec.pool_list

    @property
    def prefix_length(self) -> int:
        return self.spec.prefix_length

    @property
    def vlan_id(self) -> int:
        return self.spec.vlan_id

    @property
    def subnet_ip(self) -> str:
        return self.spec.subnet_ip

    @property
    def dhcp_options(self) -> Dict[str, List[str]]:
        return self.spec.dhcp_options
