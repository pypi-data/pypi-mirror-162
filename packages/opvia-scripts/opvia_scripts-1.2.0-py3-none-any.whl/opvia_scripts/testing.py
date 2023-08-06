import os
from typing import Dict, List

import altair as alt
import pandas as pd

from opvia_scripts.constants import OPVIA_CONTEXT
from opvia_scripts.script_utils import (
    AltairDataTypes,
    altair_column_encoding,
    altair_column_id,
    altair_table_source,
    download_tabular_files,
    put_cache_item,
)
from opvia_scripts.types.entity import (
    AnyEntity,
    AnyRole,
    CacheItemEntity,
    CacheItemRole,
    CheckboxEntity,
    CheckboxRole,
    ColumnRole,
    Entity,
    OpviaContextEntity,
    SelectEntity,
    SelectRole,
    TableEntity,
    TableRole,
    TextEntity,
    TextRole,
    UploadEntity,
    UploadRole,
)
from opvia_scripts.types.result import (
    NewCollectionPage,
    NewRecords,
    NewUpload,
    NewVegaChart,
    ScriptResult,
    UploadKind,
)
from opvia_scripts.types.script import Script

TARGET_TABLE_ROLE = "Import Target"
INPUT_UPLOAD_ROLE = "File to upload"
COLUMN_A_COLUMN = "first column role"
COLUMN_B_COLUMN = "second column role"
COLUMN_C_COLUMN = "third column role"
COLUMN_D_COLUMN = "fourth column role"


# To test this class out, add it to the 'opvia.services' plugin section of
# pyproject.toml:
#
# [tool.poetry.plugins."opvia.services"]
# simple-csv = "opvia_scripts.testing:SimpleCsvImport"


class SimpleCsvImport(Script):
    """
    Testing simple CSV import that just converts the CSV into a DataFrame
    """

    title = "DEBUG Simple CSV Import"

    description = (
        "Imports a CSV file directly, maintaining the column names and "
        "directly loading the values"
    )

    input_roles: List[AnyRole] = [
        UploadRole(
            name=INPUT_UPLOAD_ROLE, description="Some description of the expected file."
        )
    ]

    config_roles: List[AnyRole] = [
        TableRole(
            name=TARGET_TABLE_ROLE,
            description="Some description of the target table.",
            columns=[
                ColumnRole(
                    name=COLUMN_A_COLUMN, description="Description for column A"
                ),
                ColumnRole(
                    name=COLUMN_B_COLUMN, description="Description for column B"
                ),
                ColumnRole(
                    name=COLUMN_C_COLUMN, description="Description for column C"
                ),
                ColumnRole(
                    name=COLUMN_D_COLUMN, description="Description for column D"
                ),
            ],
        )
    ]

    def run(self, entities: Dict[str, Entity]) -> List[ScriptResult]:
        uploaded_file: UploadEntity = entities[INPUT_UPLOAD_ROLE]

        result = pd.read_csv(uploaded_file.file_identifier)

        result.columns = [
            COLUMN_A_COLUMN,
            COLUMN_B_COLUMN,
            COLUMN_C_COLUMN,
            COLUMN_D_COLUMN,
        ]

        return [
            NewRecords(
                table_role=TARGET_TABLE_ROLE,
                records=result,
            ),
        ]


TABLE_ROLE_1 = "Table Role 1"
TABLE_ROLE_2 = "Table Role 2"
TABLE_ROLE_3 = "Table Role 3"
ROLE_COLUMN = "Role"
VALUES_COLUMN = "Values"
UPLOAD_ROLE_1 = "Upload Role 1"
UPLOAD_ROLE_2 = "Upload Role 2"
UPLOAD_ROLE_3 = "Upload Role 3"


# To test this class out, add it to the 'opvia.services' plugin section of
# pyproject.toml:
#
# [tool.poetry.plugins."opvia.services"]
# table-and-upload = "opvia_scripts.testing:TableAndUpload"


