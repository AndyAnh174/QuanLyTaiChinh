# AI Smart Finance

![Status](https://img.shields.io/badge/Status-Completed-success?style=for-the-badge)
![AI](https://img.shields.io/badge/AI-Gemini%20%7C%20Ollama-blue?style=for-the-badge)
![Backend](https://img.shields.io/badge/Backend-Django_Ninja-092E20?style=for-the-badge&logo=django)
![Frontend](https://img.shields.io/badge/Frontend-Bootstrap_5-7952B3?style=for-the-badge&logo=bootstrap)
![Database](https://img.shields.io/badge/Database-PostgreSQL-336791?style=for-the-badge&logo=postgresql)
![Vector DB](https://img.shields.io/badge/Vector_DB-Qdrant-red?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)

Ứng dụng quản lý tài chính cá nhân thông minh với AI, sử dụng Django Ninja, PostgreSQL, Qdrant, Gemini, và Ollama.

**Project Info**:
- **Author**: AndyAnh174 (Hồ Việt Anh)
- **License**: [MIT License](LICENSE)
- **Certificates**: [View Certificates](CERTIFICATES.md)

## Tính năng chính

### ✅ Đã triển khai

1. **Database Models** - Tất cả models đã được tạo:
   - AccessCode, Wallet, Category, Transaction, Budget, RecurringTransaction
   - Migrations đã chạy thành công

2. **Access Code Protection** - Bảo vệ bằng mã truy cập:
   - API endpoints: `/api/v1/auth/verify`, `/api/v1/auth/change`
   - Middleware để kiểm tra access code
   - Rate limiting chống brute force

3. **Basic CRUD APIs** - Django Ninja APIs:
   - Wallets, Categories, Transactions
   - Full CRUD operations

4. **AI Services Integration**:
   - AI Service abstraction (Gemini/Ollama switching)
   - Embedding Service với Redis caching
   - NLP Service cho Quick Add by Text
   - OCR Service cho receipt processing

5. **Vector Search**:
   - Qdrant integration với batch operations
   - Semantic search API
   - Auto vector sync on transaction save

6. **Budget Management**:
   - Budget CRUD APIs
   - Real-time budget checking
   - Warnings at 80%, 100%, 120% thresholds

7. **Recurring Transactions**:
   - CRUD APIs
   - Celery periodic task for auto-generation

8. **Dashboard APIs**:
   - Summary, category breakdown, monthly comparison, trends
   - Redis caching for performance

9. **Debts & Loans**:
   - Debt/Loan summary APIs
   - Transaction filtering by type

10. **RAG Chat**:
    - Chat with Data API
    - Natural language queries

11. **Anomaly Detection**:
    - Service và Celery task

12. **Frontend (PWA)**:
    - Base templates
    - Access code UI
    - Transaction management UI
    - Dashboard UI
    - Service Worker cho offline support

## Cấu trúc Project

```
App-QuanLyTaiChinh/
├── app/
│   ├── models.py              # All Django models
│   ├── admin.py               # Admin interfaces
│   ├── api/                   # Django Ninja routers
│   │   ├── auth.py
│   │   ├── wallets.py
│   │   ├── categories.py
│   │   ├── transactions.py
│   │   ├── budgets.py
│   │   ├── recurring.py
│   │   ├── debts.py
│   │   ├── search.py
│   │   ├── chat.py
│   │   └── dashboard.py
│   ├── services/              # Business logic
│   │   ├── ai_service.py
│   │   ├── embedding_service.py
│   │   ├── nlp_service.py
│   │   ├── ocr_service.py
│   │   ├── vector_service.py
│   │   ├── category_learning.py
│   │   ├── budget_service.py
│   │   ├── rag_service.py
│   │   ├── anomaly_service.py
│   │   └── sentiment_service.py
│   ├── tasks/                 # Celery tasks
│   │   ├── recurring_tasks.py
│   │   ├── ocr_tasks.py
│   │   ├── vector_tasks.py
│   │   └── anomaly_tasks.py
│   ├── middleware.py          # Access code middleware
│   ├── qdrant_client.py       # Qdrant service
│   └── management/commands/     # Management commands
│       └── init_access_code.py
├── templates/                  # Django templates
│   ├── base.html
│   ├── auth/
│   ├── transactions/
│   └── dashboard/
├── static/                     # Static files
│   ├── css/
│   ├── js/
│   ├── manifest.json
│   └── sw.js
└── core/                       # Django settings
    ├── settings.py
    ├── urls.py
    └── celery.py
```

## Cài đặt và Chạy

### 1. Setup Environment

```bash
# Activate conda environment
conda activate taichinh

# Install dependencies
pip install -r requirements.txt
```

### 2. Khởi động Services

```bash
# Start Docker services (PostgreSQL, Redis, Qdrant)
docker-compose up -d
```

### 3. Database Setup

```bash
# Run migrations
python manage.py migrate

# Initialize access code (default: 1234)
python manage.py init_access_code 1234

# Create superuser (optional)
python manage.py createsuperuser
```

### 4. Chạy Server

```bash
# Django development server
python manage.py runserver

# Celery worker (in separate terminal)
celery -A core worker -l info

# Celery beat (in separate terminal)
celery -A core beat -l info
```

### 5. Test Connections

```bash
# Test all connections
C:\Users\ADMIN\anaconda3\envs\taichinh\python.exe test_connections.py
```

## API Endpoints

Tất cả APIs được document tại: `http://localhost:8000/api/v1/docs`

### Main Endpoints:
- `/api/v1/auth/*` - Access code authentication
- `/api/v1/wallets/*` - Wallet management
- `/api/v1/categories/*` - Category management
- `/api/v1/transactions/*` - Transaction CRUD + Quick Add + OCR
- `/api/v1/budgets/*` - Budget management
- `/api/v1/recurring/*` - Recurring transactions
- `/api/v1/debts/*` - Debts & loans
- `/api/v1/search/semantic` - Semantic search
- `/api/v1/chat/ask` - RAG chat
- `/api/v1/dashboard/*` - Dashboard data

## Environment Variables

Cấu hình trong `.env`:
- Database: `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`
- Redis: `REDIS_HOST`, `REDIS_PORT`, `REDIS_PASSWORD`
- Qdrant: `QDRANT_URL`
- AI: `GEMINI_API_KEY`, `OLLAMA_URL`

## Notes

- Access code mặc định: `1234` (có thể đổi bằng management command)
- Vector size trong Qdrant: 768 (bge-m3 embedding)
- Celery tasks cần Redis và Celery worker đang chạy
- Frontend sử dụng PWA với Service Worker cho offline support

## Next Steps

- Thêm Chart.js cho dashboard visualizations
- Hoàn thiện frontend UI/UX
- Thêm unit tests
- Performance optimization
- Production deployment configuration

