import logging
import os
import shutil
from contextlib import ExitStack, contextmanager
from enum import Enum
from tempfile import TemporaryDirectory
from typing import Dict, Generator, List, Optional

import numpy as np
import pandas as pd

from opvia_scripts.firebase import (
    UploadedFile,
    cache_item_storage_location,
    temp_gcloud_file,
    upload_to_firebase,
)
from opvia_scripts.types.entity import ColumnEntity, TableEntity

_FILE_IDENTIFIER = "fileIdentifier"
_DOWNLOAD_URL = "downloadUrl"


@contextmanager
def download_tabular_files(
    files_column: pd.Series,
    logger: Optional[logging.Logger] = None,
) -> Generator[Dict[str, str], None, None]:
    """
    Context manager to download all files from a file column of a dataframe
    into a temporary directory, yielding a mapping of file identifier to the
    full path of the downloaded local file.

    Supports multi-file columns, where each record has a list of files.

    In the created directory, each file exists at the subdirectory
    corresponding to the file's file identifier. So for example, if the
    temporary directory is at ``/path/to/tempdir/`` and a downloaded file has
    the cloud location of ``/orgs/abcd1234/file.txt``, the downloaded file is
    at ``/path/to/tempdir/orgs/abcd1234/file.txt``.

    N.B. Pass in a series from a filtered dataframe to only download files you
    need.
    """

    with TemporaryDirectory() as temp_dir:
        with ExitStack() as stack:

            def download_file_from_json(file_identifier: str, download_url: str) -> str:
                if logger:
                    logger.info(f"Downloading {file_identifier!r}")
                downloaded_filename = stack.enter_context(
                    temp_gcloud_file(
                        file_identifier=file_identifier,
                        download_url=download_url,
                    )
                )
                target_filename = os.path.join(temp_dir, file_identifier)
                target_dir = os.path.dirname(target_filename)
                os.makedirs(target_dir, exist_ok=True)
                shutil.move(downloaded_filename, target_filename)

                return target_filename

            results = {}

            for i, cell in enumerate(files_column.array, start=1):
                if logger:
                    logger.info(f"Downloading files for cell {i}/{len(files_column)}")

                download_list: List[Dict[str, str]]
                if isinstance(cell, list):
                    download_list = cell
                elif isinstance(cell, dict):
                    download_list = [cell]
                elif cell is None or np.isnan(cell):
                    download_list = []
                else:
                    msg = f"Expecting each cell to be dict, list, or None/NaN, got {type(cell)}: {cell}"  # noqa: E501
                    raise TypeError(msg)

                for file_info in download_list:
                    downloaded_filename = download_file_from_json(
                        file_info[_FILE_IDENTIFIER],
                        file_info[_DOWNLOAD_URL],
                    )
                    results[file_info[_FILE_IDENTIFIER]] = downloaded_filename

            yield results


def put_cache_item(
    file_location: str,
    org_id: str,
    user_token: str,
    cache_directory: str,
    cache_item_name: str,
) -> UploadedFile:
    """
    Put a new item into a cache location. This can be accessed by other scripts
    or by cache item selects in custom cards etc.
    """
    storage_location = cache_item_storage_location(
        org_id=org_id,
        cache_dir=cache_directory,
        storage_basename=cache_item_name,
    )

    return upload_to_firebase(
        file_location=file_location,
        user_token=user_token,
        storage_location=storage_location,
    )


def altair_table_source(table: TableEntity) -> pd.DataFrame:
    """
    Create a data source that can be passed into an altair chart as a data
    source, with columns referenced by ID.
    """
    _table = table.copy(deep=True)
    if _table.records is None:
        _table.records = pd.DataFrame.from_dict(
            {role_name: [] for role_name in table.columns.keys()}
        )

    records = _table.records
    records.columns = [
        table.columns[column_name].column_id for column_name in records.columns
    ]

    return records


def altair_column_id(column: ColumnEntity) -> str:
    """
    Return the name of the column as it will be presented in the live dataset
    in the app
    """
    return column.column_id


class AltairDataTypes(str, Enum):
    """
    Data types in Altair
    """

    QUANTITATIVE = "QUANTITATIVE"
    ORDINAL = "ORDINAL"
    NOMINAL = "NOMINAL"
    TEMPORAL = "TEMPORAL"
    GEOJSON = "GEOJSON"


def altair_column_encoding(
    column: ColumnEntity,
    data_type: AltairDataTypes,
) -> str:
    """
    Encoding string for ordinal data from a column, with columns referenced by
    ID.
    """
    suffix = {
        AltairDataTypes.QUANTITATIVE: "Q",
        AltairDataTypes.ORDINAL: "O",
        AltairDataTypes.NOMINAL: "N",
        AltairDataTypes.TEMPORAL: "T",
        AltairDataTypes.GEOJSON: "G",
    }[data_type]

    return f"{altair_column_id(column=column)}:{suffix}"
