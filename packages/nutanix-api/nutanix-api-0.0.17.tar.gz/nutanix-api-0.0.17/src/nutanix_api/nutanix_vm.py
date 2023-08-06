from enum import Enum
from typing import Any, Dict, List, Union

from .api_client import ApiVersion, NutanixApiClient
from .entity import Entity, Metadata, Spec, Status


class PowerState(Enum):
    OFF = "OFF"
    ON = "ON"


class VMMetadata(Metadata):
    def __init__(self, metadata: Dict[str, Any]) -> None:
        super().__init__(metadata)


class VMBootDevices(Enum):
    CDROM = "CDROM"
    DISK = "DISK"
    NETWORK = "NETWORK"

    @classmethod
    def default_boot_order(cls) -> List["VMBootDevices"]:
        return [VMBootDevices.CDROM, VMBootDevices.DISK, VMBootDevices.NETWORK]


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
    def boot_device_order(self) -> List[str]:
        return self.boot_config.get("boot_device_order_list")

    @boot_device_order.setter
    def boot_device_order(self, boot_devices: List[VMBootDevices]):
        self.boot_config["boot_device_order_list"] = [device.value for device in boot_devices]

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


class NutanixVM(Entity):
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

    @classmethod
    def list_entities(cls, api_client: NutanixApiClient, get_all: bool = True) -> List["NutanixVM"]:
        return super().list_entities(api_client, get_all)

    @property
    def num_sockets(self) -> int:
        return self.spec.sockets

    def power_off(self, wait: bool = True, timeout: int = Entity.UPDATE_WAIT_TIMEOUT):
        self.load(self.uuid)
        self.spec.power_state = PowerState.OFF
        return self.update_entity(wait, timeout=timeout)

    def power_on(self, wait: bool = True, timeout: int = Entity.UPDATE_WAIT_TIMEOUT):
        self.load(self.uuid)
        self.spec.power_state = PowerState.ON
        return self.update_entity(wait, timeout=timeout)

    def reboot(self):
        return self._api_client.POST(f"/{self.base_route}/{self.uuid}/acpi_reboot")

    def update_boot_order(
        self,
        vm_boot_devices: List[VMBootDevices],
        wait: bool = True,
        timeout: int = Entity.UPDATE_WAIT_TIMEOUT,
    ):
        self.spec.boot_device_order = vm_boot_devices
        return self.update_entity(wait, timeout=timeout)
