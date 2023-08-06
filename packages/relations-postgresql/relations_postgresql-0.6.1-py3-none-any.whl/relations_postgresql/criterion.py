"""
Module for all Relations PostgreSQL Criterions, pieces of Criteria
"""

import relations_sql
import relations_postgresql


class CRITERION(relations_postgresql.SQL):
    """
    CRITERION class, for comparing two values
    """

    LEFT = relations_postgresql.COLUMN_NAME
    RIGHT = relations_postgresql.VALUE

    JSONPATH = True


class NULL(CRITERION, relations_sql.NULL):
    """
    For IS NULL and IS NOT NULL
    """


class EQ(CRITERION, relations_sql.EQ):
    """
    For =
    """


class GT(CRITERION, relations_sql.GT):
    """
    For >
    """


class GTE(CRITERION, relations_sql.GTE):
    """
    For >=
    """


class LT(CRITERION, relations_sql.LT):
    """
    For <
    """


class LTE(CRITERION, relations_sql.LTE):
    """
    For <=
    """


class FUZZY(CRITERION):
    """
    Base for fuzzy matching
    """

    CAST = "(%s)::VARCHAR(255)"


class LIKE(FUZZY, relations_sql.LIKE):
    """
    For fuzzy matching
    """


class START(FUZZY, relations_sql.START):
    """
    For fuzzy matching end of string
    """


class END(FUZZY, relations_sql.END):
    """
    For fuzzy matching end of string
    """


class IN(CRITERION, relations_sql.IN):
    """
    For IN
    """

    RIGHT = relations_postgresql.LIST
    VALUE = relations_postgresql.VALUE


class CONTAINS(CRITERION, relations_sql.CONTAINS):
    """
    Wether one set contains another
    """

    OPERAND = "(%s)::JSONB @> %s"


class LENGTHS(CRITERION, relations_sql.LENGTHS):
    """
    Wether one set contains another
    """

    OPERAND = "jsonb_array_length((%s)::JSONB)=jsonb_array_length(%s)"