class TableAndUpload(Script):
    """
    Testing script that adds a list of all roles to all tables
    """

    title = "DEBUG Table and upload"

    description = "Has table and upload elements on both the card and config section"

    input_roles: List[AnyRole] = [
        TableRole(
            name=TABLE_ROLE_1,
            description="Description for Table 1",
            columns=[
                ColumnRole(name=ROLE_COLUMN, description="Column for the role names"),
                ColumnRole(name=VALUES_COLUMN, description="Column for the parsed IDs"),
            ],
        ),
        UploadRole(name=UPLOAD_ROLE_1, description="Description for Upload 1"),
        TableRole(
            name=TABLE_ROLE_2,
            description="Description for Table 2",
            columns=[
                ColumnRole(name=ROLE_COLUMN, description="Column for the role names"),
                ColumnRole(name=VALUES_COLUMN, description="Column for the parsed IDs"),
            ],
        ),
    ]

    config_roles: List[AnyRole] = [
        UploadRole(name=UPLOAD_ROLE_2, description="Description for Upload 2"),
        TableRole(
            name=TABLE_ROLE_3,
            description="Description for Table 3",
            columns=[
                ColumnRole(name=ROLE_COLUMN, description="Column for the role names"),
                ColumnRole(name=VALUES_COLUMN, description="Column for the parsed IDs"),
            ],
        ),
        UploadRole(name=UPLOAD_ROLE_3, description="Description for Upload 3"),
    ]

    def run(self, entities: Dict[str, AnyEntity]) -> List[ScriptResult]:
        local_file_1: UploadEntity = entities[UPLOAD_ROLE_1]
        local_file_2: UploadEntity = entities[UPLOAD_ROLE_2]
        local_file_3: UploadEntity = entities[UPLOAD_ROLE_3]
        table_id_1: TableEntity = entities[TABLE_ROLE_1]
        table_id_2: TableEntity = entities[TABLE_ROLE_2]
        table_id_3: TableEntity = entities[TABLE_ROLE_3]

        results: List[ScriptResult] = []
        for table_role in [TABLE_ROLE_1, TABLE_ROLE_2, TABLE_ROLE_3]:

            entity: TableEntity = entities[table_role]

            data = {
                ROLE_COLUMN: [
                    UPLOAD_ROLE_1,
                    UPLOAD_ROLE_2,
                    UPLOAD_ROLE_3,
                    TABLE_ROLE_1,
                    TABLE_ROLE_2,
                    TABLE_ROLE_3,
                    ROLE_COLUMN,
                    VALUES_COLUMN,
                ],
                VALUES_COLUMN: [
                    local_file_1.file_identifier,
                    local_file_2.file_identifier,
                    local_file_3.file_identifier,
                    table_id_1.table_id,
                    table_id_2.table_id,
                    table_id_3.table_id,
                    entity.columns[ROLE_COLUMN],
                    entity.columns[VALUES_COLUMN],
                ],
            }

            results.append(
                NewRecords(
                    table_role=table_role,
                    records=pd.DataFrame.from_dict(data),
                )
            )

        return results


# To test this class out, add it to the 'opvia.services' plugin section of
# pyproject.toml:
#
# [tool.poetry.plugins."opvia.services"]
# column-mapping = "opvia_scripts.testing:ColumnMappingExample"

CME_TABLE_ROLE_1 = "Table Role 1"
CME_TABLE_ROLE_2 = "Table Role 2"
CME_TABLE_ROLE_3 = "Table Role 3"
CME_COLUMN_ROLE_1A = "Column 1A"
CME_COLUMN_ROLE_1B = "Column 1B"
CME_COLUMN_ROLE_1C = "Column 1C"
CME_COLUMN_ROLE_2A = "Column 2A"
CME_COLUMN_ROLE_2B = "Column 2B"
CME_COLUMN_ROLE_2C = "Column 2C"


class ColumnMappingExample(Script):
    """
    Testing script that adds a list of all roles to all tables
    """

    title = "DEBUG Column Mapping Example"

    description = "Has columns specified as part of the role definition"

    input_roles: List[AnyRole] = [
        TableRole(
            name=CME_TABLE_ROLE_1,
            description="Table and column config on the card",
            columns=[
                ColumnRole(
                    name=CME_COLUMN_ROLE_1A,
                    description="Description for column role 1A",
                ),
                ColumnRole(
                    name=CME_COLUMN_ROLE_1B,
                    description="Description for column role 1B",
                ),
                ColumnRole(
                    name=CME_COLUMN_ROLE_1C,
                    description="Description for column role 1C",
                ),
            ],
        ),
        TableRole(
            name=CME_TABLE_ROLE_3,
            description="Table with no defined column roles",
            columns=[],
        ),
    ]

    config_roles: List[AnyRole] = [
        TableRole(
            name=CME_TABLE_ROLE_2,
            description="Table and column config in the card config",
            columns=[
                ColumnRole(
                    name=CME_COLUMN_ROLE_2A,
                    description="Description for column role 2A",
                ),
                ColumnRole(
                    name=CME_COLUMN_ROLE_2B,
                    description="Description for column role 2B",
                ),
                ColumnRole(
                    name=CME_COLUMN_ROLE_2C,
                    description="Description for column role 2C",
                ),
            ],
        ),
    ]

    def run(self, entities: Dict[str, Entity]) -> List[ScriptResult]:
        data_table_1 = {
            CME_COLUMN_ROLE_1A: [1, 2, 3, 4],
            CME_COLUMN_ROLE_1B: [5, 6, 7, 8],
            CME_COLUMN_ROLE_1C: [9, 10, 11, 12],
        }

        data_table_2 = {
            CME_COLUMN_ROLE_2A: ["A", "B", "C", "D"],
            CME_COLUMN_ROLE_2B: ["E", "F", "G", "H"],
            CME_COLUMN_ROLE_2C: ["I", "J", "K", "L"],
        }

        return [
            NewRecords(
                table_role=CME_TABLE_ROLE_1,
                records=pd.DataFrame.from_dict(data_table_1),
            ),
            NewRecords(
                table_role=CME_TABLE_ROLE_2,
                records=pd.DataFrame.from_dict(data_table_2),
            ),
        ]


