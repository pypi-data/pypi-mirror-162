from typing import Any, Dict, List

from .api_client import NutanixApiClient
from .api_object import ApiObject, Metadata, Spec, Status


class ClusterStatus(Status):
    pass


class ClusterSpec(Spec):
    @property
    def network(self) -> Dict[str, Any]:
        return self.resources.get("network", {})

    @property
    def external_ip(self) -> str:
        return self.network.get("external_ip", "")

    @property
    def external_subnet(self) -> str:
        return self.network.get("external_subnet", "")

    @property
    def external_data_services_ip(self) -> str:
        return self.network.get("external_data_services_ip", "")

    @property
    def name_server_ip_list(self) -> List[str]:
        return self.network.get("name_server_ip_list", [])

    @property
    def internal_subnet(self) -> str:
        return self.network.get("internal_subnet", str)


class ClusterMetadata(Metadata):
    pass


class NutanixCluster(ApiObject):
    status: ClusterStatus
    spec: ClusterSpec
    metadata: ClusterMetadata

    def __init__(self, api_client: NutanixApiClient, **kwargs) -> None:
        super().__init__(
            api_client,
            ClusterStatus(kwargs.get("status", {})),
            ClusterSpec(kwargs.get("spec", {})),
            ClusterMetadata(kwargs.get("metadata", {})),
        )

    @property
    def external_ip(self) -> str:
        return self.spec.external_ip

    @property
    def external_subnet(self) -> str:
        return self.spec.external_subnet

    @property
    def external_data_services_ip(self) -> str:
        return self.spec.external_data_services_ip

    @property
    def name_server_ip_list(self) -> List[str]:
        return self.spec.name_server_ip_list

    @property
    def internal_subnet(self) -> str:
        return self.spec.internal_subnet

    @classmethod
    def get(cls, api_client: NutanixApiClient, uuid: str) -> "NutanixCluster":
        cluster_info = api_client.GET(f"/clusters/{uuid}")
        return cls.get_from_info(api_client, cluster_info)

    @classmethod
    def list_clusters(cls, api_client: NutanixApiClient, get_all: bool = True) -> List["NutanixCluster"]:
        return cls.list_entities(api_client, "clusters", get_all)
