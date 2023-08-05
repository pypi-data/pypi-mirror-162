import logging

from fastapi import HTTPException
from datetime import datetime
from typing import Union, List, Dict
from dataclasses import dataclass

from autoretouchlib.types import FileContentHash, OrganizationId, FileType


@dataclass
class _MockStorageBlob:
    blob: bytes
    metadata: Dict[str, str]


class MockStorage:
    def __init__(self):
        self.__storage: Dict[str, _MockStorageBlob] = {}
        self.__computed_metadata: Dict[str, Dict[str, str]] = {}

    @staticmethod
    def __make_key(organization_id: OrganizationId, content_hash: FileContentHash) -> str:
        if isinstance(content_hash, str):
            content_hash = FileContentHash(content_hash)
        return organization_id + "/origin/" + content_hash.get_value()

    def load(self, content_hash: Union[FileContentHash, str], organization_id: OrganizationId) -> bytes:
        try:
            return self.__storage[self.__make_key(organization_id, content_hash)].blob
        except KeyError:
            raise HTTPException(status_code=404)

    def store(self, blob: bytes, content_type: Union[FileType, str], organization_id: OrganizationId) \
            -> FileContentHash:
        if isinstance(content_type, str):
            content_type = FileType(content_type)
        content_hash = FileContentHash.from_bytes(blob)
        key = self.__make_key(organization_id, content_hash)
        self.__storage[key] = _MockStorageBlob(
            blob=blob,
            metadata=None
        )
        self.__computed_metadata[key] = {
            "content-type": content_type.value,
            "content-length": str(len(blob)),
            "date": datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT"),
            "url": f"gs://[MOCK_URL]/{content_hash.get_value()}"
        }
        return content_hash

    def metadata(self, organization_id: OrganizationId, content_hash: Union[FileContentHash, str]) -> Dict[str, str]:
        try:
            metadata = dict()
            key = self.__make_key(organization_id, content_hash)
            blob = self.__storage[key]
            if blob.metadata is not None:
                metadata.update({k.replace("_", "-"): v for k, v in blob.metadata.items()})
            metadata.update(self.__computed_metadata[key])
        except KeyError:
            raise HTTPException(status_code=404)
        return metadata

    def get_creation_contexts(self, organization_id: OrganizationId, content_hash: Union[FileContentHash, str]) -> List[
        str]:
        metadata = self.metadata(organization_id, content_hash)
        return [k.replace("-", "_") for k in metadata.keys() if str(k).startswith("creation-context")]

    def uri_for(self, organization_id: OrganizationId, content_hash: Union[FileContentHash, str]) -> str:
        return self.__computed_metadata[self.__make_key(organization_id, content_hash)]["url"]

    def update_metadata(self, organization_id: OrganizationId, content_hash: Union[FileContentHash, str],
                        metadata: Dict[str, str]
                        ) -> Dict[str, str]:
        key = self.__make_key(organization_id, content_hash)
        try:
            current_metadata = self.__storage[key].metadata
            if current_metadata is None:
                current_metadata = dict()
            patched_metadata = {**current_metadata, **metadata}
            self.__storage[key].metadata = patched_metadata
        except KeyError:
            raise HTTPException(status_code=404)
        return self.metadata(organization_id, content_hash)

    # only for integration testing
    def add_real_uri(self, organization_id: OrganizationId, content_hash: Union[FileContentHash, str], uri: str):
        key = self.__make_key(organization_id, content_hash)
        try:
            self.__computed_metadata[key]["url"] = uri
        except Exception:
            logging.warning(f"MockStorage contains no entry for organization {organization_id} "
                            f"and content hash {content_hash} - adding url anyway")
            self.__computed_metadata[key] = dict()
            self.__computed_metadata[key]["url"] = uri
