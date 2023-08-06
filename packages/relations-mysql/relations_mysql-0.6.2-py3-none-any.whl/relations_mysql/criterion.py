"""
Module for all Relations MySQL Criterions, pieces of Criteria
"""

import relations_sql
import relations_mysql


class CRITERION(relations_mysql.SQL):
    """
    CRITERION class, for comparing two values
    """

    LEFT = relations_mysql.COLUMN_NAME
    RIGHT = relations_mysql.VALUE


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

    RIGHT = relations_mysql.LIST
    VALUE = relations_mysql.VALUE


class CONTAINS(CRITERION, relations_sql.CONTAINS):
    """
    Wether one set contains another
    """

    RIGHT = relations_mysql.VALUE

    OPERAND = "JSON_CONTAINS(%s,%s)"


class LENGTHS(CRITERION, relations_sql.LENGTHS):
    """
    Wether one set contains another
    """

    RIGHT = relations_mysql.VALUE

    OPERAND = "JSON_LENGTH(%s)=JSON_LENGTH(%s)"
