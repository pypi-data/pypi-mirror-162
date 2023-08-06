"""
Module for all MySQL SQL relations_sql.CLAUSES, pieces of Queries
"""

import relations_sql
import relations_mysql


class CLAUSE(relations_mysql.SQL, relations_sql.CLAUSE):
    """
    Base class for clauses
    """


class ARGS(relations_mysql.SQL, relations_sql.ARGS):
    """
    Clauses that never have keyword arguments
    """


class OPTIONS(relations_mysql.SQL, relations_sql.OPTIONS):
    """
    Beginning of a SELECT statement
    """

    ARGS = relations_sql.SQL


class FIELDS(relations_mysql.SQL, relations_sql.FIELDS):
    """
    FIELDS part of SELECT statement
    """

    ARGS = relations_mysql.COLUMN_NAME
    KWARG = relations_mysql.COLUMN_NAME
    KWARGS = relations_mysql.AS


class FROM(relations_mysql.SQL, relations_sql.FROM):
    """
    Clause for FROM
    """

    ARGS = relations_mysql.TABLE_NAME
    KWARG = relations_mysql.TABLE_NAME
    KWARGS = relations_mysql.AS


class WHERE(relations_mysql.SQL, relations_sql.WHERE):
    """
    Clause for WHERE
    """

    ARGS = relations_mysql.VALUE
    KWARGS = relations_mysql.OP


class GROUP_BY(relations_mysql.SQL, relations_sql.GROUP_BY):
    """
    Clasuse for GROUP BY
    """

    ARGS = relations_mysql.COLUMN_NAME


class HAVING(relations_mysql.SQL, relations_sql.HAVING):
    """
    Clause for HAVING
    """

    ARGS = relations_mysql.VALUE
    KWARGS = relations_mysql.OP


class ORDER_BY(relations_mysql.SQL, relations_sql.ORDER_BY):
    """
    Clause for the bORDER
    """

    ARGS = relations_mysql.ORDER
    KWARGS = relations_mysql.ORDER


class LIMIT(relations_mysql.SQL, relations_sql.LIMIT):
    """
    Base class for clauses
    """

    ARGS = relations_mysql.VALUE


class SET(relations_mysql.SQL, relations_sql.SET):
    """
    relations_sql.CRITERIA for SET
    """

    KWARGS = relations_mysql.ASSIGN


class VALUES(relations_mysql.SQL, relations_sql.VALUES):
    """
    relations_sql.CRITERIA for VALUES
    """

    ARGS = relations_mysql.LIST
