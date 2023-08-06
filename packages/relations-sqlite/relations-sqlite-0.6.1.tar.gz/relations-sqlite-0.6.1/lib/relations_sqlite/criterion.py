"""
Module for all Relations sqlite Criterions, pieces of Criteria
"""

import relations_sql
import relations_sqlite


class CRITERION(relations_sqlite.SQL):
    """
    CRITERION class, for comparing two values
    """

    LEFT = relations_sqlite.COLUMN_NAME
    RIGHT = relations_sqlite.VALUE


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


class LIKE(CRITERION, relations_sql.LIKE):
    """
    For fuzzy matching
    """


class START(CRITERION, relations_sql.START):
    """
    For fuzzy matching end of string
    """


class END(CRITERION, relations_sql.END):
    """
    For fuzzy matching end of string
    """


class IN(CRITERION, relations_sql.IN):
    """
    For IN
    """

    RIGHT = relations_sqlite.LIST
    VALUE = relations_sqlite.VALUE


class CONTAINS(CRITERION, relations_sql.CONTAINS):
    """
    Wether one set contains another
    """

    RIGHT = relations_sqlite.VALUE

    INVERT = "(SELECT COUNT(*) FROM json_each(%s) as l LEFT JOIN json_each(%s) as r ON l.value=r.value WHERE r.value IS NULL)"
    OPERAND = "(NOT %s)" % INVERT

    REVERSE = True


class LENGTHS(CRITERION, relations_sql.LENGTHS):
    """
    Wether one set contains another
    """

    RIGHT = relations_sqlite.VALUE

    OPERAND = "json_array_length(%s)=json_array_length(%s)"
