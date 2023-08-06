"""
Module for Column DDL
"""

# pylint: disable=unused-argument

import relations_sql
import relations_postgresql

class COLUMN(relations_postgresql.DDL, relations_sql.COLUMN):
    """
    COLUMN DDL
    """

    KINDS = {
        "bool": "BOOLEAN",
        "int": "INT8",
        "float": "FLOAT8",
        "str": "VARCHAR(255)",
        "json": "JSONB"
    }

    COLUMN_NAME = relations_postgresql.COLUMN_NAME

    STORE = """RENAME %s TO %s"""
    AUTO = """BIGSERIAL"""
    EXTRACT = """GENERATED ALWAYS AS ((%s)::%s) STORED"""
    SET_DEFAULT = """ALTER %s SET DEFAULT %s"""
    UNSET_DEFAULT = """ALTER %s DROP DEFAULT"""
    SET_NONE = """ALTER %s SET NOT NULL"""
    UNSET_NONE = """ALTER %s DROP NOT NULL"""

    def extract(self, kind, sql, **kwargs):
        """
        Get extract DDL
        """

        sql.append(self.KINDS.get(self.migration['kind'], self.KINDS["json"]))

        name, path = self.COLUMN_NAME.split(self.migration["store"])
        sql.append(self.EXTRACT % (self.PATH % (self.quote(name), self.str(self.walk(path))), self.KINDS.get(kind, self.KINDS["json"])))

    def kind(self, sql):
        """
        Modifies the kind
        """

        cast = self.KINDS.get(self.migration.get("kind", self.definition["kind"]), self.KINDS["json"])

        sql.append(f'ALTER {self.name()} TYPE {cast} USING {self.name()}::{cast}')
