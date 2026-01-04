APP_FEATURES = """
HỆ THỐNG QUẢN LÝ TÀI CHÍNH CÁ NHÂN THÔNG MINH (AI SMART FINANCE)
================================================================

GIỚI THIỆU CHUNG:
Đây là ứng dụng quản lý tài chính cá nhân hiện đại, tích hợp mạnh mẽ Trí tuệ nhân tạo (AI/LLM) để tự động hóa việc nhập liệu, phân tích dữ liệu và tư vấn tài chính. Ứng dụng giúp người dùng tối ưu hóa dòng tiền, tiết kiệm thời gian và đưa ra các quyết định tài chính thông minh hơn.

I. CÁC TÍNH NĂNG CHI TIẾT (DETAILED FEATURES)

1. Bảng Điều Khiển Trung Tâm (Smart Dashboard):
   - Tổng quan tài sản (Wealth Overview):
     + Thu nhập (Total Income): Tổng hợp tất cả các nguồn thu trọn đời hoặc theo bộ lọc.
     + Chi tiêu (Total Expense): Tổng hợp tất cả các khoản chi trọn đời.
     + Số dư thực tế (Net Worth): Tính toán chính xác tổng tài sản hiện có trên tất cả các ví (Tiền mặt + Ngân hàng + Đầu tư).
   - Phân tích trực quan (Visual Analytics):
     + Biểu đồ tròn (Pie Chart): Phân tích cơ cấu chi tiêu theo danh mục (Ăn uống, Nhà cửa,...) giúp nhận diện "lỗ hổng" tài chính.
     + Biểu đồ cột (Bar Chart): So sánh đối chiếu Thu - Chi trong 6 tháng gần nhất để đánh giá sức khỏe tài chính.
   - Dữ liệu thời gian thực: Mọi chỉ số được cập nhật ngay lập tức sau khi giao dịch phát sinh.

2. Quản lý Giao dịch (Transaction Hub):
   - Sổ cái điện tử: Lưu trữ chi tiết mọi giao dịch với các trường thông tin: Ngày giờ, Số tiền, Loại (Thu/Chi), Danh mục, Ví nguồn, Mô tả, và Người liên quan.
   - Công cụ mạnh mẽ: Hỗ trợ tìm kiếm, lọc, sửa đổi và xóa bỏ lịch sử giao dịch.

3. Nhập liệu Thông minh (AI-Powered Input) - Tính năng cốt lõi:
   a. Quick Add (Nhập liệu ngôn ngữ tự nhiên):
      - Mô tả: Người dùng chỉ cần nhập câu văn bình thường, không cần chọn ô thủ công.
      - Ví dụ: "Sáng nay đổ xăng 50k và ăn phở 40k bằng tiền mặt".
      - Xử lý AI: Hệ thống tự động tách thành 2 giao dịch riêng biệt, nhận diện số tiền, danh mục "Di chuyển", "Ăn uống" và ví "Tiền mặt".
   b. OCR Receipt Scanning (Quét hóa đơn tự động):
      - Mô tả: Upload ảnh hóa đơn mua sắm, bill siêu thị, nhà hàng.
      - Công nghệ: Sử dụng Gemini Vision để "đọc" ảnh.
      - Kết quả: Tự động trích xuất Tên cửa hàng (Merchant), Ngày tháng, Danh sách từng món hàng (Line items), Tổng tiền và tự động đề xuất danh mục phù hợp.

4. Trợ lý Tài chính AI (AI Financial Assistant):
   - Chatbot RAG (Retrieval-Augmented Generation): AI không chỉ trả lời chung chung mà còn "đọc" được dữ liệu trong Database của chính bạn.
   - Khả năng trả lời:
     + Truy vấn dữ liệu: "Tháng này tôi tiêu bao nhiêu tiền cho việc đi lại?", "Liệt kê các khoản chi lớn nhất năm qua".
     + Phân tích & Lời khuyên: "Tình hình tài chính tháng này thế nào?", "Tôi nên tiết kiệm thêm ở đâu?".
     + Hỗ trợ hệ thống: "Làm sao để tạo ngân sách mới?".

5. Quản lý Ngân sách & Cảnh báo (Smart Budgeting):
   - Thiết lập linh hoạt: Tạo ngân sách theo tuần hoặc tháng cho từng danh mục cụ thể.
   - Theo dõi Real-time: Thanh tiến trình hiển thị % ngân sách đã sử dụng.
   - Cảnh báo sớm: Nhắc nhở người dùng khi chi tiêu chạm ngưỡng nguy hiểm (gần hết ngân sách).

6. Hệ thống Ví & Danh mục (Wallets & Categories):
   - Đa dạng ví: Quản lý nhiều nguồn tiền: Tiền mặt, Tài khoản ngân hàng (VCB, Techcombank...), Ví điện tử (Momo, ZaloPay), Sổ tiết kiệm.
   - Danh mục tùy biến: Hệ thống danh mục phân cấp với biểu tượng (Icon) trực quan.

II. KIẾN TRÚC CÔNG NGHỆ (TECHNICAL ARCHITECTURE)

1. Backend (Lõi xử lý):
   - Framework: Django 5.0 (Python) & Django Ninja (REST API hiệu năng cao).
   - Database: PostgreSQL 16 (Lưu trữ dữ liệu giao dịch an toàn, bền vững).
   - Vector Search: Qdrant (Cơ sở dữ liệu vector để tìm kiếm ngữ nghĩa và hỗ trợ AI RAG).
   - Caching: Redis (Tăng tốc độ phản hồi API và lưu trữ session).
   - Async Tasks: Celery + Celery Beat (Xử lý tác vụ nặng: OCR, gửi mail, báo cáo định kỳ).

2. Frontend (Giao diện người dùng):
   - Core: HTML5, CSS3, JavaScript (Vanilla).
   - UI Kit: Bootstrap 5 (Giao diện hiện đại, Responsive trên Mobile/Desktop).
   - Visualization: Chart.js (Biểu đồ tương tác).

3. AI & Third-party APIs:
   - Generative AI: Google Gemini 1.5 Flash (Xử lý ngôn ngữ tự nhiên và hình ảnh tối ưu tốc độ/chi phí).
   - Embedding Models: Tạo vector đại diện cho dữ liệu văn bản.

4. Infrastructure (Hạ tầng):
   - Docker & Docker Compose: Đóng gói toàn bộ môi trường, dễ dàng triển khai (Deploy) chỉ với một câu lệnh.
   - Security: Hashed Access Codes, CSRF Protection, Secure Headers.

THÔNG TIN PHÁT TRIỂN:
- Tác giả: AndyAnh174 (Hồ Việt Anh).
- Trạng thái: Đang phát triển tích cực (Active Development).
"""
