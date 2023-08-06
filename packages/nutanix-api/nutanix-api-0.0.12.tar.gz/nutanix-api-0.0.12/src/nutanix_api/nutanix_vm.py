from enum import Enum
from typing import Any, Dict, List, Union

from .api_client import NutanixApiClient
from .api_object import ApiObject, Metadata, Spec, Status


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


class NutanixVM(ApiObject):
    status: VMStatus
    spec: VMSpec
    metadata: VMMetadata

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
    def list_vms(cls, api_client: NutanixApiClient, get_all: bool = True) -> List["NutanixVM"]:
        return cls.list_entities(api_client, "vms", get_all)

    @classmethod
    def get(cls, api_client: NutanixApiClient, uuid: str) -> "NutanixVM":
        vm_info = api_client.GET(f"/vms/{uuid}")
        return cls.get_from_info(api_client, vm_info)

    @classmethod
    def set_vms_power_state(cls, api_client: NutanixApiClient, uuid: str, state: PowerState):
        vm = cls.get(api_client, uuid)
        vm.power_state = state

        vm_info = vm.get_info()
        del vm_info["status"]
        return api_client.PUT(f"/vms/{uuid}", body=vm_info)

    def power_off(self):
        return self.set_vms_power_state(self._api_client, self.uuid, PowerState.OFF)

    def power_on(self):
        return self.set_vms_power_state(self._api_client, self.uuid, PowerState.ON)

    def reboot(self):
        return self._api_client.POST(f"/vms/{self.uuid}/acpi_reboot")