# To test this class out, add it to the 'opvia.services' plugin section of
# pyproject.toml:
#
# [tool.poetry.plugins."opvia.services"]
# new-upload = "opvia_scripts.testing:CreateNewUpload"
class CreateNewUpload(Script):
    """
    Testing script that just takes nothing and returns a new upload
    """

    title = "DEBUG Create New Upload"

    description = "Creates a new upload as a direct copy of the uploaded file"

    input_roles: List[AnyRole] = [
        UploadRole(
            name=INPUT_UPLOAD_ROLE,
            description="Some file.",
        )
    ]

    config_roles: List[AnyRole] = []

    def run(self, entities: Dict[str, Entity]) -> List[ScriptResult]:
        uploaded_file: UploadEntity = entities[INPUT_UPLOAD_ROLE]

        return [
            NewUpload(
                file_location=uploaded_file.file_identifier,
                upload_kind=UploadKind.image,
                caption="A caption",
            )
        ]


SELECT_ROLE_A = "Select A"
SELECT_ROLE_B = "Select B"


# To test this class out, add it to the 'opvia.services' plugin section of
# pyproject.toml:
#
# [tool.poetry.plugins."opvia.services"]
# multi-select = "opvia_scripts.testing:SelectExample"


class SelectExample(Script):
    """
    Testing a select
    """

    title = "DEBUG Select Example"

    description = (
        "Provides a couple selects that determine what table data gets returned"
    )

    input_roles: List[AnyRole] = [
        SelectRole(
            name=SELECT_ROLE_A,
            description="Some description of the expected file.",
            multi=True,
            options=["Option A", "Option B", "Option C", "Option D"],
        )
    ]

    config_roles: List[AnyRole] = [
        SelectRole(
            name=SELECT_ROLE_B,
            description="Some description of the expected file.",
            multi=False,
            options=["Option 1", "Option 2", "Option 3", "Option 4"],
        ),
        TableRole(
            name=TARGET_TABLE_ROLE,
            description="Some description of the target table.",
            columns=[
                ColumnRole(
                    name=COLUMN_A_COLUMN,
                    description="Description for column A",
                ),
                ColumnRole(
                    name=COLUMN_B_COLUMN,
                    description="Description for column B",
                ),
            ],
        ),
    ]

    def run(self, entities: Dict[str, Entity]) -> List[ScriptResult]:
        selections_a: SelectEntity = entities[SELECT_ROLE_A]
        selections_b: SelectEntity = entities[SELECT_ROLE_B]

        results = {
            COLUMN_A_COLUMN: selections_a.selections,
            COLUMN_B_COLUMN: selections_b.selections,
        }

        return [
            NewRecords(
                table_role=TARGET_TABLE_ROLE,
                records=pd.DataFrame.from_dict(results, orient="index").T,
            ),
        ]


# To test this class out, add it to the 'opvia.services' plugin section of
# pyproject.toml:
#
# [tool.poetry.plugins."opvia.services"]
# opvia-context = "opvia_scripts.testing:ContextExample"


class ContextExample(Script):
    """
    Testing a select
    """

    title = "DEBUG Context Example"

    description = "Shows that context can be added"

    input_roles: List[AnyRole] = []

    config_roles: List[AnyRole] = [
        TableRole(
            name=TARGET_TABLE_ROLE,
            description="Some description of the target table.",
            columns=[
                ColumnRole(
                    name=COLUMN_A_COLUMN,
                    description="Description for column A",
                ),
            ],
        ),
    ]

    def run(self, entities: Dict[str, Entity]) -> List[ScriptResult]:
        context: OpviaContextEntity = entities[OPVIA_CONTEXT]

        results = {COLUMN_A_COLUMN: [context.org_id, context.id_token]}

        return [
            NewRecords(
                table_role=TARGET_TABLE_ROLE,
                records=pd.DataFrame.from_dict(results),
            ),
        ]


# To test this class out, add it to the 'opvia.services' plugin section of
# pyproject.toml:
#
# [tool.poetry.plugins."opvia.services"]
# task-logging = "opvia_scripts.testing:TaskLoggingExample"


class TaskLoggingExample(Script):
    """
    Testing a select
    """

    title = "DEBUG Task Logging"

    description = "Logs some stuff to the tasks service"

    input_roles: List[AnyRole] = [
        SelectRole(
            name=SELECT_ROLE_A,
            description="Some description of the expected options.",
            multi=True,
            options=["Option A", "Option B", "Option C", "Option D", "Broken Option"],
        )
    ]

    config_roles: List[AnyRole] = [
        TableRole(
            name=TARGET_TABLE_ROLE,
            description="Some description of the target table.",
            columns=[
                ColumnRole(
                    name=COLUMN_A_COLUMN,
                    description="Description for column A",
                ),
            ],
        ),
    ]

    def run(self, entities: Dict[str, Entity]) -> List[ScriptResult]:
        selections_a: SelectEntity = entities[SELECT_ROLE_A]

        self.logger.info(f"You selected {selections_a.selections!r}")
        self.logger.warning("A warning message")

        if "Broken Option" in selections_a.selections:
            raise ValueError("You shouldn't pick the broken option")

        results = {COLUMN_A_COLUMN: selections_a.selections}

        return [
            NewRecords(
                table_role=TARGET_TABLE_ROLE,
                records=pd.DataFrame.from_dict(results, orient="index").T,
            ),
        ]


