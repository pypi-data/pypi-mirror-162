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
        self.__storage[self.__make_key(organization_id, content_hash)] = _MockStorageBlob(
            blob=blob,
            metadata={
                "content-type": content_type.value,
                "content-length": str(len(blob)),
                "date": datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT"),
                "url": f"gs://[MOCK_URL]/{content_hash.get_value()}"
            }
        )
        return content_hash

    def metadata(self, organization_id: OrganizationId, content_hash: Union[FileContentHash, str]) -> Dict[str, str]:
        try:
            metadata = self.__storage[self.__make_key(organization_id, content_hash)].metadata
        except KeyError:
            raise HTTPException(status_code=404)
        return {k.replace("_", "-"): v for k, v in metadata.items()}

    def get_creation_contexts(self, organization_id: OrganizationId, content_hash: Union[FileContentHash, str]) -> List[str]:
        metadata = self.metadata(organization_id, content_hash)
        return [k.replace("-", "_") for k in metadata.keys() if str(k).startswith("creation-context")]

    def uri_for(self, organization_id: OrganizationId, content_hash: Union[FileContentHash, str]) -> str:
        return self.__storage[self.__make_key(organization_id, content_hash)].metadata["url"]

    def update_metadata(self, organization_id: OrganizationId, content_hash: Union[FileContentHash, str], metadata: Dict[str, str]
                        ) -> Dict[str, str]:
        try:
            current_metadata = self.__storage[self.__make_key(organization_id, content_hash)].metadata
            patched_metadata = {**current_metadata, **metadata}
            self.__storage[self.__make_key(organization_id, content_hash)].metadata = patched_metadata
        except KeyError:
            raise HTTPException(status_code=404)
        return self.metadata(organization_id, content_hash)

    # only for integration testing
    def add_real_uri(self, organization_id: OrganizationId, content_hash: Union[FileContentHash, str], uri: str):
        try:
            self.__storage[self.__make_key(organization_id, content_hash)].metadata["url"] = uri
        except Exception:
            logging.warning(f"MockStorage contains no entry for organization {organization_id} "
                            f"and content hash {content_hash} - adding url anyway")
            self.__storage[self.__make_key(organization_id, content_hash)] = _MockStorageBlob(
                blob=None,
                metadata={"url": uri}
            )
