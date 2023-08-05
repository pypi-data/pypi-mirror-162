import logging
import os
from typing import Union, Dict, List

from fastapi import HTTPException
from google.api_core.exceptions import NotFound
from google.cloud import storage as google_cloud_storage
from google.cloud.exceptions import GoogleCloudError

from autoretouchlib.types import FileContentHash, OrganizationId, FileType


def blob_path(organization_id, content_hash) -> str:
    return f"{organization_id}/origin/{content_hash.get_value()}"


class Storage:

    def __init__(self):
        bucket_name = os.getenv("IMAGES_BUCKET")
        project = os.getenv("GOOGLE_PROJECT")
        self.storage_client = google_cloud_storage.Client(project=project)
        self.bucket = self.storage_client.bucket(bucket_name, project)

    def load(self, content_hash: Union[FileContentHash, str], organization_id: OrganizationId
             ) -> bytes:
        if isinstance(content_hash, str):
            content_hash = FileContentHash(content_hash)
        blob = self.bucket.blob(blob_path(organization_id, content_hash))
        if not blob.exists():
            raise HTTPException(status_code=404)
        return blob.download_as_bytes()

    def store(self, blob: bytes, content_type: Union[FileType, str], organization_id: OrganizationId
              ) -> FileContentHash:
        if isinstance(content_type, str):
            content_type = FileType(content_type)
        content_hash = FileContentHash.from_bytes(blob)
        bucket_blob = self.bucket.blob(blob_path(organization_id, content_hash))
        if not bucket_blob.exists():
            try:
                bucket_blob.upload_from_string(data=blob, content_type=content_type.value)
            except GoogleCloudError as e:
                logging.error(
                    f"GoogleCloudError in storing {content_hash.get_value()} for organization {organization_id}: " + e)
                # bucket_blob.delete()
                raise e
        return content_hash

    def metadata(self, organization_id: OrganizationId, content_hash: Union[FileContentHash, str]) -> Dict[str, str]:
        metadata = dict()
        if isinstance(content_hash, str):
            content_hash = FileContentHash(content_hash)
        blob = self.bucket.get_blob(blob_path(organization_id, content_hash))
        if not blob.exists():
            raise HTTPException(status_code=404)
        if blob.metadata is not None:
            for key in blob.metadata.keys():
                metadata.update({key.replace("_", "-"): blob.metadata[key]})
        metadata.update({"content-type": blob.content_type})
        metadata.update({"url": f"gs://{self.bucket.name}/{blob_path(organization_id, content_hash)}"})
        metadata.update({"content-length": f"{blob.size}"})
        return metadata

    def get_creation_contexts(self, organization_id: OrganizationId, content_hash: Union[FileContentHash, str]) -> List[
        str]:
        metadata = self.metadata(organization_id, content_hash)
        return [k.replace("-", "_") for k in metadata.keys() if str(k).startswith("creation-context")]

    def uri_for(self, organization_id: OrganizationId, content_hash: Union[FileContentHash, str]) -> str:
        return self.metadata(organization_id, content_hash)["url"]

    def update_metadata(self, organization_id: OrganizationId, content_hash: Union[FileContentHash, str],
                        metadata: Dict[str, str]
                        ) -> Dict[str, str]:
        if isinstance(content_hash, str):
            content_hash = FileContentHash(content_hash)
        blob = self.bucket.get_blob(blob_path(organization_id, content_hash))
        if not blob.exists():
            raise HTTPException(status_code=404)
        blob.metadata = metadata
        try:
            blob.patch()
        except GoogleCloudError as e:
            logging.error(
                f"GoogleCloudError in patching {content_hash.get_value()} for organization {organization_id}: " + e)
            raise e
        metadata = dict()
        for k in blob.metadata.keys():
            metadata[k.replace("_", "-")] = blob.metadata[k]
        return metadata


storage = Storage()
