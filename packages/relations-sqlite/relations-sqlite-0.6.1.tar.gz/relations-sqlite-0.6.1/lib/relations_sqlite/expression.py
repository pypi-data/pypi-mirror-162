"""
Module for all Relations sqlite Expressions. pieces of criterions, criteria, and statements
"""

import relations_sql
import relations_sqlite


class EXPRESSION(relations_sqlite.SQL, relations_sql.EXPRESSION):
    """
    Base class for expressions
    """


class VALUE(relations_sqlite.SQL, relations_sql.VALUE):
    """
    Class for storing a value that will need to be escaped
    """


class NOT(relations_sqlite.SQL, relations_sql.NOT):
    """
    Negation
    """

    VALUE = VALUE

    OPERAND = "NOT %s"


class LIST(relations_sqlite.SQL, relations_sql.LIST):
    """
    Holds a list of values for IN, NOT IN, and VALUES
    """

    ARG = VALUE


class NAME(relations_sqlite.SQL, relations_sql.NAME):
    """
    For anything that needs to be quote
    """


class SCHEMA_NAME(relations_sqlite.SQL, relations_sql.SCHEMA_NAME):
    """
    For schemas
    """


class TABLE_NAME(relations_sqlite.SQL, relations_sql.TABLE_NAME):
    """
    For tables
    """

    SCHEMA_NAME = SCHEMA_NAME


class COLUMN_NAME(relations_sqlite.SQL, relations_sql.COLUMN_NAME):
    """
    Class for storing a column that'll be used as a field
    """

    TABLE_NAME = TABLE_NAME


class NAMES(relations_sqlite.SQL, relations_sql.NAMES):
    """
    Holds a list of field names only, with table
    """

    ARG = NAME


class COLUMN_NAMES(relations_sqlite.SQL, relations_sql.COLUMN_NAMES):
    """
    Holds a list of column names only, with table
    """

    ARG = COLUMN_NAME


class AS(relations_sqlite.SQL, relations_sql.AS):
    """
    For AS pairings
    """

    NAME = NAME


ASC = relations_sql.ASC
DESC = relations_sql.DESC

class ORDER(relations_sqlite.SQL, relations_sql.ORDER):
    """
    For anything that needs to be ordered
    """

    EXPRESSION = COLUMN_NAME

    ORDER = {
        ASC: "ASC",
        DESC: "DESC"
    }


class ASSIGN(relations_sqlite.SQL, relations_sql.ASSIGN):
    """
    For SET pairings
    """

    COLUMN_NAME = COLUMN_NAME
    EXPRESSION = VALUE
