"""
Module for Column DDL
"""

# pylint: disable=unused-argument

import relations_sql
import relations_sqlite

class COLUMN(relations_sqlite.DDL, relations_sql.COLUMN):
    """
    COLUMN DDL
    """

    KINDS = {
        "bool": "INTEGER",
        "int": "INTEGER",
        "float": "REAL",
        "str": "TEXT",
        "json": "TEXT"
    }

    COLUMN_NAME = relations_sqlite.COLUMN_NAME

    AUTO = """INTEGER PRIMARY KEY"""
    EXTRACT = """AS (%s)"""

    def __init__(self, migration=None, definition=None, added=False, **kwargs):

        super().__init__(migration, definition, added, **kwargs)

        if self.migration and self.migration.get("kind") == "bool" and "default" in self.migration:
            self.migration["default"] = int(self.migration["default"])
