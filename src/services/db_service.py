from typing import List, Any, Dict
from contextlib import contextmanager
from PyQt6.QtSql import QSqlQuery, QSqlDatabase

from src import constants

# from src.my_types import IgnoreType, ResultType
from src.database.database import initialize_database


@contextmanager
def transaction(db: QSqlDatabase):
    """Context manager for database transactions with automatic rollback on exception."""
    if not db.transaction():
        print("[DB_TRANSACTION] Failed to start transaction.")
        raise RuntimeError("Failed to start transaction")
    try:
        yield
        if not db.commit():
            print("[DB_TRANSACTION] Failed to commit transaction.")
            raise RuntimeError("Failed to commit transaction")
    except Exception:
        if db.isOpen():
            db.rollback()
        raise


class BaseService:
    TABLE_NAME: str = ""

    @classmethod
    def get_db(cls) -> QSqlDatabase:
        return QSqlDatabase.database(constants.DB_CONNECTION)

    @classmethod
    def get_columns(cls) -> List[str]:
        raise NotImplementedError("get_columns() must be implemented by subclass.")

    @classmethod
    def _exec_query(cls, query: QSqlQuery) -> bool:
        if not query.exec():
            error = query.lastError().text()
            sql = query.lastQuery()
            print(f"[QUERY_EXECUTION] Error on {cls.TABLE_NAME}: {error} -- SQL: {sql}")
            return False
        return True

    @classmethod
    def _convert_record_to_dict(cls, query: QSqlQuery) -> Dict[str, Any]:
        record = query.record()
        return {record.fieldName(i): record.value(i) for i in range(record.count())}

    @classmethod
    def read(cls, record_id: int) -> Dict[str, Any] | None:
        db = cls.get_db()
        query = QSqlQuery(db)
        sql = f"SELECT * FROM {cls.TABLE_NAME} WHERE id = :id"
        if not query.prepare(sql):
            print(f"[READ] Prepare failed: {query.lastError().text()}")
            return None
        query.bindValue(":id", record_id)
        if not cls._exec_query(query):
            return None
        if query.next():
            return cls._convert_record_to_dict(query)
        print(f"[READ] No record with id={record_id} in {cls.TABLE_NAME}.")
        return None

    @classmethod
    def read_all(cls) -> List[Dict[str, Any]]:
        db = cls.get_db()
        query = QSqlQuery(db)
        sql = f"SELECT * FROM {cls.TABLE_NAME}"
        if not query.prepare(sql):
            print(f"[READ_ALL] Prepare failed: {query.lastError().text()}")
            return []
        if not cls._exec_query(query):
            return False
        results = []
        while query.next():
            results.append(cls._convert_record_to_dict(query))
        print(f"[READ_ALL] Retrieved {len(results)} from {cls.TABLE_NAME}.")
        return results

    @classmethod
    def create(cls, payload: Dict[str, Any]) -> bool:
        db = cls.get_db()
        valid_cols = [c for c in cls.get_columns() if c in payload]
        if not valid_cols:
            print(f"[CREATE] No valid columns for {cls.TABLE_NAME}: {payload}")
            return False
        cols = ", ".join(valid_cols)
        placeholders = ", ".join(f":{c}" for c in valid_cols)
        sql = f"INSERT INTO {cls.TABLE_NAME} ({cols}) VALUES ({placeholders})"
        query = QSqlQuery(db)
        if not query.prepare(sql):
            print(f"[CREATE] Prepare failed: {query.lastError().text()}")
            return False
        for col in valid_cols:
            query.bindValue(f":{col}", payload[col])
        with transaction(db):
            if not cls._exec_query(query):
                return False
        print(f"[CREATE] Inserted into {cls.TABLE_NAME}: {payload}")
        return True

    @classmethod
    def update(cls, record_id: Any, payload: Dict[str, Any]) -> bool:
        db = cls.get_db()
        valid_cols = [c for c in cls.get_columns() if c in payload]
        if not valid_cols:
            print(f"[UPDATE] No valid columns for {cls.TABLE_NAME}: {payload}")
            return False
        set_clause = ", ".join(f"{c} = :{c}" for c in valid_cols)
        sql = f"UPDATE {cls.TABLE_NAME} SET {set_clause} WHERE id = :id"
        query = QSqlQuery(db)
        if not query.prepare(sql):
            print(f"[UPDATE] Prepare failed: {query.lastError().text()}")
            return False
        query.bindValue(":id", record_id)
        for col in valid_cols:
            query.bindValue(f":{col}", payload[col])
        with transaction(db):
            if not cls._exec_query(query):
                return False
        print(f"[UPDATE] Updated id={record_id} in {cls.TABLE_NAME}: {payload}")
        return True

    @classmethod
    def delete(cls, record_id: Any) -> bool:
        db = cls.get_db()
        query = QSqlQuery(db)
        sql = f"DELETE FROM {cls.TABLE_NAME} WHERE id = :id"
        if not query.prepare(sql):
            print(f"[DELETE] Prepare failed: {query.lastError().text()}")
            return False
        query.bindValue(":id", record_id)
        with transaction(db):
            if not cls._exec_query(query):
                return False
        print(f"[DELETE] Deleted id={record_id} from {cls.TABLE_NAME}.")
        return True

    @classmethod
    def is_field_value_exists(cls, value: Any) -> bool:
        db = cls.get_db()
        query = QSqlQuery(db)
        sql = f"SELECT 1 FROM {cls.TABLE_NAME} WHERE value = ? LIMIT 1"
        if not query.prepare(sql):
            print(f"[VALUE_EXISTS] Prepare failed: {query.lastError().text()}")
            return False
        query.addBindValue(value)
        if not query.exec():
            print(f"[VALUE_EXISTS] Exec failed: {query.lastError().text()}")
            query.finish()
            return False
        exists = query.next()
        query.finish()
        return exists

    @classmethod
    def import_data(cls, payload: List[Dict[str, Any]]) -> bool:
        if not payload:
            print(f"[IMPORT_DATA] Empty payload for {cls.TABLE_NAME}.")
            return False
        db = cls.get_db()
        with transaction(db):
            for record in payload:
                val = record.get("value")
                if val and cls.is_field_value_exists(val):
                    print(f"[IMPORT_DATA] Skip duplicate value: {val}")
                    continue
                valid_cols = [c for c in cls.get_columns() if c in record]
                cols = ", ".join(valid_cols)
                placeholders = ", ".join(f":{c}" for c in valid_cols)
                sql = f"INSERT INTO {cls.TABLE_NAME} ({cols}) VALUES ({placeholders})"
                query = QSqlQuery(db)
                query.prepare(sql)
                for col in valid_cols:
                    query.bindValue(f":{col}", record[col])
                if not cls._exec_query(query):
                    raise RuntimeError(f"Failed to import record: {record}")
        print(f"[IMPORT_DATA] Imported {len(payload)} into {cls.TABLE_NAME}.")
        return True


