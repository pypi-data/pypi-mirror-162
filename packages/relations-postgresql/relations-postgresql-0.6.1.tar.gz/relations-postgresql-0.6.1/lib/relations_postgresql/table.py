"""–
Module for Column DDL
"""

# pylint: disable=unused-argument

import relations_sql
import relations_postgresql


class TABLE(relations_postgresql.DDL, relations_sql.TABLE):
    """
    TABLE DDL
    """

    NAME = relations_postgresql.TABLE_NAME
    COLUMN = relations_postgresql.COLUMN
    INDEX = relations_postgresql.INDEX
    UNIQUE = relations_postgresql.UNIQUE

    INDEXES = False

    SCHEMA = """ALTER TABLE %s SET SCHEMA %s"""
    STORE = """ALTER TABLE %s RENAME TO %s"""
    PRIMARY = """PRIMARY KEY (%s)"""

    def name(self, state="migration", rename=False): # pylint: disable=arguments-differ
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

    def store(self, sql):
        """
        Change the schema
        """

        sql.append(self.STORE % (self.name(state={"name": "definition", "schema": "migration"}), self.name(rename=True)))
