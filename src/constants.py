# src/constants.py
import os
import sys

# Lấy đường dẫn thư mục chứa tệp thực thi hoặc mã nguồn
BASE_DIR = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))

# Đường dẫn tuyệt đối đến tệp cơ sở dữ liệu
DB_PATH = os.path.join(BASE_DIR, "repositories", "db", "database.db")
# DB_PATH = "/Users/ndb/Dev/python/python.scraper/repositories/db/database.db"
DB_CONNECTION = "database_connection"
TABLE_IGNORE_PHONE_NUMBER = "table_ignore_phone_number"
TABLE_IGNORE_UID = "table_ignore_uid"
TABLE_RESULT = "table_result"

SCRAPING = "scraping"
LAUNCHING = "launching"
