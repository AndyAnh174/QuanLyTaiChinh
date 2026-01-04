# Hướng Dẫn Kích Hoạt Deployment

Để kích hoạt quá trình Deploy tự động (CI/CD) mà chúng ta đã cấu hình, bạn cần tạo một **Release Tag** mới trên GitHub.

## Các Bước Thực Hiện:

1. Vào trang GitHub Repo của dự án.
2. Ở cột bên phải (Sidebar), tìm mục **Releases** và bấm vào đó (hoặc bấm **Create a new release**).
3. Bấm nút **Draft a new release**.
4. Điền các thông tin sau vào form:
   
   - **Choose a tag**: Nhập `v1.0.0` (Rồi bấm nút "Create new tag: v1.0.0...").
     > Đây là phiên bản chính thức đầu tiên của chúng ta.
   
   - **Target**: Chọn `main` (hoặc `master`).
   
   - **Release title**: Đặt tiêu đề, ví dụ: `Official Release v1.0.0`.
   
   - **Describe this release**: Ghi chú về phiên bản này. Ví dụ:
     ```markdown
     ## Tính năng mới
     - Hoàn thiện AI Chatbot tài chính thông minh.
     - Cấu hình CI/CD tự động deploy lên Self-hosted Runner.
     - Tối ưu hóa Database với PostgreSQL, Redis và Qdrant.
     - Fix bảo mật và cấu hình Domain chính thức.
     ```

5. Bấm nút xanh **Publish release**.

## Chuyện Gì Xảy Ra Tiếp Theo?

Ngay sau khi bạn bấm Publish:
1. GitHub Actions sẽ tự động kích hoạt workflow.
2. Nó sẽ chạy Test lại một lần nữa.
3. Nếu Test thành công, nó sẽ gửi lệnh xuống máy chủ của bạn để update code mới nhất và khởi động lại dịch vụ.

Chúc mừng bạn đã hoàn tất quy trình phát triển chuyên nghiệp! 🚀
