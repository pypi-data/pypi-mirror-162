"""
Module for all Relations PostgreSQL Queries.
"""

import collections

import relations_sql
import relations_postgresql

class QUERY(relations_postgresql.SQL, relations_sql.CLAUSE):
    """
    Base query
    """


class SELECT(relations_postgresql.SQL, relations_sql.SELECT):
    """
    SELECT
    """

    CLAUSES = collections.OrderedDict([
        ("OPTIONS", relations_postgresql.OPTIONS),
        ("FIELDS", relations_postgresql.FIELDS),
        ("FROM", relations_postgresql.FROM),
        ("WHERE", relations_postgresql.WHERE),
        ("GROUP_BY", relations_postgresql.GROUP_BY),
        ("HAVING", relations_postgresql.HAVING),
        ("ORDER_BY", relations_postgresql.ORDER_BY),
        ("LIMIT", relations_postgresql.LIMIT)
    ])


class INSERT(relations_postgresql.SQL, relations_sql.INSERT):
    """
    INSERT query
    """

    CLAUSES = collections.OrderedDict([
        ("OPTIONS", relations_postgresql.OPTIONS),
        ("TABLE", relations_postgresql.TABLE_NAME),
        ("COLUMNS", relations_postgresql.COLUMN_NAMES),
        ("VALUES", relations_postgresql.VALUES),
        ("SELECT", SELECT)
    ])


class LIMITED(relations_postgresql.SQL, relations_sql.LIMITED):
    """
    Clause that has a limit
    """


class UPDATE(relations_postgresql.SQL, relations_sql.UPDATE):
    """
    UPDATE query
    """

    CLAUSES = collections.OrderedDict([
        ("OPTIONS", relations_postgresql.OPTIONS),
        ("TABLE", relations_postgresql.TABLE_NAME),
        ("SET", relations_postgresql.SET),
        ("WHERE", relations_postgresql.WHERE),
        ("ORDER_BY", relations_postgresql.ORDER_BY),
        ("LIMIT", relations_postgresql.LIMIT)
    ])


class DELETE(relations_postgresql.SQL, relations_sql.DELETE):
    """
    DELETE query
    """

    CLAUSES = collections.OrderedDict([
        ("OPTIONS", relations_postgresql.OPTIONS),
        ("TABLE", relations_postgresql.TABLE_NAME),
        ("WHERE", relations_postgresql.WHERE),
        ("ORDER_BY", relations_postgresql.ORDER_BY),
        ("LIMIT", relations_postgresql.LIMIT)
    ])
