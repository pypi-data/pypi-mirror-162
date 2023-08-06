from typing import List

from .api_client import NutanixApiClient
from .entity import Entity, Metadata, Spec, Status


class ImageStatus(Status):
    @property
    def size_bytes(self):
        return self.resources.get("size_bytes")


class ImageSpec(Spec):
    @property
    def source_uri(self) -> str:
        return self.resources.get("source_uri", "")

    @property
    def architecture(self) -> str:
        return self.resources.get("architecture")

    @property
    def image_type(self) -> str:
        return self.resources.get("image_type")

    @property
    def description(self) -> str:
        return self._spec.get("description")


class ImageMetadata(Metadata):
    pass


class NutanixImage(Entity):
    status: ImageStatus
    spec: ImageSpec
    metadata: ImageMetadata

    base_route = "images"

    def __init__(self, api_client: NutanixApiClient, **kwargs) -> None:
        super().__init__(
            api_client,
            ImageStatus(kwargs.get("status", {})),
            ImageSpec(kwargs.get("spec", {})),
            ImageMetadata(kwargs.get("metadata", {})),
        )

    @property
    def size_bytes(self):
        return self.status.size_bytes

    @property
    def source_uri(self) -> str:
        return self.spec.source_uri

    @property
    def architecture(self) -> str:
        return self.spec.architecture

    @property
    def image_type(self) -> str:
        return self.spec.image_type

    @property
    def description(self) -> str:
        return self.spec.description

    @classmethod
    def list_entities(cls, api_client: NutanixApiClient, get_all: bool = True) -> List["NutanixImage"]:
        return super().list_entities(api_client, get_all)
