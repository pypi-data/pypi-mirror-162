__all__ = [
    'CreateProviderOptionData', 'CreateProviderOptionSchema',
    'UpdateProviderOptionData', 'UpdateProviderOptionSchema',
    'ProviderData', 'ProviderSchema', 'ProviderListData', 'ProviderListSchema',
    'ProviderCredentialData', 'ProviderCredentialSchema',
    'CreateDocumentOptionData', 'CreateDocumentOptionSchema',
    'UpdateDocumentOptionData', 'UpdateDocumentOptionSchema',
    'DocumentOptionUploadData',
    'DocumentData', 'DocumentSchema'
]

import datetime
from dataclasses import dataclass, field
from typing import Optional, List

import marshmallow_dataclass

from .users import UserData


@dataclass
class WebDavCredentials:
    server: str = field()
    username: str = field()
    password: str = field()


@dataclass
class CreateProviderOptionData:
    name: str = field()
    type: str = field()
    credentials: WebDavCredentials = field()

    public: Optional[bool] = field()


@dataclass
class UpdateProviderOptionData:
    name: Optional[str] = field()
    type: Optional[str] = field()
    credentials: Optional[WebDavCredentials] = field()

    public: Optional[bool] = field()


@dataclass
class ProviderData:
    id: int = field()
    name: str = field()
    type: str = field()


@dataclass
class ProviderListData:
    length: int = field()
    page: int = field()
    pages: int = field()
    items: List[ProviderData] = field(default_factory=list)


@dataclass
class ProviderCredentialData:
    id: str = field()
    name: str = field()
    type: str = field()
    salt: str = field()
    credentials: str = field()


@dataclass
class DocumentOptionUploadData:
    base64: str = field()


@dataclass
class CreateDocumentOptionData:
    name: str = field()
    path: str = field()

    on_created: Optional[datetime.datetime] = field()
    on_updated: Optional[datetime.datetime] = field()

    upload_data: Optional[DocumentOptionUploadData] = field()


@dataclass
class UpdateDocumentOptionData:
    name: Optional[str] = field()

    on_created: Optional[datetime.datetime] = field()
    on_updated: Optional[datetime.datetime] = field()

    upload_data: Optional[DocumentOptionUploadData] = field()


@dataclass
class DocumentData:
    id: str = field()
    name: str = field()

    owner: Optional[UserData] = field()


CreateProviderOptionSchema = marshmallow_dataclass.class_schema(CreateProviderOptionData)()
UpdateProviderOptionSchema = marshmallow_dataclass.class_schema(UpdateProviderOptionData)()
ProviderSchema = marshmallow_dataclass.class_schema(ProviderData)()
ProviderListSchema = marshmallow_dataclass.class_schema(ProviderListData)()
ProviderCredentialSchema = marshmallow_dataclass.class_schema(ProviderCredentialData)()

CreateDocumentOptionSchema = marshmallow_dataclass.class_schema(CreateDocumentOptionData)()
UpdateDocumentOptionSchema = marshmallow_dataclass.class_schema(UpdateDocumentOptionData)()
DocumentSchema = marshmallow_dataclass.class_schema(DocumentData)()
