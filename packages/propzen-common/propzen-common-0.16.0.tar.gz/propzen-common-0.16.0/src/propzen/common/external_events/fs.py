from uuid import UUID
from dataclasses import dataclass
from propzen.common.service_layer.externalbus import ExternalEvent


@dataclass
class ProfilePictureUploaded(ExternalEvent):
    account_id: UUID
    filename: str


@dataclass
class PropertyPictureUploaded(ExternalEvent):
    account_id: UUID
    property_id: UUID
    filename: str


@dataclass
class AssetAttachmentUploaded(ExternalEvent):
    account_id: UUID
    asset_id: UUID
    filename: str
    originalname: str
