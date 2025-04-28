# src/database/database.py

from PyQt6.QtSql import QSqlDatabase, QSqlQuery

from src import constants


def initialize_database():
    db = QSqlDatabase.addDatabase("QSQLITE", constants.DB_CONNECTION)
    db.setDatabaseName(constants.DB_PATH)
    if not db.open():
        raise Exception(
            f"An error occurred while opening the database: {db.lastError().text()}"
        )
    query = QSqlQuery(db)
    query.exec("PRAGMA foreign_keys = ON;")
    try:
        if not db.transaction():
            raise Exception(f"Could not start transaction.")
        sql_ignore_phone = f"""
CREATE TABLE IF NOT EXISTS {constants.TABLE_IGNORE_PHONE_NUMBER} (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    value TEXT UNIQUE NOT NULL,
    created_at TEXT DEFAULT (strftime('%Y-%m-%d %H:%M:%S', 'now'))
)
"""
        sql_ignore_uid = f"""
CREATE TABLE IF NOT EXISTS {constants.TABLE_IGNORE_UID} (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    value TEXT UNIQUE NOT NULL,
    created_at TEXT DEFAULT (strftime('%Y-%m-%d %H:%M:%S', 'now'))
)
"""
        sql_result = f"""
CREATE TABLE IF NOT EXISTS {constants.TABLE_RESULT} (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_url,
    post_content TEXT,
    created_at TEXT DEFAULT (strftime('%Y-%m-%d %H:%M:%S', 'now'))
)
"""
        if not query.exec(sql_ignore_phone):
            raise Exception(
                f"An error occurred while creating table '{constants.TABLE_IGNORE_PHONE_NUMBER}': {query.lastError().text()}."
            )
        if not query.exec(sql_ignore_uid):
            raise Exception(
                f"An error occurred while creating table '{constants.TABLE_IGNORE_UID}': {query.lastError().text()}."
            )
        if not query.exec(sql_result):
            raise Exception(
                f"An error occurred while creating table '{constants.TABLE_RESULT}': {query.lastError().text()}."
            )
        if not db.commit():
            raise Exception(
                f"Failed to commit database transaction: {db.lastError().text()}"
            )
        return True
    except Exception as e:
        if db.isValid() and db.isOpen() and db.transaction():
            db.rollback()
        raise Exception(f"Failed to initialize database: {str(e)}")
