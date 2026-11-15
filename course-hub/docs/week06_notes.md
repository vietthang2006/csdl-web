# Buổi 6 - Docker, Testing, CI

## Môi trường
- OS: Windows 11 (`Microsoft Windows NT 10.0.26200.0`)
- Docker version: `Docker version 29.6.2, build dfc4efb`
- Python / Node version: Python `3.13.9` (`.venv` local) / `3.12` (CI); Node `v26.13.0` (local) / `22.12.0` (CI)

## Kết quả local
- `python -m pytest backend/tests -q`: **3 passed** (trong `1.04s`) — kiểm tra đủ `REQUIRED_PATHS`, method `post`/`delete` của `/enrollments` và method `get` của `/sections`.
- `npm test` (`node --test tests/api.test.mjs`): **7/7 pass** (mock `fetch` kiểm tra GET 200 JSON, POST JSON, DELETE 204, HTTP error string/array detail, phản hồi non-JSON, lỗi mạng & `AbortError`).
- `npm run build` (`vite build`): **Pass** (31 modules transformed, xuất `dist/` trong `~635ms`).
- `docker compose up --build`: `docker compose config` hợp lệ; build thành công cả 2 image `course-hub-backend` và `course-hub-frontend`. 

## Debug / AI
- Lỗi gặp phải:
  1. `ModuleNotFoundError: No module named 'database'` khi chạy container backend (do `Dockerfile` chạy `backend.app.main:app` từ `/app` nhưng `main.py` import phẳng `from database`), kèm file `backend/.env.docker` lúc đầu bị trống.
  2. `Bind for 0.0.0.0:8000 failed: port is already allocated` khi chạy `docker compose up --build`.
  3. `npm ci` lần đầu trên Windows báo `EPERM: operation not permitted, unlink ... rollup.win32-x64-msvc.node` do khóa file tạm thời (chạy lại lần 2 thành công).
  4. `pytest backend/tests -q` trên local gọi nhầm `pytest` của Anaconda và thiếu `sys.path` nên báo `No module named 'backend'`.
  5. GitHub Actions ban đầu không chạy do `.github/workflows/ci.yml` đặt nhầm trong `course-hub/`, và khi chạy PR bị `ImportError` ở `backend/tests/week04_rollback_test.py` (file cũ từ nhánh `main`).
- Bằng chứng đã xem:
  - Traceback Uvicorn trong container `backend-1`, kết quả `docker ps` cho thấy container `coursehub-backend-test` đang giữ cổng `8000`.
  - Kết quả `git rev-parse --show-toplevel` (`E:/CSDL_WEB`) và log lỗi step `Test backend contract` trên GitHub Actions.
- Nếu dùng AI: gợi ý nào đã dùng và đã xác minh thế nào?
  - Đã dùng gợi ý sửa `main.py` sang relative import (`from .database`, `from .schemas`), điền đủ biến môi trường vào `backend/.env.docker`, tắt container `coursehub-backend-test` bằng `docker stop`, tạo `frontend/tests/api.test.mjs`, chuyển `ci.yml` ra `E:\CSDL_WEB\.github\workflows\ci.yml` kèm `working-directory: course-hub`, biến môi trường `env:` cho `database.py` và chạy `python -m pytest backend/tests/test_openapi_contract.py -q`.
  - Xác minh lại toàn bộ bằng các lệnh chạy trực tiếp ở local (`python -m pytest`, `npm test`, `npm run build`) và theo dõi kết quả trên GitHub Actions.
  - Ở bài 2: khi cố tình sửa lại DB name trong .env.docker và `docker compose up`, chương trình báo ko kết nối được đến serve.

```
backend-1  | - host: 'localhost', port: 5432, hostaddr: '127.0.0.1': connection failed: connection to server at "127.0.0.1", port 5432 failed: Connection refused
```


## Pull Request / CI
- PR: Nhánh `week06-docker-ci` -> `main`
- CI run:
  - Lần chạy cũ bị **fail** do sai vị trí `.github/workflows/ci.yml` và lỗi collect file `week04_rollback_test.py` khi merge PR với `main` (đã sửa ở commit `5bf1e74`, `b63f874`).
  - Thử nghiệm Bài 1 (CI đỏ -> CI xanh):
    - Commit `8a41495` (`test: intentionally break GET /sections assertions to verify red CI`): **Fail (đỏ)** đúng như mong đợi ở job `backend`.
    - Commit `e1dbfde` (`test: restore GET /sections OpenAPI contract assertion`): khôi phục assertion `assert "get" in paths["/sections"]` → **Pass (xanh)** 
