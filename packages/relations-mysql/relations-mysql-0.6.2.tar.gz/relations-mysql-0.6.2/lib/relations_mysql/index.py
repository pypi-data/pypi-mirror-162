"""–
Module for Column DDL
"""

# pylint: disable=unused-argument

import relations_sql
import relations_mysql


class INDEX(relations_mysql.DDL, relations_sql.INDEX):
    """
    INDEX DDL
    """

    TABLE = relations_mysql.TABLE_NAME
    COLUMNS = relations_mysql.COLUMN_NAMES

    CREATE = "INDEX"
    MODIFY = "RENAME INDEX %s TO %s"

    def create(self, **kwargs):
        """
        CREATE DLL
        """

        sql = []

        if "table" in self.migration:
            sql.append("ADD")

        sql.append(self.CREATE)
        sql.append(self.name(full=False))

        columns = self.COLUMNS(self.migration["columns"])
        columns.generate()
        sql.append(columns.sql)

        self.sql = " ".join(sql)

class UNIQUE(INDEX):
    """
    UNIQUE INDEX DDL
    """

    CREATE = "UNIQUE"