class IgnorePhoneService(BaseService):
    TABLE_NAME = constants.TABLE_IGNORE_PHONE_NUMBER

    @classmethod
    def get_columns(cls) -> List[str]:
        return ["id", "value", "created_at"]


class IgnoreUIDService(BaseService):
    TABLE_NAME = constants.TABLE_IGNORE_UID

    @classmethod
    def get_columns(cls) -> List[str]:
        return ["id", "value", "created_at"]


class ResultService(BaseService):
    TABLE_NAME = constants.TABLE_RESULT

    @classmethod
    def get_columns(cls) -> List[str]:
        return ["id", "post_url", "post_content", "created_at"]


def main():
    import sys, json
    from PyQt6.QtWidgets import QApplication

    app = QApplication([])
    print("— Khởi tạo database …")
    if initialize_database():
        print("✅ Database đã khởi tạo/kiểm tra thành công.\n")
        print("Prepare import ignore phone")
        # phone_payload = [
        #     {"value": "0123456789"},
        #     {"value": "0987654321"},
        #     {"value": "0909406001"},
        #     {"value": "0123456789"},  # giá trị trùng sẽ bị skip
        # ]
        # is_import = IgnorePhoneService.import_data(phone_payload)
        # if is_import:
        #     print("✅ Import thành công.\n")
        # /Volumes/KINGSTON/Dev/python/scraper/repositories/ignorePhoneNumber.json
        # /Volumes/KINGSTON/Dev/python/scraper/repositories/ignoreUID.json
        # with open(
        #     "/Volumes/KINGSTON/Dev/python/scraper/repositories/ignorePhoneNumber.json",
        #     encoding="utf8",
        # ) as f:
        #     payload = []
        #     data = json.load(f)
        #     for phone_number in data:
        #         payload.append({"value": phone_number})
        #     is_import = IgnorePhoneService.import_data(payload)
        #     if is_import:
        #         print("✅ Import thành công.\n")

        with open(
            "/Volumes/KINGSTON/Dev/python/scraper/repositories/ignoreUID.json",
            encoding="utf8",
        ) as f:
            data = json.load(f)
            payload = []
            for uid in data:
                payload.append({"value": uid})
            is_import = IgnoreUIDService.import_data(payload)
            if is_import:
                print("✅ Import thành công.\n")

    else:
        print("❎ Database đã khởi tạo/kiểm tra thất bại.\n")


if __name__ == "__main__":

    main()
