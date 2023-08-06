"""
Module for all Relations MySQL Queries.
"""

import collections

import relations_sql
import relations_mysql

class QUERY(relations_mysql.SQL, relations_sql.CLAUSE):
    """
    Base query
    """


class SELECT(relations_mysql.SQL, relations_sql.SELECT):
    """
    SELECT
    """

    CLAUSES = collections.OrderedDict([
        ("OPTIONS", relations_mysql.OPTIONS),
        ("FIELDS", relations_mysql.FIELDS),
        ("FROM", relations_mysql.FROM),
        ("WHERE", relations_mysql.WHERE),
        ("GROUP_BY", relations_mysql.GROUP_BY),
        ("HAVING", relations_mysql.HAVING),
        ("ORDER_BY", relations_mysql.ORDER_BY),
        ("LIMIT", relations_mysql.LIMIT)
    ])


class INSERT(relations_mysql.SQL, relations_sql.INSERT):
    """
    INSERT query
    """

    CLAUSES = collections.OrderedDict([
        ("OPTIONS", relations_mysql.OPTIONS),
        ("TABLE", relations_mysql.TABLE_NAME),
        ("COLUMNS", relations_mysql.COLUMN_NAMES),
        ("VALUES", relations_mysql.VALUES),
        ("SELECT", SELECT)
    ])


class LIMITED(relations_mysql.SQL, relations_sql.LIMITED):
    """
    Clause that has a limit
    """


class UPDATE(relations_mysql.SQL, relations_sql.UPDATE):
    """
    UPDATE query
    """

    CLAUSES = collections.OrderedDict([
        ("OPTIONS", relations_mysql.OPTIONS),
        ("TABLE", relations_mysql.TABLE_NAME),
        ("SET", relations_mysql.SET),
        ("WHERE", relations_mysql.WHERE),
        ("ORDER_BY", relations_mysql.ORDER_BY),
        ("LIMIT", relations_mysql.LIMIT)
    ])


class DELETE(relations_mysql.SQL, relations_sql.DELETE):
    """
    DELETE query
    """

    CLAUSES = collections.OrderedDict([
        ("OPTIONS", relations_mysql.OPTIONS),
        ("TABLE", relations_mysql.TABLE_NAME),
        ("WHERE", relations_mysql.WHERE),
        ("ORDER_BY", relations_mysql.ORDER_BY),
        ("LIMIT", relations_mysql.LIMIT)
    ])
