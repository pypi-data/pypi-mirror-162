from __future__ import annotations

from enum import Enum
from typing import Dict, List, Literal, Optional, Type

import pandas as pd
from altair import TopLevelMixin
from pydantic import BaseModel, Field

from opvia_scripts.exceptions import MalformedObject
from opvia_scripts.types.entity import TableEntity


class ResultKind(str, Enum):
    #: Add new records to a table
    NEW_RECORDS = "NEW_RECORDS"

    #: Add a new upload or image card
    NEW_UPLOAD = "NEW_UPLOAD"

    #: Add a new page to a collection
    NEW_COLLECTION_PAGE = "NEW_COLLECTION_PAGE"

    #: Add a new Vega chart to a page
    NEW_VEGA_CHART = "NEW_VEGA_CHART"


class ScriptResult(BaseModel):
    """
    A single instruction to send back to the Opvia app
    """

    class Config:
        arbitrary_types_allowed = True
        extra = "forbid"

    kind: ResultKind


class NewRecords(ScriptResult):
    """
    New records to add to an Opvia table and present in the app as a table
    records card.

    The content of the records can be numbers or text for simple value types,
    such as text cells, number cells, date cells (using ISO dates), and link
    cells. They can also be instances of ``ScriptResult`` for complex cell
    types such as file and image cells.
    """

    kind: Literal[ResultKind.NEW_RECORDS] = Field(
        ResultKind.NEW_RECORDS,
        title="kind",
        description=(
            "A literal 'NEW_RECORDS' value to enable discrimination in the JSON "
            "parser. It's not generally necessary to use this value."
        ),
    )

    #: ID of the table to add records to
    table_role: str = Field(
        ...,
        title="Table Role",
        description="Role name of the table to add records to.",
    )

    #: Pandas DataFrame containing new records to add to the Opvia table.
    #: The column names of the DataFrame should be the table's column role
    #: names. Opvia will automatically convert these into column IDs and
    #: add the records to the table.
    records: pd.DataFrame


class UploadKind(str, Enum):
    """
    The kind of a new upload
    """

    #: An image upload
    image = "image"

    #: A file upload
    file = "file"


class NewUpload(ScriptResult):
    """
    Upload a new file to Opvia and present it in the app as a new file or image
    card.
    """

    kind: Literal[ResultKind.NEW_UPLOAD] = Field(
        ResultKind.NEW_UPLOAD,
        title="kind",
        description=(
            "A literal 'NEW_UPLOAD' value to enable discrimination in the JSON "
            "parser. It's not generally necessary to use this value."
        ),
    )

    file_location: str = Field(
        ...,
        title="File Location",
        description=(
            "Location of the file in local storage. This will be automatically "
            "uploaded to Opvia for you."
        ),
    )

    upload_kind: UploadKind = Field(
        ...,
        title="Upload Kind",
        description=(
            "Either 'image' to present the result as a new image card, or "
            "'file' to present it as a new uploads card."
        ),
    )

    #: Caption of the upload
    caption: Optional[str] = Field(
        default=None,
        title="Caption",
        description="Optional caption to display under the new upload.",
    )


class NewCollectionPage(ScriptResult):
    """
    Indicates that the script should create a new entry in a collection.

    The ``record`` populates the record information in the collection, and the
    ``cards`` create cards within the new collection page.

    This is generally used for automatic data ingestion scripts.
    """

    kind: Literal[ResultKind.NEW_COLLECTION_PAGE] = Field(
        ResultKind.NEW_COLLECTION_PAGE,
        title="kind",
        description=(
            "A literal 'NEW_COLLECTION_PAGE' value to enable discrimination in the "
            "JSON parser. It's not generally necessary to use this value."
        ),
    )

    collection_role: str = Field(
        ...,
        title="Collection Role",
        description="Role name of the collection to add a page to.",
    )

    #: Pandas DataFrame containing a single new record to add to the Opvia
    #: table.
    #: The column names of the DataFrame should be the table's column role
    #: names. Opvia will automatically convert these into column IDs and
    #: add the records to the table.
    record: pd.DataFrame

    #: New cards to add to the new collection page.
    cards: List[ScriptResult]


class NewVegaChart(ScriptResult):
    """
    (WORK IN PROGRESS) Add a new Vega chart card to the app.

    Note that the Altair data sources for any live tables must be created using
    ``altair_table_source``, ``altair_column_id``, and
    ``altair_column_encoding``.
    """

    kind: Literal[ResultKind.NEW_VEGA_CHART] = Field(
        ResultKind.NEW_VEGA_CHART,
        title="kind",
        description=(
            "A literal 'NEW_VEGA_CHART' value to enable discrimination in the "
            "JSON parser. It's not generally necessary to use this value."
        ),
    )

    #: Altair chart to return to the app as an in-app visualization
    chart: TopLevelMixin

    #: List of ``TableEntity`` that should be treated as live. The app will
    #: use the latest data to form the visualization, rather than the snapshot
    #: of data set to this script. Note that the Altair data sources for these
    #: tables must be created using ``altair_table_source``,
    #: ``altair_column_id``, and ``altair_column_encoding``.
    live_datasets: List[TableEntity]


# ---- Discriminator

_SCRIPT_RESULT: Dict[ResultKind, Type[ScriptResult]] = {
    ResultKind.NEW_RECORDS: NewRecords,
    ResultKind.NEW_UPLOAD: NewUpload,
    ResultKind.NEW_COLLECTION_PAGE: NewCollectionPage,
    ResultKind.NEW_VEGA_CHART: NewVegaChart,
}


class AnyScriptResult(BaseModel):
    """
    Any result returned by a script
    """

    # See https://github.com/samuelcolvin/pydantic/issues/619#issuecomment-713508861
    @classmethod
    def __get_validators__(cls):
        yield cls.return_valid

    @classmethod
    def return_valid(cls, values):
        try:
            kind = values["kind"]
        except KeyError as e:
            raise MalformedObject(
                f"Missing required 'kind' field for result: {values}"
            ) from e
        try:
            return _SCRIPT_RESULT[kind](**values)
        except KeyError as e:
            raise MalformedObject(f"Unsupported kind: {kind}") from e
