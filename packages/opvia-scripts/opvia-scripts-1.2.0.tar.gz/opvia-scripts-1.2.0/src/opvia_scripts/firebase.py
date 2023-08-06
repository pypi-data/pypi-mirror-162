import os
from contextlib import contextmanager
from tempfile import TemporaryDirectory
from typing import Generator

import pyrebase
import requests
from pydantic import BaseModel
from pyrebase.pyrebase import Firebase

from opvia_scripts.constants import (
    FIREBASE_API_KEY,
    FIREBASE_AUTH_DOMAIN,
    FIREBASE_DATABASE_URL,
    FIREBASE_STORAGE_BUCKET,
)


def firebase() -> Firebase:
    config = {
        "apiKey": FIREBASE_API_KEY,
        "authDomain": FIREBASE_AUTH_DOMAIN,
        "databaseURL": FIREBASE_DATABASE_URL,
        "storageBucket": FIREBASE_STORAGE_BUCKET,
    }
    return pyrebase.initialize_app(config)


class UploadedFile(BaseModel):
    bucket: str
    path: str
    filename: str


def cache_item_storage_location(
    org_id: str,
    cache_dir: str,
    storage_basename: str,
) -> str:
    return f"org/{org_id}/servicesCache/{cache_dir}/{storage_basename}"


@contextmanager
def temp_gcloud_file(
    file_identifier: str,
    download_url: str,
) -> Generator[str, None, None]:
    """
    Download a file from google cloud, store it locally for the duration of the
    context, and yield the temporary filename to be consumed by scripts
    """
    basename = os.path.basename(file_identifier)

    # TODO: async here and up from here

    with TemporaryDirectory() as temp_dir:
        temp_filename = os.path.join(temp_dir, basename)
        with requests.get(download_url, stream=True) as result_stream:
            result_stream.raise_for_status()
            with open(temp_filename, "wb") as f:
                for chunk in result_stream.iter_content(chunk_size=8192):
                    f.write(chunk)

        yield temp_filename


def upload_to_firebase(
    file_location: str,
    user_token: str,
    storage_location: str,
) -> UploadedFile:
    """
    Upload a file to firebase and return the file identifier
    """
    basename = os.path.basename(file_location)

    storage = firebase().storage()
    target = storage.child(storage_location)
    target.put(file_location, token=user_token)

    bucket = target.storage_bucket.split("/")[-1]

    return UploadedFile(
        path=storage_location,
        filename=basename,
        bucket=bucket,
    )
