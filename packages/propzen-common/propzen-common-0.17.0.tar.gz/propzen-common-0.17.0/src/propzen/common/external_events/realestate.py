from uuid import UUID
from dataclasses import dataclass
from propzen.common.service_layer.externalbus import ExternalEvent


@dataclass
class AssetAttachmentRemoved(ExternalEvent):
    account_id: UUID
    asset_id: UUID
    file_id: UUID


@dataclass
class AssetImageRemoved(ExternalEvent):
    account_id: UUID
    asset_id: UUID
    file_id: UUID