# To test this class out, add it to the 'opvia.services' plugin section of
# pyproject.toml:
#
# [tool.poetry.plugins."opvia.services"]
# table-data-echo = "opvia_scripts.testing:TableDataEchoExample"

ECHO_SOURCE_TABLE_ROLE = "Source Table"
ECHO_TARGET_TABLE_ROLE = "Target Table"

SOURCE_COL_A = "first source column"
SOURCE_COL_B = "second source column"
SOURCE_COL_C = "third source column"
SOURCE_COL_D = "fourth source column"
TARGET_COL_A = "first target column"
TARGET_COL_B = "second target column"
TARGET_COL_C = "third target column"
TARGET_COL_D = "fourth target column"


class TableDataEchoExample(Script):
    """
    Testing data ingestion and processing
    """

    title = "DEBUG Table data echo"

    description = "Return copies of the records we get"

    input_roles: List[AnyRole] = [
        TableRole(
            name=ECHO_SOURCE_TABLE_ROLE,
            description="Data goes in",
            include_records=True,
            columns=[
                ColumnRole(
                    name=SOURCE_COL_A,
                    description="",
                ),
                ColumnRole(
                    name=SOURCE_COL_B,
                    description="",
                ),
                ColumnRole(
                    name=SOURCE_COL_C,
                    description="",
                ),
                ColumnRole(
                    name=SOURCE_COL_D,
                    description="",
                ),
            ],
        ),
        TableRole(
            name=ECHO_TARGET_TABLE_ROLE,
            description="Data comes out",
            include_records=False,
            columns=[
                ColumnRole(
                    name=TARGET_COL_A,
                    description="",
                ),
                ColumnRole(
                    name=TARGET_COL_B,
                    description="",
                ),
                ColumnRole(
                    name=TARGET_COL_C,
                    description="",
                ),
                ColumnRole(
                    name=TARGET_COL_D,
                    description="",
                ),
            ],
        ),
    ]

    config_roles: List[AnyRole] = []

    def run(self, entities: Dict[str, Entity]) -> List[ScriptResult]:
        table: TableEntity = entities[ECHO_SOURCE_TABLE_ROLE]

        df = table.records

        if df is None:
            return []

        df = df.rename(
            columns={
                SOURCE_COL_A: TARGET_COL_A,
                SOURCE_COL_B: TARGET_COL_B,
                SOURCE_COL_C: TARGET_COL_C,
                SOURCE_COL_D: TARGET_COL_D,
            }
        )

        return [NewRecords(table_role=ECHO_TARGET_TABLE_ROLE, records=df)]


# To test this class out, add it to the 'opvia.services' plugin section of
# pyproject.toml:
#
# [tool.poetry.plugins."opvia.services"]
# text-role-example = "opvia_scripts.testing:TextRoleExample"

SOME_TEXT_1_ROLE = "Some short text"
SOME_TEXT_2_ROLE = "Some long text"
SOME_TABLE_ROLE = "Some table"

TEXT_COL_ROLE = "Some text col"


class TextRoleExample(Script):
    """
    Testing text roles
    """

    title = "DEBUG Text role test"

    description = "Inserts some text into a table"

    input_roles: List[AnyRole] = [
        TextRole(
            name=SOME_TEXT_1_ROLE,
            description="Some text to enter",
            long=False,
        ),
        TextRole(
            name=SOME_TEXT_2_ROLE,
            description="Some long to enter",
            long=True,
        ),
        TableRole(
            name=SOME_TABLE_ROLE,
            description="Some table to add text data to",
            columns=[
                ColumnRole(
                    name=TEXT_COL_ROLE,
                    description="",
                ),
            ],
        ),
    ]

    config_roles: List[AnyRole] = []

    def run(self, entities: Dict[str, Entity]) -> List[ScriptResult]:
        short_text: TextEntity = entities[SOME_TEXT_1_ROLE]
        long_text: TextEntity = entities[SOME_TEXT_2_ROLE]

        df = pd.DataFrame.from_records(
            [
                {TEXT_COL_ROLE: short_text.value},
                {TEXT_COL_ROLE: long_text.value},
            ]
        )

        return [NewRecords(table_role=SOME_TABLE_ROLE, records=df)]


# To test this class out, add it to the 'opvia.services' plugin section of
# pyproject.toml:
#
# [tool.poetry.plugins."opvia.services"]
# files-in-table = "opvia_scripts.testing:FilesInTableExample"

FILESTABLE_INPUT_TABLE = "Source Table"
FILESTABLE_SINGLE_FILE_COLUMN = "single-select files"
FILESTABLE_MULTI_FILE_COLUMN = "multi-select files"

FILESTABLE_OUTPUT_TABLE = "Target Table"
FILESTABLE_FIRST_LINE_COLUMN = "First line"


