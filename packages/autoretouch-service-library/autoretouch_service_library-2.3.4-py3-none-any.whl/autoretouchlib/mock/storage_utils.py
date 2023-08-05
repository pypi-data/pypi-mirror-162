from pathlib import Path
from typing import Union, Tuple, Optional

from autoretouchlib.types import FileType, OrganizationId
from autoretouchlib.storage_v2 import Storage
from autoretouchlib.mock.storage import MockStorage


def store_image_for_ai_platform(
        image_path: Union[Path, str], storage: Storage, mock_storage: Optional[MockStorage] = None,
        organization_id: OrganizationId = OrganizationId("00000000-0000-0000-0000-000000000000")
) -> Tuple[str, str]:
    """
    Store an image file in real storage, get the actual uri for the AI platform request for integration testing,
    and optionally set up a mock storage instance.
    :returns: content hash as string referring to the image, absolute uri as string
    """
    file_type = FileType.from_filename(image_path)
    with open(image_path, "rb") as image_file:
        blob = image_file.read()
        image_content_hash = storage.store(blob, file_type, organization_id)
        if mock_storage:
            mock_storage.store(blob, file_type, organization_id)
    uri = storage.uri_for(organization_id, image_content_hash)
    if mock_storage:
        mock_storage.add_real_uri(organization_id, image_content_hash, uri)
    return image_content_hash.get_value(), uri
