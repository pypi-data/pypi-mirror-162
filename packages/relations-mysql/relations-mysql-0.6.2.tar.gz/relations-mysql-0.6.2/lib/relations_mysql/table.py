"""–
Module for Column DDL
"""

# pylint: disable=unused-argument

import relations_sql
import relations_mysql


class TABLE(relations_mysql.DDL, relations_sql.TABLE):
    """
    TABLE DDL
    """

    NAME = relations_mysql.TABLE_NAME
    COLUMN = relations_mysql.COLUMN
    INDEX = relations_mysql.INDEX
    UNIQUE = relations_mysql.UNIQUE

    INDEXES = True

    STORE = """RENAME TABLE %s TO %s"""
    PRIMARY = """PRIMARY KEY (%s)"""

    def schema(self, sql):
        """
        Change the schema
        """

        sql.append(self.STORE % (self.name(state="definition"), self.name()))

    def store(self, sql):
        """
        Change the store
        """

        if "schema" not in self.migration:
            self.schema(sql)
