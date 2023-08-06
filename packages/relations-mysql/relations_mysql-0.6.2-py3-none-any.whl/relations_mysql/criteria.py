"""
Module for MySQL CRITERIA
"""

import relations_sql
import relations_mysql


class CRITERIA(relations_mysql.SQL):
    """
    Collection of CRITERIONS
    """

    ARGS = relations_mysql.VALUE


class AND(CRITERIA, relations_sql.AND):
    """
    CLAUSE for AND
    """


class OR(CRITERIA, relations_sql.OR):
    """
    CLAUSE for OR
    """


class SETS(relations_mysql.SQL):
    """
    For comparing sets with each other
    """


class HAS(SETS, relations_sql.HAS):
    """
    For if the left has all the members of right
    """

    CONTAINS = relations_mysql.CONTAINS


class ANY(SETS, relations_sql.ANY):
    """
    For if the left has any the members of right
    """

    OR = OR
    LEFT = relations_mysql.COLUMN_NAME
    VALUE = relations_mysql.VALUE
    CONTAINS = relations_mysql.CONTAINS


class ALL(SETS, relations_sql.ALL):
    """
    For if the left and right have the same members
    """

    AND = AND
    CONTAINS = relations_mysql.CONTAINS
    LENGTHS = relations_mysql.LENGTHS


class OP(SETS, relations_sql.OP): # pylint: disable=too-few-public-methods
    """
    Determines the criterion based on operand
    """

    NOT = relations_mysql.NOT

    CRITERIONS = {
        'null': relations_mysql.NULL,
        'eq': relations_mysql.EQ,
        'gt': relations_mysql.GT,
        'gte': relations_mysql.GTE,
        'lt': relations_mysql.LT,
        'lte': relations_mysql.LTE,
        'like': relations_mysql.LIKE,
        'start': relations_mysql.START,
        'end': relations_mysql.END,
        'in': relations_mysql.IN,
        'has': HAS,
        'any': ANY,
        'all': ALL
    }