class FilesInTableExample(Script):
    """
    Testing getting files from a table
    """

    title = "DEBUG Files in table"

    description = "Get files from a table and add their first lines to a file"

    input_roles: List[AnyRole] = [
        TableRole(
            name=FILESTABLE_INPUT_TABLE,
            description="Data goes in",
            include_records=True,
            columns=[
                ColumnRole(
                    name=FILESTABLE_SINGLE_FILE_COLUMN,
                    description="",
                ),
                ColumnRole(
                    name=FILESTABLE_MULTI_FILE_COLUMN,
                    description="",
                ),
            ],
        ),
        TableRole(
            name=FILESTABLE_OUTPUT_TABLE,
            description="Data comes out",
            include_records=False,
            columns=[
                ColumnRole(
                    name=FILESTABLE_FIRST_LINE_COLUMN,
                    description="",
                ),
            ],
        ),
    ]

    config_roles: List[AnyRole] = []

    def run(self, entities: Dict[str, Entity]) -> List[ScriptResult]:
        table: TableEntity = entities[ECHO_SOURCE_TABLE_ROLE]

        df = table.records

        if df is None:
            return []

        def extract_first_line(file_identifier):
            with open(file_identifier, "r") as f:
                return f.readline().strip()

        results = []

        self.logger.info("Downloading files from table")
        with download_tabular_files(
            df[FILESTABLE_SINGLE_FILE_COLUMN].append(df[FILESTABLE_MULTI_FILE_COLUMN]),
            logger=self.logger,
        ) as downloaded_file_info:
            for local_filename in downloaded_file_info.values():
                line = extract_first_line(local_filename)
                results.append(line)

        new_df = pd.DataFrame.from_records(
            [{FILESTABLE_FIRST_LINE_COLUMN: result} for result in results]
        )

        return [NewRecords(table_role=FILESTABLE_OUTPUT_TABLE, records=new_df)]


# To test this class out, add it to the 'opvia.services' plugin section of
# pyproject.toml:
#
# [tool.poetry.plugins."opvia.services"]
# new-table-files = "opvia_scripts.testing:CreateNewFilesInTableExample"

NEW_FILES_TABLE_TABLE_ROLE = "Target table"

EXAMPLE_NORMAL_COLUMN = "Some normal column"
EXAMPLE_FILE_COLUMN = "File column"
EXAMPLE_MULTIFILE_COLUMN = "Multi-File column"


class CreateNewFilesInTableExample(Script):
    """
    Create new files in an Opvia table
    """

    title = "DEBUG New files in table"

    description = "Add some new files to a table's file column"

    input_roles: List[AnyRole] = [
        TableRole(
            name=NEW_FILES_TABLE_TABLE_ROLE,
            description="Table to add some new files to",
            columns=[
                ColumnRole(
                    name=EXAMPLE_NORMAL_COLUMN,
                    description="",
                ),
                ColumnRole(
                    name=EXAMPLE_FILE_COLUMN,
                    description="",
                ),
                ColumnRole(
                    name=EXAMPLE_MULTIFILE_COLUMN,
                    description="",
                ),
            ],
        ),
    ]

    config_roles: List[AnyRole] = []

    def run(self, entities: Dict[str, Entity]) -> List[ScriptResult]:
        new_files = ["aaa.csv", "bbb.csv", "ccc.csv"]
        for filename in new_files:
            pd.DataFrame.from_dict(
                {"A": [1, 3, 3], "B": [4, 5, 6], "C": [7, 8, 9]}
            ).to_csv(filename)

        new_df = pd.DataFrame.from_records(
            [
                {
                    EXAMPLE_NORMAL_COLUMN: f"Created {filename}",
                    EXAMPLE_FILE_COLUMN: NewUpload(
                        file_location=filename,
                        upload_kind=UploadKind.file,
                    ),
                    EXAMPLE_MULTIFILE_COLUMN: [
                        NewUpload(
                            file_location=f,
                            upload_kind=UploadKind.file,
                        )
                        for f in new_files
                    ],
                }
                for filename in new_files
            ]
        )

        return [NewRecords(table_role=NEW_FILES_TABLE_TABLE_ROLE, records=new_df)]


# To test this class out, add it to the 'opvia.services' plugin section of
# pyproject.toml:
#
# [tool.poetry.plugins."opvia.services"]
# new-collection-page = "opvia_scripts.testing:CreateNewCollectionPageExample"

NEW_COLLECTION_PAGE_COLLECTION_ROLE = "Target collection"

NEW_COLLECTION_PAGE_TITLE_COLUMN = "Page Title"
NEW_COLLECTION_PAGE_FILE_COLUMN = "File column"
NEW_COLLECTION_PAGE_OTHER_COLUMN = "Some other column"


