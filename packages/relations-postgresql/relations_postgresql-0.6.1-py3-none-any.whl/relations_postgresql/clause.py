"""
Module for all PostgreSQL SQL relations_sql.CLAUSES, pieces of Queries
"""

import relations_sql
import relations_postgresql


class CLAUSE(relations_postgresql.SQL, relations_sql.CLAUSE):
    """
    Base class for clauses
    """


class ARGS(relations_postgresql.SQL, relations_sql.ARGS):
    """
    Clauses that never have keyword arguments
    """


class OPTIONS(relations_postgresql.SQL, relations_sql.OPTIONS):
    """
    Beginning of a SELECT statement
    """

    ARGS = relations_sql.SQL


class FIELDS(relations_postgresql.SQL, relations_sql.FIELDS):
    """
    FIELDS part of SELECT statement
    """

    ARGS = relations_postgresql.COLUMN_NAME
    KWARG = relations_postgresql.COLUMN_NAME
    KWARGS = relations_postgresql.AS


class FROM(relations_postgresql.SQL, relations_sql.FROM):
    """
    Clause for FROM
    """

    ARGS = relations_postgresql.TABLE_NAME
    KWARG = relations_postgresql.TABLE_NAME
    KWARGS = relations_postgresql.AS


class WHERE(relations_postgresql.SQL, relations_sql.WHERE):
    """
    Clause for WHERE
    """

    ARGS = relations_postgresql.VALUE
    KWARGS = relations_postgresql.OP


class GROUP_BY(relations_postgresql.SQL, relations_sql.GROUP_BY):
    """
    Clasuse for GROUP BY
    """

    ARGS = relations_postgresql.COLUMN_NAME


class HAVING(relations_postgresql.SQL, relations_sql.HAVING):
    """
    Clause for HAVING
    """

    ARGS = relations_postgresql.VALUE
    KWARGS = relations_postgresql.OP


class ORDER_BY(relations_postgresql.SQL, relations_sql.ORDER_BY):
    """
    Clause for the bORDER
    """

    ARGS = relations_postgresql.ORDER
    KWARGS = relations_postgresql.ORDER


class LIMIT(relations_postgresql.SQL, relations_sql.LIMIT):
    """
    Base class for clauses
    """

    ARGS = relations_postgresql.VALUE


class SET(relations_postgresql.SQL, relations_sql.SET):
    """
    relations_sql.CRITERIA for SET
    """

    KWARGS = relations_postgresql.ASSIGN


class VALUES(relations_postgresql.SQL, relations_sql.VALUES):
    """
    relations_sql.CRITERIA for VALUES
    """

    ARGS = relations_postgresql.LIST
