# AI Smart Finance - Quản Lý Tài Chính Thông Minh

![Status](https://img.shields.io/badge/Status-Completed-success?style=for-the-badge)
![AI](https://img.shields.io/badge/AI-Gemini%20%7C%20Ollama-blue?style=for-the-badge)
![Backend](https://img.shields.io/badge/Backend-Django_Ninja-092E20?style=for-the-badge&logo=django)
![Frontend](https://img.shields.io/badge/Frontend-Bootstrap_5-7952B3?style=for-the-badge&logo=bootstrap)
![Database](https://img.shields.io/badge/Database-PostgreSQL-336791?style=for-the-badge&logo=postgresql)
![Vector DB](https://img.shields.io/badge/Vector_DB-Qdrant-red?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)

## 📖 Giới Thiệu
**AI Smart Finance** là hệ thống quản lý tài chính cá nhân thế hệ mới, tích hợp sâu trí tuệ nhân tạo (AI) để không chỉ ghi chép mà còn phân tích, thấu hiểu và đưa ra lời khuyên tài chính cho người dùng. Dự án kết hợp sức mạnh của **Generative AI (Gemini/Ollama)** và **Vector Search (Qdrant)** để mang lại trải nghiệm tương tác tự nhiên và thông minh.

- **Tác giả**: AndyAnh174 (Hồ Việt Anh)
- **Giấy phép**: [MIT License](LICENSE)
- **Chứng nhận**: [Xem chi tiết](CERTIFICATES.md)

---

## 🚀 Tính Năng Nổi Bật

### 🤖 Trí Tuệ Nhân Tạo (AI Features)
- **Chat với Dữ Liệu (RAG)**: Hỏi đáp tự nhiên về tình hình tài chính (VD: "Tháng này tôi tiêu bao nhiêu cho ăn uống?", "So sánh với tháng trước").
- **Nhập Liệu Thông Minh (NLP)**: Tạo giao dịch từ câu nói tự nhiên (VD: "Sáng nay ăn phở 35k tiền mặt").
- **Phân Tích Chi Tiêu**: AI tự động phân loại giao dịch và phát hiện xu hướng tiêu dùng.
- **Quét Hóa Đơn (OCR)**: Tự động trích xuất thông tin từ ảnh chụp hóa đơn (đang phát triển).

### 💰 Quản Lý Tài Chính (Core Features)
- **Đa Ví & Danh Mục**: Quản lý nhiều nguồn tiền và danh mục chi tiêu tùy chỉnh.
- **Ngân Sách Thông Minh**: Thiết lập ngân sách và nhận cảnh báo khi chi tiêu lố tay.
- **Giao Dịch Định Kỳ**: Tự động ghi chép các khoản thu chi lặp lại (tiền nhà, lương, Netflix...).
- **Dashboard Trực Quan**: Biểu đồ thống kê Real-time, báo cáo thu chi, dòng tiền.

### 🛡️ Hệ Thống & Bảo Mật
- **Mã Truy Cập (Access Code)**: Bảo vệ dữ liệu cá nhân với lớp bảo mật 2 lớp.
- **An Toàn Dữ Liệu**: Sử dụng PostgreSQL mạnh mẽ và ổn định cho dữ liệu giao dịch.

---

## 🛠️ Công Nghệ Sử Dụng

| Thành phần | Công nghệ | Chi tiết |
|------------|-----------|----------|
| **Backend** | Python, Django | Django Ninja (FastAPI-like), Celery (Async Tasks) |
| **Frontend** | HTML5, JS | Bootstrap 5, Vanilla JS, PWA Ready |
| **Database** | PostgreSQL | Cơ sở dữ liệu chính (Relational) |
| **Vector DB** | Qdrant | Lưu trữ vector cho Semantic Search & RAG |
| **Cache** | Redis | Caching & Message Broker |
| **AI/LLM** | Gemini / Ollama | Generative AI Model & Embeddings |

---

## ⚙️ Cài Đặt & Triển Khai

### Yêu cầu hệ thống
- Python 3.10+
- Docker & Docker Compose
- API Key Google Gemini (Nếu dùng Cloud AI) hoặc Ollama (Nếu chạy Local)

### Các bước cài đặt

#### 1. Clone dự án và khởi tạo môi trường
```bash
git clone https://github.com/AndyAnh174/AI-Smart-Finance.git
cd AI-Smart-Finance

# Tạo môi trường ảo (khuyến nghị)
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

#### 2. Khởi chạy Services (Docker)
Chạy PostgreSQL, Qdrant và Redis bằng Docker Compose:
```bash
docker-compose up -d
```

#### 3. Cài đặt thư viện và cấu hình
```bash
pip install -r requirements.txt

# Tạo bảng trong Database
python manage.py migrate

# Khởi tạo mã truy cập mặc định (VD: 1234)
python manage.py init_access_code 1234
```

#### 4. Cấu hình biến môi trường
Tạo file `.env` tại thư mục gốc và điền thông tin:
```env
DB_NAME=taichinh
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
GEMINI_API_KEY=your_key_here
```

#### 5. Chạy ứng dụng
```bash
# Terminal 1: Chạy Web Server
python manage.py runserver

# Terminal 2: Chạy Celery Worker (Xử lý tác vụ nền)
celery -A core worker -l info
```
Truy cập ứng dụng tại: `http://localhost:8000`

---

## 📞 Liên Hệ
- **Developer**: Hồ Việt Anh (AndyAnh174)
- **Email**: [Email của bạn]
- **GitHub**: [github.com/AndyAnh174](https://github.com/AndyAnh174)

---
&copy; 2026 AI Smart Finance. MIT Licensed.
