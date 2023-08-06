"""
Module for PostgreSQL CRITERIA
"""

import relations_sql
import relations_postgresql


class CRITERIA(relations_postgresql.SQL, relations_sql.CRITERIA):
    """
    Collection of CRITERIONS
    """


class AND(relations_postgresql.SQL, relations_sql.AND):
    """
    CLAUSE for AND
    """

    ARGS = relations_postgresql.VALUE


class OR(relations_postgresql.SQL, relations_sql.OR):
    """
    CLAUSE for OR
    """

    ARGS = relations_postgresql.VALUE


class SETS(relations_postgresql.SQL, relations_sql.SETS):
    """
    For comparing sets with each other
    """


class HAS(relations_postgresql.SQL, relations_sql.HAS):
    """
    For if the left has all the members of right
    """

    CONTAINS = relations_postgresql.CONTAINS


class ANY(relations_postgresql.SQL, relations_sql.ANY):
    """
    For if the left has any the members of right
    """

    OR = OR
    LEFT = relations_postgresql.COLUMN_NAME
    VALUE = relations_postgresql.VALUE
    CONTAINS = relations_postgresql.CONTAINS


class ALL(relations_postgresql.SQL, relations_sql.ALL):
    """
    For if the left and right have the same members
    """

    AND = AND
    CONTAINS = relations_postgresql.CONTAINS
    LENGTHS = relations_postgresql.LENGTHS


class OP(relations_postgresql.SQL, relations_sql.OP): # pylint: disable=too-few-public-methods
    """
    Determines the criterion based on operand
    """

    NOT = relations_postgresql.NOT

    CRITERIONS = {
        'null': relations_postgresql.NULL,
        'eq': relations_postgresql.EQ,
        'gt': relations_postgresql.GT,
        'gte': relations_postgresql.GTE,
        'lt': relations_postgresql.LT,
        'lte': relations_postgresql.LTE,
        'like': relations_postgresql.LIKE,
        'start': relations_postgresql.START,
        'end': relations_postgresql.END,
        'in': relations_postgresql.IN,
        'has': HAS,
        'any': ANY,
        'all': ALL
    }
