print("CourseHub - Buoi 1")

students = [
    {"id": "22000001", "name": "Nguyen Minh Anh", "major": "KHDL"},
    {"id": "22000002", "name": "Tran Duc Long", "major": "KHDL"},
    {"id": "22000003", "name": "Pham Viet Thang", "major": "KHDL"}
]

courses = [
    {
        "code": "INT2204",
        "name": "Co so du lieu Web va he thong thong tin",
        "capacity": 3,
        "enrolled": 2,
    },
    {
        "code": "INT2205",
        "name": "Khai pha du lieu",
        "capacity": 2,
        "enrolled": 2,
    },
    {
        "code": "CS229",
        "name": "Hoc may",
        "capacity": 4,
        "enrolled": 2,
    },
]

enrollments = [
    {"student_id": "22000001", "course_code": "INT2204"}
]

for course in courses:
    remaining = course["capacity"] - course["enrolled"]
    print(course["code"], "- con", remaining, "cho")

def find_course(course_code):
    for course in courses:
        if course["code"] == course_code:
            return course
    return None

print(find_course("INT2204"))

def can_enroll(student_id, course_code):
    course = find_course(course_code)
    if course is None:
        return False, "Hoc phan khong ton tai"
    
    if course["enrolled"] >= course["capacity"]:
        return False, "Lop da du so luong"
    
    duplicated = any(
        item["student_id"] == student_id and item["course_code"] == course_code
        for item in enrollments
    )

    if duplicated:
        return False, "Sinh vien da dang ky hoc phan nay"
    return True, "Co the dang ky"

print(can_enroll("22000002", "INT2204"))

try:
    limit = int(input("Nhap so luong hoc phan muon hien thi: "))
    print(courses[:limit])
except ValueError:
    print("So luong phai la so nguyen")

def search_courses(keyword):
    normalized = keyword.strip().lower()
    results = []

    for course in courses:
        code = course['code'].lower()
        name = course['name'].lower()
        if normalized in code or normalized in name:
            results.append(course)

    return results

print(search_courses('web'))


#1. Hoàn thiện hàm đăng kí học phần
def enroll_student(student_id, course_code):
    """
    Kiểm tra sinh viên tồn tại, học phần tồn tại, lớp còn chỗ và sinh viên chưa đăng kí trùng
    """
    if student_id not in [student['id'] for student in students]:
        return False, "Sinh viên không tồn tại"
    able_enroll, message = can_enroll(student_id=student_id, course_code=course_code)
    if able_enroll:
        enrollments.append({
            "student_id": student_id,
            "course_code": course_code
        })
        course = find_course(course_code=course_code)
        if course:
            course['enrolled'] += 1
        return able_enroll, "Dang ki thanh cong"

    return able_enroll, message
    

#2. Tạo tổi thiểu 5 tình huống chạy thử:
# Mã sinh viên không tồn tại
print(enroll_student("24001702", "MAT2303"))

# Mã học phần không tồn tại
print(enroll_student("22000003", "CS330"))

# Đăng kí lớp trùng
print(enroll_student("22000001", "INT2204"))

# Lớp đầy
print(enroll_student("22000001", "INT2205"))

# Đăng kí thành công
print(enroll_student("22000003", "INT2204"))

# Lớp đầy
print(enroll_student("22000002", "INT2204"))

"""
Mô tả: 
(False, 'Sinh viên không tồn tại')
(False, 'Hoc phan khong ton tai')
(False, 'Sinh vien da dang ky hoc phan nay')
(False, 'Lop da du so luong')
(True, 'Dang ki thanh cong')
(False, 'Lop da du so luong')
"""

#3. Lưu thay đổi bằng Git/GitHub