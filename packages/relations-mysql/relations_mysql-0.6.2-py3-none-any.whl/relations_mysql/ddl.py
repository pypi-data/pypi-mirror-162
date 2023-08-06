"""
Module for all Relations SQL Definition.
"""

import relations_sql
import relations_mysql


class DDL(relations_mysql.SQL, relations_sql.DDL):
    """
    Base definiton
    """
