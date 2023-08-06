from __future__ import annotations

from abc import ABC
from enum import Enum
from typing import Any, Dict, List, Literal, Optional

import pandas as pd
from fastapi_camelcase import CamelModel
from pydantic import Field
from pydantic.class_validators import validator

from opvia_scripts.exceptions import MalformedObject


class EntityKind(str, Enum):
    #: Context
    CONTEXT = "_OPVIA_CONTEXT"

    #: Table
    TABLE = "TABLE"

    #: Static table selection by ID
    TABLE_BY_ID = "TABLE_BY_ID"

    #: Column
    COLUMN = "COLUMN"

    #: A file uploaded to Firebase
    UPLOAD = "UPLOAD"

    #: A Select
    SELECT = "SELECT"

    #: Text
    TEXT = "TEXT"

    #: A file in a cache subdirectory
    CACHE_ITEM = "CACHE_ITEM"

    #: A checkbox
    CHECKBOX = "CHECKBOX"


# -- Entities


class Entity(CamelModel, ABC):
    """
    Contains values that a user has entered into the form fields. See each
    subclass for how to access the data from each field.
    """

    class Config:
        extra = "forbid"

    #: Kind this entity corresponds to
    kind: EntityKind


class ColumnEntity(Entity):
    """
    Definition of a column within an Opvia table.
    Generally used as part of a TableEntity.
    """

    kind: Literal[EntityKind.COLUMN] = Field(
        EntityKind.COLUMN,
        title="kind",
        description=(
            "A literal 'COLUMN' value to enable discrimination in the JSON "
            "parser. It's not generally necessary to use this value."
        ),
    )

    #: Column ID
    column_id: str = Field(
        ...,
        title="Column ID",
        description="The internal ID of the column in Opvia",
    )


class RecordsScope(str, Enum):
    """
    The scope of records supplied with the table entity, if any
    """

    #: Just a page's records
    PAGE = "PAGE"

    #: All records
    ALL = "ALL"


class TableEntity(Entity):
    """
    Definition of an Opvia table, including ID, column info, and any records
    sent from the app.
    """

    class Config:
        arbitrary_types_allowed = True

    kind: Literal[EntityKind.TABLE] = Field(
        EntityKind.TABLE,
        title="kind",
        description=(
            "A literal 'TABLE' value to enable discrimination in the JSON "
            "parser. It's not generally necessary to use this value."
        ),
    )

    #: Table ID
    table_id: str = Field(
        ...,
        title="Table ID",
        description="ID of the table in Opvia",
    )

    #: Optional view ID
    view_id: Optional[str] = Field(
        None, title="View ID", description="Optional view ID"
    )

    #: Any column entities specified in the role definition.
    columns: Dict[str, ColumnEntity] = Field(
        ...,
        title="Columns",
        description=(
            "A dictionary whose keys are the column role names defined in the table's "
            "specification, and whose values are ``ColumnEntity`` instances "
            "defining how the user mapped up Opvia columns to column roles. "
            "Primarily used internally unless you need access to the column's "
            "internal ID."
        ),
    )

    #: Records in the table
    records: Optional[pd.DataFrame] = Field(
        None,
        title="Table Records",
        description=(
            "Optional records provided by Opvia, presented as a Pandas DataFrame, if "
            "the field specified that records should be included. "
            "The DataFrame's column names are the column field names, i.e. the keys of "
            "``columns``"
        ),
    )

    records_scope: Optional[RecordsScope] = Field(
        None,
        title="Records Scope",
        description=(
            "If records are provided, this specifies if the provided records are from "
            "just one page, or if they're from all pages."
        ),
    )

    @validator("records", pre=True)
    def transform_records(cls, records_raw: Optional[Dict[str, List[Any]]]):
        """
        Parse the input JSON as a dataframe
        """
        if records_raw is None:
            return None

        return pd.DataFrame.from_records(records_raw)


class _UploadEntityBase(Entity):
    """
    Base class defining how upload inputs are specified and presented to the
    user
    """

    #: File identifier
    file_identifier: str = Field(
        ...,
        title="Upload file identifier",
        description=(
            "Filename of the upload on the local file system. "
            "Can be opened and used as a file normally, as it's downloaded "
            "automatically before the script executes."
        ),
    )

    #: Signed download URL
    download_url: str = Field(
        ...,
        title="Download URL",
        description=(
            "Internally used pre-signed download URL for the file. "
            "Not generally useful, as the file is already downloaded and available on "
            "the local filesystem as ``file_identifier`` when the script executes."
        ),
    )


