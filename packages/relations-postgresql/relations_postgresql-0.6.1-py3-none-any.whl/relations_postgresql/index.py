"""–
Module for Column DDL
"""

# pylint: disable=unused-argument

import relations_sql
import relations_postgresql


class INDEX(relations_postgresql.DDL, relations_sql.INDEX):
    """
    INDEX DDL
    """

    TABLE = relations_postgresql.TABLE_NAME
    COLUMNS = relations_postgresql.COLUMN_NAMES

    CREATE = "INDEX"
    MODIFY = "ALTER INDEX %s RENAME TO %s"

    def modify(self, **kwargs):
        """
        MODIFY DLL
        """

        self.sql = self.MODIFY % (self.name(definition=True), self.name(full=False))

class UNIQUE(INDEX):
    """
    UNIQUE INDEX DDL
    """

    CREATE = "UNIQUE INDEX"
