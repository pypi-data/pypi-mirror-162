from enum import Enum
from typing import Any, Dict, List, Union

from .api_client import ApiVersion, NutanixApiClient
from .api_object import Metadata, Spec, Status, V3ApiObject


class PowerState(Enum):
    OFF = "OFF"
    ON = "ON"


class VMMetadata(Metadata):
    def __init__(self, metadata: Dict[str, Any]) -> None:
        super().__init__(metadata)


class VMSpec(Spec):
    def __init__(self, spec: Dict[str, Any]) -> None:
        super().__init__(spec)

    @property
    def cluster_reference(self) -> Dict[str, str]:
        return self._spec.get("cluster_reference", {})

    @property
    def cluster_reference_name(self) -> Dict[str, Any]:
        return self.cluster_reference.get("name", {})

    @property
    def nic_list(self) -> List[Dict[str, Any]]:
        return self.resources.get("nic_list", [])

    @property
    def ip_endpoint_list(self) -> List[str]:
        """Return list of vm ips as they described in the VM spec"""

        ips = list()
        for nic in self.nic_list:
            for ip_endpoint_list in nic.get("ip_endpoint_list", []):
                if ip := ip_endpoint_list.get("ip"):
                    ips.append(ip)
        return ips

    @property
    def mac_addresses(self) -> List[str]:
        """Return list of vm MAC addresses as they described in the VM spec"""

        return [nic.get("mac_address") for nic in self.nic_list if nic.get("mac_address")]

    @property
    def vcpus_per_socket(self) -> Union[int, None]:
        return self.resources.get("num_vcpus_per_socket")

    @property
    def sockets(self) -> Union[int, None]:
        return self.resources.get("num_sockets")

    @property
    def memory_size_mib(self) -> Union[int, None]:
        return self.resources.get("memory_size_mib")

    @property
    def boot_config(self) -> Dict[str, Any]:
        return self.resources.get("boot_config")

    @property
    def power_state(self) -> str:
        return self.resources.get("power_state")

    @power_state.setter
    def power_state(self, power_state: PowerState):
        self.resources["power_state"] = power_state.value

    @property
    def disk_list(self) -> List[Dict[str, Any]]:
        return self.resources.get("disk_list")


class VMStatus(Status):
    def __init__(self, status: Dict[str, Any]) -> None:
        super().__init__(status)


class NutanixVMLabel:
    def __init__(self, **entity_info) -> None:
        self._uuid = entity_info.get("uuid")
        self._name = entity_info.get("name")
        self._description = entity_info.get("description")
        self._entity_type = entity_info.get("entityType")
        self._create_timestamp = entity_info.get("createTimestampUSecs")
        self._last_modified_timestamp = entity_info.get("lastModifiedTimestampUSecs")

    @property
    def uuid(self):
        return self._uuid

    @property
    def name(self):
        return self._name

    @property
    def description(self):
        return self._description

    @property
    def entity_type(self):
        return self._entity_type

    @property
    def create_timestamp(self):
        return self._create_timestamp

    @property
    def last_modified_timestamp(self):
        return self._last_modified_timestamp

    @classmethod
    def get(cls, api_client: NutanixApiClient, name: str) -> "NutanixVMLabel":
        response = api_client.GET("tags", api_version=ApiVersion.V1)
        return NutanixVMLabel(**next(label for label in response.get("entities", []) if label["name"] == name))

    @classmethod
    def create(cls, api_client: NutanixApiClient, name: str) -> "NutanixVMLabel":
        response = api_client.POST("tags", api_version=ApiVersion.V1, body={"name": name, "entityType": "vm"})
        return NutanixVMLabel(**response)


class NutanixVM(V3ApiObject):
    status: VMStatus
    spec: VMSpec
    metadata: VMMetadata

    base_route = "vms"

    def __init__(self, api_client: NutanixApiClient, **kwargs) -> None:
        super().__init__(
            api_client,
            VMStatus(kwargs.get("status", {})),
            VMSpec(kwargs.get("spec", {})),
            VMMetadata(kwargs.get("metadata", {})),
        )

    @property
    def power_state(self) -> str:
        return self.spec.power_state

    @power_state.setter
    def power_state(self, power_state: PowerState):
        self.spec.power_state = power_state

    @property
    def mac_addresses(self) -> List[str]:
        return self.spec.mac_addresses

    @property
    def ip_addresses(self) -> List[str]:
        return self.spec.ip_endpoint_list

    @property
    def num_sockets(self) -> int:
        return self.spec.sockets

    @classmethod
    def set_vms_power_state(cls, api_client: NutanixApiClient, uuid: str, state: PowerState):
        vm = cls.get(api_client, uuid)
        vm.power_state = state
        vm_info = vm.get_info()

        del vm_info["status"]
        return api_client.PUT(f"/{cls.base_route}/{uuid}", body=vm_info)

    def power_off(self):
        return self.set_vms_power_state(self._api_client, self.uuid, PowerState.OFF)

    def power_on(self):
        return self.set_vms_power_state(self._api_client, self.uuid, PowerState.ON)

    def reboot(self):
        return self._api_client.POST(f"/{self.base_route}/{self.uuid}/acpi_reboot")
