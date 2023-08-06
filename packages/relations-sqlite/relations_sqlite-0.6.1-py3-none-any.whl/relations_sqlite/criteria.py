"""
Module for sqlite CRITERIA
"""

import relations_sql
import relations_sqlite


class CRITERIA(relations_sqlite.SQL):
    """
    Collection of CRITERIONS
    """

    ARGS = relations_sqlite.VALUE


class AND(CRITERIA, relations_sql.AND):
    """
    CLAUSE for AND
    """


class OR(CRITERIA, relations_sql.OR):
    """
    CLAUSE for OR
    """


class SETS(relations_sqlite.SQL):
    """
    For comparing sets with each other
    """


class HAS(SETS, relations_sql.HAS):
    """
    For if the left has all the members of right
    """

    CONTAINS = relations_sqlite.CONTAINS


class ANY(SETS, relations_sql.ANY):
    """
    For if the left has any the members of right
    """

    OR = OR
    LEFT = relations_sqlite.COLUMN_NAME
    VALUE = relations_sqlite.VALUE
    CONTAINS = relations_sqlite.CONTAINS


class ALL(SETS, relations_sql.ALL):
    """
    For if the left and right have the same members
    """

    AND = AND
    CONTAINS = relations_sqlite.CONTAINS
    LENGTHS = relations_sqlite.LENGTHS


class OP(SETS, relations_sql.OP): # pylint: disable=too-few-public-methods
    """
    Determines the criterion based on operand
    """

    NOT = relations_sqlite.NOT

    CRITERIONS = {
        'null': relations_sqlite.NULL,
        'eq': relations_sqlite.EQ,
        'gt': relations_sqlite.GT,
        'gte': relations_sqlite.GTE,
        'lt': relations_sqlite.LT,
        'lte': relations_sqlite.LTE,
        'like': relations_sqlite.LIKE,
        'start': relations_sqlite.START,
        'end': relations_sqlite.END,
        'in': relations_sqlite.IN,
        'has': HAS,
        'any': ANY,
        'all': ALL
    }
