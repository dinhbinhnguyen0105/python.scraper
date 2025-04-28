# src/scripts/init_and_test_db.py

import os
import sys
from PyQt6.QtWidgets import QApplication

# Thêm đường dẫn src vào sys.path nếu cần
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.database.database import initialize_database
from src.services.db_service import (
    IgnorePhoneService,
    IgnoreUIDService,
    ResultService,
)


def main():
    app = QApplication([])
    # 1. Khởi tạo database (nếu đã tồn tại, sẽ giữ nguyên schema)
    print("— Khởi tạo database …")
    initialize_database()
    print("✓ Database đã khởi tạo/kiểm tra thành công.\n")

    # 2. Seed data mẫu cho IgnorePhoneService
    print("— Thêm dữ liệu mẫu cho IgnorePhoneService …")
    phone_payload = [
        {"value": "0123456789"},
        {"value": "0987654321"},
        {"value": "0123456789"},  # giá trị trùng sẽ bị skip
    ]
    ok = IgnorePhoneService.import_data(phone_payload)
    print(f"import_data returned: {ok}")
    print("Dữ liệu hiện có:", IgnorePhoneService.read_all(), "\n")

    # 3. Test CRUD với IgnoreUIDService
    print("— Test CRUD với IgnoreUIDService …")
    # Create
    created = IgnoreUIDService.create({"value": "UID_ABC123"})
    print("create ->", created)
    # Read All
    all_uids = IgnoreUIDService.read_all()
    print("read_all ->", all_uids)
    # Read single
    if all_uids:
        rec_id = all_uids[0]["id"]
        single = IgnoreUIDService.read(rec_id)
        print(f"read(id={rec_id}) ->", single)
        # Update
        updated = IgnoreUIDService.update(rec_id, {"value": "UID_XYZ789"})
        print(f"update(id={rec_id}) ->", updated)
        print("read_all sau update ->", IgnoreUIDService.read_all())
        # Delete
        deleted = IgnoreUIDService.delete(rec_id)
        print(f"delete(id={rec_id}) ->", deleted)
        print("read_all sau delete ->", IgnoreUIDService.read_all())
    print()

    # 4. Seed và test ResultService
    print("— Thêm và test ResultService …")
    result_payload = [
        {"post_url": "http://example.com/1", "post_content": "Nội dung bài 1"},
        {"post_url": "http://example.com/2", "post_content": "Nội dung bài 2"},
    ]
    ok2 = ResultService.import_data(result_payload)
    print(f"import_data returned: {ok2}")
    all_results = ResultService.read_all()
    print("read_all ->", all_results)
    # Update nội dung bài 2
    rec = next((r for r in all_results if r["post_url"].endswith("/2")), None)
    if rec:
        rid = rec["id"]
        ok3 = ResultService.update(rid, {"post_content": "Nội dung mới bài 2"})
        print(f"update id={rid} ->", ok3)
        print("read(id) ->", ResultService.read(rid))
    print()

    print("✅ Tất cả tests đã hoàn tất.")


if __name__ == "__main__":
    main()