class CreateNewCollectionPageExample(Script):
    """
    Create new collection page with some cards
    """

    title = "DEBUG New page in collection"

    description = "Add a new page to a collection"

    input_roles: List[AnyRole] = [
        TableRole(
            name=NEW_COLLECTION_PAGE_COLLECTION_ROLE,
            description="Table to add some new files to",
            collection_only=True,
            columns=[
                ColumnRole(
                    name=NEW_COLLECTION_PAGE_TITLE_COLUMN,
                    description="",
                ),
                ColumnRole(
                    name=NEW_COLLECTION_PAGE_FILE_COLUMN,
                    description="",
                ),
                ColumnRole(
                    name=NEW_COLLECTION_PAGE_OTHER_COLUMN,
                    description="",
                ),
            ],
        ),
        TableRole(
            name=NEW_FILES_TABLE_TABLE_ROLE,
            description="Table to add some new files to",
            columns=[
                ColumnRole(
                    name=EXAMPLE_NORMAL_COLUMN,
                    description="",
                ),
                ColumnRole(
                    name=EXAMPLE_FILE_COLUMN,
                    description="",
                ),
                ColumnRole(
                    name=EXAMPLE_MULTIFILE_COLUMN,
                    description="",
                ),
            ],
        ),
    ]

    config_roles: List[AnyRole] = []

    def run(self, entities: Dict[str, Entity]) -> List[ScriptResult]:
        collection_file = "collection-attach.csv"
        upload_card_file = "upload-card-file.csv"
        new_files = ["aaa.csv", "bbb.csv", "ccc.csv"]
        for filename in [collection_file, upload_card_file, *new_files]:
            pd.DataFrame.from_dict(
                {
                    "A": [1, 3, 3],
                    "B": [4, 5, 6],
                    "C": [7, 8, 9],
                }
            ).to_csv(filename)

        new_df = pd.DataFrame.from_records(
            [
                {
                    EXAMPLE_NORMAL_COLUMN: f"Created {filename}",
                    EXAMPLE_FILE_COLUMN: NewUpload(
                        file_location=filename,
                        upload_kind=UploadKind.file,
                    ),
                    EXAMPLE_MULTIFILE_COLUMN: [
                        NewUpload(
                            file_location=f,
                            upload_kind=UploadKind.file,
                        )
                        for f in new_files
                    ],
                }
                for filename in new_files
            ]
        )

        collection_record = pd.DataFrame.from_records(
            [
                {
                    NEW_COLLECTION_PAGE_TITLE_COLUMN: "New Page Title",
                    NEW_COLLECTION_PAGE_FILE_COLUMN: NewUpload(
                        file_location=collection_file,
                        upload_kind=UploadKind.file,
                    ),
                    NEW_COLLECTION_PAGE_OTHER_COLUMN: "Some other value",
                }
            ]
        )

        return [
            NewCollectionPage(
                collection_role=NEW_COLLECTION_PAGE_COLLECTION_ROLE,
                record=collection_record,
                cards=[
                    NewRecords(table_role=NEW_FILES_TABLE_TABLE_ROLE, records=new_df),
                    NewUpload(
                        file_location=upload_card_file,
                        upload_kind=UploadKind.file,
                    ),
                ],
            )
        ]


# To test this class out, add it to the 'opvia.services' plugin section of
# pyproject.toml:
#
# [tool.poetry.plugins."opvia.services"]
# data-ingestion-example = "opvia_scripts.testing:DataIngestionExample"

DATA_INGESTION_UPLOADED_FILE = "Uploaded File"

DATA_INGESTION_COLLECTION_ROLE = "Target collection"

DATA_INGESTION_COLL_TITLE_COLUMN = "Submission Title"
DATA_INGESTION_COLL_FILE_COLUMN = "Data File"

DATA_INGESTION_TABLE_ROLE = "Experimental Data"

DATA_COLLECTION_TAB_SAMPLE_COLUMN = "Sample"
DATA_COLLECTION_TAB_CONCENTRATION_COLUMN = "Concentration"
DATA_COLLECTION_TAB_MEASUREMENT_TIME_COLUMN = "Measurement Time"
DATA_COLLECTION_TAB_MEASUREMENT_COLUMN = "Measurement"


class DataIngestionExample(Script):
    """
    Ingest data from a file, to be executed via REST
    """

    title = "DEBUG Data ingestion example"

    description = "Add some data from a file to a collection"

    input_roles: List[AnyRole] = [
        UploadRole(
            name=DATA_INGESTION_UPLOADED_FILE,
            description="A CSV with experimental data",
        ),
        TableRole(
            name=DATA_INGESTION_COLLECTION_ROLE,
            description="Collection to add a new record to",
            collection_only=True,
            columns=[
                ColumnRole(
                    name=DATA_INGESTION_COLL_TITLE_COLUMN,
                    description="",
                ),
                ColumnRole(
                    name=DATA_INGESTION_COLL_FILE_COLUMN,
                    description="",
                ),
            ],
        ),
        TableRole(
            name=DATA_INGESTION_TABLE_ROLE,
            description="Table to add some new data into",
            columns=[
                ColumnRole(
                    name=DATA_COLLECTION_TAB_SAMPLE_COLUMN,
                    description="",
                ),
                ColumnRole(
                    name=DATA_COLLECTION_TAB_CONCENTRATION_COLUMN,
                    description="",
                ),
                ColumnRole(
                    name=DATA_COLLECTION_TAB_MEASUREMENT_TIME_COLUMN,
                    description="",
                ),
                ColumnRole(
                    name=DATA_COLLECTION_TAB_MEASUREMENT_COLUMN,
                    description="",
                ),
            ],
        ),
    ]

    config_roles: List[AnyRole] = []

    def run(self, entities: Dict[str, Entity]) -> List[ScriptResult]:
        def remove_uuid(filename: str):
            split = filename.split("_", maxsplit=1)
            if len(split) == 0:
                return filename
            return split[1]

        uploaded_file: UploadEntity = entities[DATA_INGESTION_UPLOADED_FILE]
        data_file = os.path.join(
            os.path.dirname(uploaded_file.file_identifier),
            remove_uuid(os.path.basename(uploaded_file.file_identifier)),
        )
        os.rename(uploaded_file.file_identifier, data_file)

        df = pd.read_csv(
            data_file,
            parse_dates=[DATA_COLLECTION_TAB_MEASUREMENT_TIME_COLUMN],
        )

        collection_record = pd.DataFrame.from_records(
            [
                {
                    DATA_INGESTION_COLL_TITLE_COLUMN: f"Auto-ingest for {os.path.basename(data_file)}",  # noqa: E501
                    DATA_INGESTION_COLL_FILE_COLUMN: NewUpload(
                        file_location=data_file,
                        upload_kind=UploadKind.file,
                    ),
                }
            ]
        )

        return [
            NewCollectionPage(
                collection_role=DATA_INGESTION_COLLECTION_ROLE,
                record=collection_record,
                cards=[
                    NewRecords(
                        table_role=DATA_INGESTION_TABLE_ROLE,
                        records=df,
                    ),
                ],
            )
        ]


