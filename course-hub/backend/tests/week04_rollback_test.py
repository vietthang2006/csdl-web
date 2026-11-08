from __future__ import annotations

import sys
from pathlib import Path

# Add backend/app to path
APP_DIR = Path(__file__).resolve().parents[1] / "app"
sys.path.insert(0, str(APP_DIR))

from fastapi import HTTPException
from sqlalchemy import text
from database import engine
from schemas import EnrollmentCreate
from main import demo_test_rollback


def run_rollback_test() -> None:
    print("=" * 60)
    print("KIEM THU ROLLBACK NHIEU BANG (BAI 2)")
    print("=" * 60)

    section_id = "RACE-01"
    test_student_id = "22000002"

    # 1. Lay so luong enrollments hien tai cua RACE-01
    count_sql = """
        SELECT COUNT(*) FROM enrollments WHERE class_section_id = :class_section_id
    """
    check_student_sql = """
        SELECT 1 FROM enrollments
        WHERE student_id = :student_id AND class_section_id = :class_section_id
    """
    check_event_sql = """
        SELECT COUNT(*) FROM enrollment_events
        WHERE event_type = 'INVALID_TYPE'
    """

    with engine.connect() as conn:
        count_before = conn.execute(
            text(count_sql), {"class_section_id": section_id}
        ).scalar_one()

    print(f"[*] So luong enrollments ban dau cua lop {section_id}: {count_before}")

    # 2. Goi endpoint demo co y gay loi o buoc 2
    payload = EnrollmentCreate(student_id=test_student_id, class_section_id=section_id)
    rollback_occurred = False

    try:
        demo_test_rollback(payload)
    except HTTPException as exc:
        if exc.status_code == 409:
            rollback_occurred = True
            print(f"[+] Endpoint nem HTTPException 409 dung mong doi: {exc.detail}")
        else:
            raise

    assert rollback_occurred, "Transaction phai nem HTTPException 409 do vi pham constraint"

    # 3. Kiem tra lai so luong enrollments sau khi rollback
    with engine.connect() as conn:
        count_after = conn.execute(
            text(count_sql), {"class_section_id": section_id}
        ).scalar_one()
        student_enrolled = conn.execute(
            text(check_student_sql),
            {"student_id": test_student_id, "class_section_id": section_id},
        ).first()
        invalid_events_count = conn.execute(text(check_event_sql)).scalar_one()

    print(f"[*] So luong enrollments sau rollback cua lop {section_id}: {count_after}")
    assert count_after == count_before, (
        f"Loi: So luong enrollments bi thay doi! Truoc: {count_before}, Sau: {count_after}"
    )
    assert student_enrolled is None, (
        f"Loi: Sinh vien {test_student_id} van bi luu vao enrollments mac du buoc 2 loi!"
    )
    assert invalid_events_count == 0, (
        "Loi: Su kien loi bi luu vao enrollment_events!"
    )

    print("-" * 60)
    print("XAC NHAN: Transaction da ROLLBACK thanh cong!")
    print(f"- Bang enrollments khong tang dong nao ({count_before} == {count_after}).")
    print(f"- Sinh vien {test_student_id} khong ton tai trong lop {section_id}.")
    print("- Bang enrollment_events khong chua su kien rac.")
    print("PASS: Atomicity duoc bao toan toan ven khi co loi giua transaction.")
    print("=" * 60)


if __name__ == "__main__":
    run_rollback_test()
