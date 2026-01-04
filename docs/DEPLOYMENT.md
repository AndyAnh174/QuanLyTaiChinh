# Hướng Dẫn Cấu Hình Deployment (CI/CD)

Tài liệu này hướng dẫn cách cấu hình GitHub Actions để tự động deploy ứng dụng lên Self-Hosted Runner.

## 1. Cấu hình Environment & Secrets (Quan trọng!)

Để Job Deploy hoạt động, bạn cần cấu hình **Environment** và **Secret** trên GitHub Repo.

### Bước 1: Tạo Environment
1. Vào tab **Settings** (Cài đặt) trên thanh menu trên cùng của Repo.
2. Ở menu bên trái, tìm mục **Code and automation**, chọn **Environments**.
3. Bấm nút **New environment**.
4. Đặt tên là `production` và bấm **Configure environment**.

### Bước 2: Thêm Secret (Biến môi trường)
1. Trong trang cấu hình của environment `production` vừa tạo.
2. Kéo xuống phần **Environment secrets**.
3. Bấm **Add secret**.
4. Điền thông tin sau:
   - **Name**: `ENV_FILE`
   - **Value**: (Copy toàn bộ nội dung từ file `.env.prod` dưới máy bạn va dán vào đây).
5. Bấm **Add secret**.

> **Lưu ý:** Ảnh bạn chụp là trang "New release" (Tạo phiên bản mới), **KHÔNG PHẢI** là trang cài đặt Environment. Bạn cần quay lại tab **Settings** của Repo nhé.

## 2. Kích hoạt Deployment

Quy trình CI/CD đã được cài đặt để chạy tự động:

1. **Trigger:** Mỗi khi bạn `push` code mới lên nhánh `main` hoặc `master`.
2. **Test:** GitHub sẽ chạy Test tự động.
3. **Deploy:** Nếu Test OK -> GitHub sẽ ra lệnh cho máy chủ của bạn (Self-hosted Runner) tải code về và deploy lại.

## 3. Kiểm tra kết quả
- Vào tab **Actions** trên GitHub để xem tiến trình chạy.
- Nếu thấy tích xanh ✅ ở cả job `test` và `deploy` là thành công.