# To test these classes out, add it to the 'opvia.services' plugin section of
# pyproject.toml:
#
# [tool.poetry.plugins."opvia.services"]
# example-put-cache = "opvia_scripts.testing:PutCacheExample"
# example-use-cache = "opvia_scripts.testing:UseCacheExample"

CACHE_ITEM_DIRECTORY = "testCacheDir"
NEW_CACHE_ITEM_NAME_ROLE = "Item Name"
INPUT_CACHE_ITEM_ROLE = "Cache Item"
PUT_TABLE_ROLE = "A table"


class PutCacheExample(Script):
    """
    Testing adding a simple item to a cache
    """

    title = "DEBUG Put Cache Example"

    description = "Put a file into a cache"

    input_roles: List[AnyRole] = [
        TextRole(
            name=NEW_CACHE_ITEM_NAME_ROLE,
            description="Name of the new cache item",
            long=False,
        ),
    ]

    config_roles: List[AnyRole] = []

    def run(self, entities: Dict[str, Entity]) -> List[ScriptResult]:
        context: OpviaContextEntity = entities[OPVIA_CONTEXT]
        new_item_name: TextEntity = entities[NEW_CACHE_ITEM_NAME_ROLE]

        new_filename = "./new-filename.csv"

        pd.DataFrame.from_dict({"A": [1, 3, 3], "B": [4, 5, 6], "C": [7, 8, 9]}).to_csv(
            new_filename
        )

        put_cache_item(
            file_location=new_filename,
            org_id=context.org_id,
            user_token=context.id_token,
            cache_directory=CACHE_ITEM_DIRECTORY,
            cache_item_name=new_item_name.value,
        )

        return []


class UseCacheExample(Script):
    """
    Testing simply using an item from a cache directory
    """

    title = "DEBUG Use Cache Example"

    description = "Uses a cached value, returning it as a new file card"

    input_roles: List[AnyRole] = [
        CacheItemRole(
            name=INPUT_CACHE_ITEM_ROLE,
            description="Select an item from this cache directory.",
            directory=CACHE_ITEM_DIRECTORY,
        ),
        TableRole(
            name=PUT_TABLE_ROLE,
            description="",
            columns=[
                ColumnRole(name="A", description=""),
                ColumnRole(name="B", description=""),
                ColumnRole(name="C", description=""),
            ],
        ),
    ]

    config_roles: List[AnyRole] = []

    def run(self, entities: Dict[str, Entity]) -> List[ScriptResult]:
        cache_item: CacheItemEntity = entities[INPUT_CACHE_ITEM_ROLE]

        return [
            NewRecords(
                table_role=PUT_TABLE_ROLE,
                records=pd.read_csv(cache_item.file_identifier),
            ),
        ]


# To test this class out, add it to the 'opvia.services' plugin section of
# pyproject.toml:
#
# [tool.poetry.plugins."opvia.services"]
# checkbox-role-example = "opvia_scripts.testing:CheckboxRoleExample"

CHECKBOX_FACE_FIELD = "Ticked on face"
CHECKBOX_CONFIG_FIELD = "Ticked on config"

CHECKBOX_TRACKING_TABLE = "Checkboxes table"
IS_CHECKED_COLUMN = "Was ticked"


