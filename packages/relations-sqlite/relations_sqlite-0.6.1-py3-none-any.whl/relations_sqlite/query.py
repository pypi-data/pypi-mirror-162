"""
Module for all Relations sqlite Queries.
"""

import collections

import relations_sql
import relations_sqlite

class QUERY(relations_sqlite.SQL, relations_sql.CLAUSE):
    """
    Base query
    """


class SELECT(relations_sqlite.SQL, relations_sql.SELECT):
    """
    SELECT
    """

    CLAUSES = collections.OrderedDict([
        ("OPTIONS", relations_sqlite.OPTIONS),
        ("FIELDS", relations_sqlite.FIELDS),
        ("FROM", relations_sqlite.FROM),
        ("WHERE", relations_sqlite.WHERE),
        ("GROUP_BY", relations_sqlite.GROUP_BY),
        ("HAVING", relations_sqlite.HAVING),
        ("ORDER_BY", relations_sqlite.ORDER_BY),
        ("LIMIT", relations_sqlite.LIMIT)
    ])


class INSERT(relations_sqlite.SQL, relations_sql.INSERT):
    """
    INSERT query
    """

    CLAUSES = collections.OrderedDict([
        ("OPTIONS", relations_sqlite.OPTIONS),
        ("TABLE", relations_sqlite.TABLE_NAME),
        ("COLUMNS", relations_sqlite.COLUMN_NAMES),
        ("VALUES", relations_sqlite.VALUES),
        ("SELECT", SELECT)
    ])


class LIMITED(relations_sqlite.SQL, relations_sql.LIMITED):
    """
    Clause that has a limit
    """


class UPDATE(relations_sqlite.SQL, relations_sql.UPDATE):
    """
    UPDATE query
    """

    CLAUSES = collections.OrderedDict([
        ("OPTIONS", relations_sqlite.OPTIONS),
        ("TABLE", relations_sqlite.TABLE_NAME),
        ("SET", relations_sqlite.SET),
        ("WHERE", relations_sqlite.WHERE),
        ("ORDER_BY", relations_sqlite.ORDER_BY),
        ("LIMIT", relations_sqlite.LIMIT)
    ])


class DELETE(relations_sqlite.SQL, relations_sql.DELETE):
    """
    DELETE query
    """

    CLAUSES = collections.OrderedDict([
        ("OPTIONS", relations_sqlite.OPTIONS),
        ("TABLE", relations_sqlite.TABLE_NAME),
        ("WHERE", relations_sqlite.WHERE),
        ("ORDER_BY", relations_sqlite.ORDER_BY),
        ("LIMIT", relations_sqlite.LIMIT)
    ])