class UploadEntity(_UploadEntityBase):
    """
    Definition of an uploaded file in the Opvia platform. Within a script, it
    can be opened locally from its local filename ``file_identifier``
    """

    kind: Literal[EntityKind.UPLOAD] = Field(
        EntityKind.UPLOAD,
        title="kind",
        description=(
            "A literal 'UPLOAD' value to enable discrimination in the JSON "
            "parser. It's not generally necessary to use this value."
        ),
    )

    #: Opvia upload ID
    upload_id: str = Field(
        ...,
        title="Upload ID",
        description="Internal ID of the upload in Opvia",
    )


class CacheItemEntity(_UploadEntityBase):
    """
    An item from some part of the files cache for scripts to access.
    """

    kind: Literal[EntityKind.CACHE_ITEM] = Field(
        EntityKind.CACHE_ITEM,
        title="kind",
        description=(
            "A literal 'CACHE_ITEM' value to enable discrimination in the JSON "
            "parser. It's not generally necessary to use this value."
        ),
    )


class SelectEntity(Entity):
    """
    Selection of str values
    """

    kind: Literal[EntityKind.SELECT] = Field(
        EntityKind.SELECT,
        title="kind",
        description=(
            "A literal 'SELECT' value to enable discrimination in the JSON "
            "parser. It's not generally necessary to use this value."
        ),
    )

    #: Selections
    selections: List[str] = Field(
        ...,
        title="Selections",
        description=(
            "The selections made by the user. If multi-select is enabled, there may be "
            "more than one, and if option creation is enabled, there may be values not "
            "present in the defined list of options."
        ),
    )


class TextEntity(Entity):
    """
    A simple text input
    """

    kind: Literal[EntityKind.TEXT] = EntityKind.TEXT

    #: Text that the user entered
    value: str


class CheckboxEntity(Entity):
    """
    A simple checkbox input
    """

    kind: Literal[EntityKind.CHECKBOX] = EntityKind.CHECKBOX

    #: Value of the checkbox
    checked: bool


class OpviaContextEntity(Entity):
    """
    An internally used entity under the key "__OPVIA_CONTEXT" that contains
    useful context
    """

    # N.B. intentionally omitted from the entity parser on the API - not ever
    # passed in

    kind: Literal[EntityKind.CONTEXT] = Field(
        EntityKind.CONTEXT,
        title="kind",
        description=(
            "A literal 'CONTEXT' value to enable discrimination in the JSON "
            "parser. It's not generally necessary to use this value."
        ),
    )

    #: Organization ID
    org_id: str

    #: Invoking user ID token
    id_token: str


_ENTITIES = {
    EntityKind.COLUMN: ColumnEntity,
    EntityKind.TABLE: TableEntity,
    EntityKind.UPLOAD: UploadEntity,
    EntityKind.SELECT: SelectEntity,
    EntityKind.TEXT: TextEntity,
    EntityKind.CACHE_ITEM: CacheItemEntity,
    EntityKind.CHECKBOX: CheckboxEntity,
}


class AnyEntity(CamelModel):
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
                f"Missing required 'kind' field for entity: {values}"
            ) from e
        try:
            return _ENTITIES[kind](**values)
        except KeyError as e:
            raise MalformedObject(f"Unsupported kind: {kind}") from e


# -- Entity Roles


class EntityRole(CamelModel):
    """
    Specify how a script interacts with an entity in Opvia
    """

    class Config:
        extra = "forbid"

    #: Kind of entity this role corresponds to
    kind: EntityKind

    #: Role of this entity, referenced in the script and mapped by the user to
    #: a specific entity ID
    name: str = Field(
        ...,
        title="Name",
        description=(
            "Name of the field that will appear on the custom card. "
            "This should be unique, as it's also how the value the user inputs "
            "is referenced in the script."
        ),
    )

    #: Longer description of the role
    description: str = Field(
        ...,
        title="Description",
        description="Description of the field that will appear on the custom card",
    )


class ColumnRole(EntityRole):
    """
    Specify how a script interacts with an Opvia column
    """

    kind: Literal[EntityKind.COLUMN] = Field(
        EntityKind.COLUMN,
        title="kind",
        description=(
            "A literal 'COLUMN' value to enable discrimination in the JSON "
            "parser. It's not generally necessary to use this value."
        ),
    )


class _TableRoleBase(CamelModel):

    #: Whether records will be sent with the table
    include_records: bool = Field(
        False,
        title="Include Records?",
        description=(
            "If True, we expect records to be sent from this table when we're running "
            "the script, for example in data processing scripts. If False, no "
            "records from this table will be sent to the script, for example if "
            "the goal is just to add new records to the table without reading existing "
            "records."
        ),
    )


