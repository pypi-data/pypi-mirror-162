from enum import Enum
from typing import Any, Dict, List, Union

from .api_client import ApiObject, NutanixApiClient


class PowerState(Enum):
    OFF = "OFF"
    ON = "ON"


class VMMetadata(ApiObject):
    def __init__(self, metadata: Dict[str, Any]) -> None:
        self._metadata = metadata

    @property
    def uuid(self) -> str:
        return self._metadata.get("uuid")

    def get_info(self) -> Dict[str, Any]:
        return {"metadata": self._metadata}


class VMSpec(ApiObject):
    def __init__(self, spec: Dict[str, Any]) -> None:
        self._spec = spec

    @property
    def cluster_reference(self) -> Dict[str, str]:
        return self._spec.get("cluster_reference", {})

    @property
    def cluster_reference_name(self) -> Dict[str, Any]:
        return self.cluster_reference.get("name", {})

    @property
    def resources(self) -> Dict[str, Any]:
        return self._spec.get("resources", {})

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

    @property
    def name(self) -> str:
        return self._spec.get("name", "")

    def get_info(self) -> Dict[str, Any]:
        return {"spec": self._spec}


class VMStatus(ApiObject):
    def __init__(self, status: Dict[str, Any]) -> None:
        self._status = status

    def get_info(self) -> Dict[str, Any]:
        return {"status": self._status}


class VirtualMachine(ApiObject):
    def __init__(self, api_client: NutanixApiClient, **kwargs) -> None:
        self.status: VMStatus = VMStatus(kwargs.get("status", {}))
        self.spec: VMSpec = VMSpec(kwargs.get("spec", {}))
        self.metadata: VMMetadata = VMMetadata(kwargs.get("metadata", {}))
        self._api_client = api_client

    def get_info(self) -> Dict[str, Any]:
        return {**self.spec.get_info(), **self.metadata.get_info(), **self.status.get_info()}

    @property
    def name(self) -> str:
        return self.spec.name

    @property
    def uuid(self) -> str:
        return self.metadata.uuid

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

    def load(self, uuid: str) -> "VirtualMachine":
        vm = self.get_vm(uuid)
        self.spec = vm.spec
        self.metadata = vm.metadata
        self.status = vm.status
        return self

    @classmethod
    def list_vms(cls, api_client: NutanixApiClient) -> List["VirtualMachine"]:
        return [VirtualMachine(api_client, **vm_info) for vm_info in api_client.POST("/vms/list")["entities"]]

    @classmethod
    def get_vm(cls, api_client: NutanixApiClient, uuid: str) -> "VirtualMachine":
        vm_info = api_client.GET(f"/vms/{uuid}")
        return VirtualMachine(api_client, **vm_info)

    @classmethod
    def set_vms_power_state(cls, api_client: NutanixApiClient, uuid: str, state: PowerState):
        vm = cls.get_vm(uuid)
        vm.power_state = state.value

        vm_info = vm.get_info()
        del vm_info["status"]
        return api_client.PUT(f"/vms/{uuid}", body=vm_info)
