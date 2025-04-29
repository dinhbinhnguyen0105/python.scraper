# src/models/model.py
from PyQt6.QtCore import Qt
from PyQt6.QtSql import QSqlTableModel, QSqlDatabase

import constants


class BaseModel(QSqlTableModel):
    def __init__(self, table_name, parent=None):
        super().__init__(parent, QSqlDatabase.database(constants.DB_CONNECTION))
        self.setTable(table_name)
        self.setEditStrategy(QSqlTableModel.EditStrategy.OnFieldChange)
        if not self.select():
            print(
                f"Error selecting data from table '{table_name}': {self.lastError().text()}"
            )

    def flags(self, index):
        return (
            Qt.ItemFlag.ItemIsSelectable
            | Qt.ItemFlag.ItemIsEnabled
            | Qt.ItemFlag.ItemIsEditable
        )

    def get_record_ids(self, rows):
        ids = []
        for row in rows:
            if 0 <= row <= self.rowCount():
                index = self.index(row, self.fieldIndex("id"))
                ids.append(self.data(index))
        return ids


class IgnorePhone_Model(BaseModel):
    def __init__(self, parent=None):
        super().__init__(constants.TABLE_IGNORE_PHONE_NUMBER, parent)


class IgnoreUID_Model(BaseModel):
    def __init__(self, parent=None):
        super().__init__(constants.TABLE_IGNORE_UID, parent)


class IgnoreResult_Model(BaseModel):
    def __init__(self, parent=None):
        super().__init__(constants.TABLE_RESULT, parent)
