"""
Module for all sqlite SQL relations_sql.CLAUSES, pieces of Queries
"""

import relations_sql
import relations_sqlite


class CLAUSE(relations_sqlite.SQL, relations_sql.CLAUSE):
    """
    Base class for clauses
    """


class ARGS(relations_sqlite.SQL, relations_sql.ARGS):
    """
    Clauses that never have keyword arguments
    """


class OPTIONS(relations_sqlite.SQL, relations_sql.OPTIONS):
    """
    Beginning of a SELECT statement
    """

    ARGS = relations_sql.SQL


class FIELDS(relations_sqlite.SQL, relations_sql.FIELDS):
    """
    FIELDS part of SELECT statement
    """

    ARGS = relations_sqlite.COLUMN_NAME
    KWARG = relations_sqlite.COLUMN_NAME
    KWARGS = relations_sqlite.AS


class FROM(relations_sqlite.SQL, relations_sql.FROM):
    """
    Clause for FROM
    """

    ARGS = relations_sqlite.TABLE_NAME
    KWARG = relations_sqlite.TABLE_NAME
    KWARGS = relations_sqlite.AS


class WHERE(relations_sqlite.SQL, relations_sql.WHERE):
    """
    Clause for WHERE
    """

    ARGS = relations_sqlite.VALUE
    KWARGS = relations_sqlite.OP


class GROUP_BY(relations_sqlite.SQL, relations_sql.GROUP_BY):
    """
    Clasuse for GROUP BY
    """

    ARGS = relations_sqlite.COLUMN_NAME


class HAVING(relations_sqlite.SQL, relations_sql.HAVING):
    """
    Clause for HAVING
    """

    ARGS = relations_sqlite.VALUE
    KWARGS = relations_sqlite.OP


class ORDER_BY(relations_sqlite.SQL, relations_sql.ORDER_BY):
    """
    Clause for the bORDER
    """

    ARGS = relations_sqlite.ORDER
    KWARGS = relations_sqlite.ORDER


class LIMIT(relations_sqlite.SQL, relations_sql.LIMIT):
    """
    Base class for clauses
    """

    ARGS = relations_sqlite.VALUE


class SET(relations_sqlite.SQL, relations_sql.SET):
    """
    relations_sql.CRITERIA for SET
    """

    KWARGS = relations_sqlite.ASSIGN


class VALUES(relations_sqlite.SQL, relations_sql.VALUES):
    """
    relations_sql.CRITERIA for VALUES
    """

    ARGS = relations_sqlite.LIST
