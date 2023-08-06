"""–
Module for Column DDL
"""

# pylint: disable=unused-argument,arguments-differ

import relations_sql
import relations_sqlite


class INDEX(relations_sqlite.DDL, relations_sql.INDEX):
    """
    INDEX DDL
    """

    TABLE = relations_sqlite.TABLE_NAME
    COLUMNS = relations_sqlite.COLUMN_NAMES

    CREATE = "INDEX"

    def name(self, definition=False, full=True):
        """
        Generate a quoted name, with store as the default
        """

        state = self.definition if definition else self.migration
        name = state['store'] if 'store' in state else state['name']

        sql = []

        table = self.TABLE(**state["table"]) if state.get("table") else None

        if table and full and table.schema:
            sql.append(self.quote(table.schema.name))

        if table:
            name = f"{table.name}_{name}"

        name = name.replace("-", "_")

        sql.append(self.quote(name))

        return self.SEPARATOR.join(sql)

    def create(self, **kwargs):
        """
        CREATE DLL
        """

        sql = []

        if "table" in self.migration:
            sql.append("CREATE")

        sql.append(self.CREATE)
        sql.append(self.name())

        if self.migration.get("table"):
            table = self.TABLE(name=self.migration['table']["name"])
            table.generate()
            sql.append(f"ON {table.sql}")

        columns = self.COLUMNS(self.migration["columns"])
        columns.generate()
        sql.append(columns.sql)

        self.sql = " ".join(sql)

    def modify(self, indent=0, count=0, pad=' ', **kwargs):
        """
        MODIFY DLL
        """

        sql = []

        self.drop(**kwargs)
        sql.append(self.sql)

        self.create(**kwargs)
        sql.append(self.sql)

        migration = pad * (count * indent)
        delimitter = f";\n\n{migration}"

        self.sql = f"{delimitter.join(sql)};\n"

class UNIQUE(INDEX):
    """
    UNIQUE INDEX DDL
    """

    CREATE = "UNIQUE INDEX"