class CheckboxRoleExample(Script):
    """
    Testing checkbox fields
    """

    title = "DEBUG Checkbox role test"

    description = "Inserts some text into a table"

    input_roles: List[AnyRole] = [
        CheckboxRole(
            name=CHECKBOX_FACE_FIELD,
            description="If the first value should be ticked",
        )
    ]

    config_roles: List[AnyRole] = [
        CheckboxRole(
            name=CHECKBOX_CONFIG_FIELD,
            description="If the second value should be ticked",
        ),
        TableRole(
            name=CHECKBOX_TRACKING_TABLE,
            description="Some table to add checkbox data to",
            columns=[
                ColumnRole(
                    name=IS_CHECKED_COLUMN,
                    description="",
                ),
            ],
        ),
    ]

    def run(self, entities: Dict[str, Entity]) -> List[ScriptResult]:
        face_checkbox: CheckboxEntity = entities[CHECKBOX_FACE_FIELD]
        config_checkbox: CheckboxEntity = entities[CHECKBOX_CONFIG_FIELD]
        df = pd.DataFrame.from_records(
            [
                {IS_CHECKED_COLUMN: "true" if face_checkbox.checked else "false"},
                {IS_CHECKED_COLUMN: "true" if config_checkbox.checked else "false"},
            ]
        )
        return [NewRecords(table_role=CHECKBOX_TRACKING_TABLE, records=df)]


# To test this class out, add it to the 'opvia.services' plugin section of
# pyproject.toml:
#
# [tool.poetry.plugins."opvia.services"]
# vega-chart-demo = "opvia_scripts.testing:VegaChartExample"

VEGA_SOURCE_TABLE_A_ROLE = "Source Table A"
VEGA_SOURCE_TABLE_B_ROLE = "Source Table B"

VEGA_SOURCE_A_COL_A = "source A X column"
VEGA_SOURCE_A_COL_B = "source A Y column"
VEGA_SOURCE_A_COL_C = "source A color column"
VEGA_SOURCE_B_COL_A = "source B X column"
VEGA_SOURCE_B_COL_B = "source B Y column"


class VegaChartExample(Script):
    """
    Testing online and offline data for vega charts
    """

    title = "DEBUG Vega chart example"

    description = (
        "Plot a vega chart based on Opvia table data, including some live data. "
        "The first table is expected to have a simple time series, and the second "
        "to have multiple overlapping data points at each point in time. "
        "The first will be presented as a simple line series and the second as "
        "a mean with a confidence interval shading."
    )

    input_roles: List[AnyRole] = [
        TableRole(
            name=VEGA_SOURCE_TABLE_A_ROLE,
            description="Table A",
            include_records=True,
            columns=[
                ColumnRole(
                    name=VEGA_SOURCE_A_COL_A,
                    description="",
                ),
                ColumnRole(
                    name=VEGA_SOURCE_A_COL_B,
                    description="",
                ),
                ColumnRole(
                    name=VEGA_SOURCE_A_COL_C,
                    description="",
                ),
            ],
        ),
        TableRole(
            name=VEGA_SOURCE_TABLE_B_ROLE,
            description="Table B",
            include_records=True,
            columns=[
                ColumnRole(
                    name=VEGA_SOURCE_B_COL_A,
                    description="",
                ),
                ColumnRole(
                    name=VEGA_SOURCE_B_COL_B,
                    description="",
                ),
            ],
        ),
    ]

    config_roles: List[AnyRole] = []

    def run(self, entities: Dict[str, Entity]) -> List[ScriptResult]:
        table_a: TableEntity = entities[VEGA_SOURCE_TABLE_A_ROLE]
        table_b: TableEntity = entities[VEGA_SOURCE_TABLE_B_ROLE]

        table_a_data = altair_table_source(table_a)
        table_b_data = altair_table_source(table_b)

        chart_a: alt.Chart = (
            alt.Chart(table_a_data)
            .mark_line()
            .encode(
                x=altair_column_encoding(
                    table_a.columns[VEGA_SOURCE_A_COL_A],
                    AltairDataTypes.TEMPORAL,
                ),
                y=altair_column_encoding(
                    table_a.columns[VEGA_SOURCE_A_COL_B],
                    AltairDataTypes.QUANTITATIVE,
                ),
                color=altair_column_encoding(
                    table_a.columns[VEGA_SOURCE_A_COL_C],
                    AltairDataTypes.ORDINAL,
                ),
                strokeDash=altair_column_encoding(
                    table_a.columns[VEGA_SOURCE_A_COL_C],
                    AltairDataTypes.ORDINAL,
                ),
            )
        )

        chart_b_mean = (
            alt.Chart(table_b_data)
            .mark_line()
            .encode(
                x=altair_column_encoding(
                    table_b.columns[VEGA_SOURCE_B_COL_A],
                    AltairDataTypes.TEMPORAL,
                ),
                y=f"mean({altair_column_id(table_b.columns[VEGA_SOURCE_B_COL_B])}):Q",
            )
        )

        chart_b_band: alt.Chart = (
            alt.Chart(table_b_data)
            .mark_errorband(extent="ci")
            .encode(
                x=altair_column_encoding(
                    table_b.columns[VEGA_SOURCE_B_COL_A],
                    AltairDataTypes.TEMPORAL,
                ),
                y=alt.Y(
                    altair_column_encoding(
                        table_b.columns[VEGA_SOURCE_B_COL_B],
                        AltairDataTypes.QUANTITATIVE,
                    ),
                    title="Y axis title",
                ),
            )
        )

        return [
            NewVegaChart(
                chart=(chart_a + chart_b_mean + chart_b_band),
                live_datasets=[
                    table_a,
                    table_b,
                ],
            ),
        ]