class TableRole(EntityRole, _TableRoleBase):
    """
    A field that will appear in the custom card as a Table select.
    """

    kind: Literal[EntityKind.TABLE] = Field(
        EntityKind.TABLE,
        title="kind",
        description=(
            "A literal 'TABLE' value to enable discrimination in the JSON "
            "parser. It's not generally necessary to use this value."
        ),
    )

    #: Any column roles that must be filled
    columns: List[ColumnRole] = Field(
        ...,
        title="Columns",
        description=(
            "List of column definitions expected in the table. "
            "In order to make scripts flexible enough to apply to tables with "
            "different column IDs and names, we define these placeholder names for "
            "columns we need from each table. These placeholder names are used as the "
            "names of columns for DataFrames when passing data to and from Opvia "
            "tables."
        ),
    )

    #: Whether the selected table must be a collection
    collection_only: bool = Field(
        False,
        title="Only collections?",
        description=(
            "If True, only collections can be submitted as entries to this role."
        ),
    )


class TableByIdRole(EntityRole, _TableRoleBase):
    """
    A field that will appear in a card as a static table selection that cannot
    be changed. Records will be accessible as a dataframe whose column names
    are the column names of the source table.
    """

    kind: Literal[EntityKind.TABLE_BY_ID] = Field(
        EntityKind.TABLE_BY_ID,
        title="kind",
        description=(
            "A literal 'TABLE_BY_ID' value to enable discrimination in the "
            "JSON parser. It's not generally necessary to use this value."
        ),
    )

    table_id: str = Field(..., title="Table ID", description="ID of the table to use")

    view_id: Optional[str] = Field(..., title="View ID", description="Optional view ID")


class UploadRole(EntityRole):
    """
    A field that will appear in the custom card as an Upload select.
    """

    kind: Literal[EntityKind.UPLOAD] = Field(
        EntityKind.UPLOAD,
        title="kind",
        description=(
            "A literal 'UPLOAD' value to enable discrimination in the JSON "
            "parser. It's not generally necessary to use this value."
        ),
    )


class CacheItemRole(EntityRole):
    """
    A field that will appear in the custom card as a selection from a subdir
    of the servicesCache uploads dir
    """

    kind: Literal[EntityKind.CACHE_ITEM] = Field(
        EntityKind.CACHE_ITEM,
        title="kind",
        description=(
            "A literal 'CACHE_ITEM' value to enable discrimination in the JSON "
            "parser. It's not generally necessary to use this value."
        ),
    )

    #: Directory within the servicesCache space to use
    directory: str


class SelectRole(EntityRole):
    """
    A field that will appear in the custom card as a select between some
    defined options.
    """

    kind: Literal[EntityKind.SELECT] = Field(
        EntityKind.SELECT,
        title="kind",
        description=(
            "A literal 'SELECT' value to enable discrimination in the JSON "
            "parser. It's not generally necessary to use this value."
        ),
    )

    #: Whether this is a single- or multi-select
    multi: bool = Field(
        False,
        title="Multi-select",
        description="If the user can select multiple values",
    )

    #: Allow creation of new values by the user
    create: bool = Field(
        False,
        title="Create",
        description=(
            "If the user can define their own values rather than just selecting from "
            "the pre-specified ones."
        ),
    )

    #: Optional default selections to display to the user
    default: Optional[List[str]] = Field(
        None,
        title="Default Value",
        description="A default value to populate the select with",
    )

    #: The options for the select
    options: List[str] = Field(
        ...,
        title="Options",
        description="The options to present to the user in the select",
    )


class TextRole(EntityRole):
    """
    Options for a simple text input
    """

    kind: Literal[EntityKind.TEXT] = EntityKind.TEXT

    #: If a larger multi-line text block should be displayed, otherwise a simple
    #: one-line input is displayed.
    long: bool = False


class CheckboxRole(EntityRole):
    """
    A simple checkbox will appear on the custom card
    """

    kind: Literal[EntityKind.CHECKBOX] = EntityKind.CHECKBOX


_ROLES = {
    EntityKind.TABLE: TableRole,
    EntityKind.TABLE_BY_ID: TableByIdRole,
    EntityKind.COLUMN: ColumnRole,
    EntityKind.UPLOAD: UploadRole,
    EntityKind.SELECT: SelectRole,
    EntityKind.TEXT: TextRole,
    EntityKind.CACHE_ITEM: CacheItemRole,
    EntityKind.CHECKBOX: CheckboxRole,
}


class AnyRole(CamelModel):
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
                f"Missing required 'kind' field for role: {values}"
            ) from e
        try:
            return _ROLES[kind](**values)
        except KeyError as e:
            raise MalformedObject(f"Unsupported kind: {kind}") from e
