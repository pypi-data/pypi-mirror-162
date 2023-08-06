"""
Module for all Relations SQL Definition.
"""

import relations_sql
import relations_sqlite


class DDL(relations_sqlite.SQL, relations_sql.DDL):
    """
    Base definiton
    """
