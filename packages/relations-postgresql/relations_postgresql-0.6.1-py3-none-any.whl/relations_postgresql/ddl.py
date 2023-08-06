"""
Module for all Relations SQL Definition.
"""

import relations_sql
import relations_postgresql


class DDL(relations_postgresql.SQL, relations_sql.DDL):
    """
    Base definiton
    """
