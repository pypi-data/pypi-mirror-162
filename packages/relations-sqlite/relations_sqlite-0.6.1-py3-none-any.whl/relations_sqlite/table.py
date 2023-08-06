"""–
Module for Column DDL
"""

# pylint: disable=unused-argument,arguments-differ

import relations_sql
import relations_sqlite


class TABLE(relations_sqlite.DDL, relations_sql.TABLE):
    """
    TABLE DDL
    """

    NAME = relations_sqlite.TABLE_NAME
    COLUMN = relations_sqlite.COLUMN
    INDEX = relations_sqlite.INDEX
    UNIQUE = relations_sqlite.UNIQUE
    INSERT = relations_sqlite.INSERT
    SELECT = relations_sqlite.SELECT

    INDEXES = False

    def name(self, state="migration", prefix='', rename=False):
        """
        Generate a quoted name, with table as the default
        """

        if isinstance(state, str):
            state = {
                "name": state,
                "schema": state
            }

        definition_store = (self.definition or {}).get("store")
        definition_schema = (self.definition or {}).get("schema")

        migration_store = (self.migration or {}).get("store")
        migration_schema = (self.migration or {}).get("schema")

        if state["name"] == "migration":
            store = migration_store or definition_store
        else:
            store = definition_store or migration_store

        store = prefix + store

        if not rename:
            if state["schema"] == "migration":
                schema = migration_schema or definition_schema
            else:
                schema = definition_schema or migration_schema
        else:
            schema = None

        table = self.NAME(store, schema=schema)

        table.generate()

        return table.sql

    def modify(self, indent=0, count=0, pad=' ', **kwargs): # pylint: disable=too-many-locals,too-many-branches
        """
        MODIFY DLL
        """

        sql = [f"""ALTER TABLE {self.name(state='definition')} RENAME TO {self.name(state='definition', prefix='_old_', rename=True)}"""]

        migration = {
            "store": self.migration.get("store", self.definition["store"]),
            "schema": self.migration.get("schema", self.definition.get("schema")),
            "fields": [],
            "index": {},
            "unique": {},
        }

        for attr in ["name", "store", "schema"]:
            value = self.migration.get(attr, self.definition.get(attr))
            if value is not None:
                migration[attr] = value

        renames = {}

        for field in self.definition.get("fields", []):
            if field.get("inject") or field["name"] in self.migration.get("fields", {}).get("remove", []):
                continue
            if field["name"] in self.migration.get("fields", {}).get("change", {}):
                migration["fields"].append({**field, **self.migration["fields"]["change"][field["name"]]})
                renames[self.migration["fields"]["change"][field["name"]].get("store", field["store"])] = field["store"]
            else:
                migration["fields"].append(field)
                renames[field["store"]] = field["store"]

        for field in self.migration.get("fields", {}).get("add", []):
            if field.get("inject"):
                continue
            migration["fields"].append(field)

        table = {
            "name": self.definition["store"],
            "schema": self.definition.get("schema")
        }

        indexes = []

        for index in self.definition.get("index", {}):
            indexes.append(self.INDEX(definition={
                "name": index,
                "columns": self.definition["index"][index],
                "table": table
            }))
            if index in self.migration.get("index", {}).get("remove", []):
                continue
            if index in self.migration.get("index", {}).get("rename", {}):
                migration["index"][self.migration["index"]["rename"][index]] = self.definition["index"][index]
            else:
                migration["index"][index] = self.definition["index"][index]

        migration["index"].update(self.migration.get("index", {}).get("add", {}))

        for index in self.definition.get("unique", {}):
            indexes.append(self.UNIQUE(definition={
                "name": index,
                "columns": self.definition["unique"][index],
                "table": table
            }))
            if index in self.migration.get("unique", {}).get("remove", []):
                continue
            if index in self.migration.get("unique", {}).get("rename", {}):
                migration["unique"][self.migration["unique"]["rename"][index]] = self.definition["unique"][index]
            else:
                migration["unique"][index] = self.definition["unique"][index]

        migration["unique"].update(self.migration.get("unique", {}).get("add", {}))

        current = pad * (count * indent)
        delimitter = f";\n\n{current}"

        for index in indexes:
            index.generate()
            sql.append(index.sql)

        ddl = self.__class__(migration)
        ddl.generate(indent=indent, count=count, pad=pad, **kwargs)
        sql.append(ddl.sql[:-2])

        query = self.INSERT(
            self.NAME(ddl.migration["store"], schema=ddl.migration.get("schema")), COLUMNS=sorted(renames.keys()),
            SELECT=self.SELECT(FIELDS=renames).FROM(relations_sql.SQL(self.name(state='definition', prefix='_old_')))
        )

        query.generate(indent, count, pad, **kwargs)
        sql.append(query.sql)

        sql.append(f"""DROP TABLE {self.name(state='definition', prefix='_old_')}""")

        self.sql = f"{delimitter.join(sql)};\n"
