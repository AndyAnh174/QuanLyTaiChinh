# Testing Guide - Playwright UI Tests

## Prerequisites

1. **Django server phải đang chạy**:

   ```bash
   C:\Users\ADMIN\anaconda3\envs\taichinh\python.exe manage.py runserver 8000
   ```

2. **Access code đã được set**:

   ```bash
   C:\Users\ADMIN\anaconda3\envs\taichinh\python.exe manage.py init_access_code 1234
   ```

3. **Playwright browsers đã cài đặt**:
   ```bash
   C:\Users\ADMIN\anaconda3\envs\taichinh\python.exe -m playwright install chromium
   ```

## Chạy Tests

### Cách 1: Sử dụng batch file (đơn giản nhất)

```bash
# Chạy headless (mặc định)
run_tests.bat

# Chạy với browser hiển thị
run_tests.bat headed

# Chạy chậm để xem browser hoạt động
run_tests.bat slow
```

### Cách 2: Chạy trực tiếp với pytest

```bash
# Headless (mặc định)
C:\Users\ADMIN\anaconda3\envs\taichinh\python.exe -m pytest tests/ -p no:django -v

# Với browser hiển thị
C:\Users\ADMIN\anaconda3\envs\taichinh\python.exe -m pytest tests/ --headed -p no:django -v

# Chạy test cụ thể
C:\Users\ADMIN\anaconda3\envs\taichinh\python.exe -m pytest tests/test_ui_access_code.py -p no:django -v

# Slow motion (500ms delay)
C:\Users\ADMIN\anaconda3\envs\taichinh\python.exe -m pytest tests/ --headed --slowmo=500 -p no:django -v
```

## Test Files

### `tests/test_ui_access_code.py`

Tests trang Access Code:

- ✅ `test_access_code_page_loads` - Page load và hiển thị đúng elements
- ✅ `test_access_code_redirect` - Redirect khi chưa verify
- ✅ `test_access_code_empty_submit` - HTML5 validation
- ✅ `test_access_code_autofocus` - Input có autofocus
- ✅ `test_access_code_success` - Verify thành công và redirect
- ✅ `test_access_code_wrong_code` - Hiển thị error khi sai code

### `tests/test_ui_dashboard.py`

Tests Dashboard:

- ✅ `test_dashboard_requires_access_code` - Dashboard yêu cầu xác thực

## Configuration

- **pytest.ini** - Cấu hình pytest chung
- **tests/conftest.py** - Fixtures cho tests

## Lưu ý quan trọng

⚠️ **Phải disable pytest-django plugin** (`-p no:django`) vì:

- Tests chạy với server đã start sẵn (không dùng live_server)
- Playwright async loop conflict với Django ORM

## Troubleshooting

### Lỗi "Browser not found"

```bash
C:\Users\ADMIN\anaconda3\envs\taichinh\python.exe -m playwright install chromium
```

### Lỗi "Connection refused"

Đảm bảo Django server đang chạy trên port 8000

### Tests chạy quá nhanh để xem

Sử dụng slow motion:

```bash
run_tests.bat slow
```
