# Hướng dẫn Setup

## 1. Cài đặt Dependencies

```bash
# Activate conda environment
conda activate taichinh

# Cài đặt packages
pip install -r requirements.txt
```

## 2. Cấu hình Environment Variables

File `.env` đã được tạo sẵn với cấu hình mặc định dùng `localhost` (phù hợp khi chạy từ host machine).

**Lưu ý:**
- **Khi chạy từ host machine (Windows/Linux/Mac)**: Sử dụng `localhost` (đã cấu hình sẵn)
- **Khi chạy trong Docker container**: Có thể đổi sang service names (`db`, `redis`, `qdrant`)

Cấu hình hiện tại trong `.env`:
```env
DB_HOST=localhost          # Đổi thành 'db' nếu chạy trong Docker
REDIS_HOST=localhost       # Đổi thành 'redis' nếu chạy trong Docker  
QDRANT_URL=http://localhost:6333  # Đổi thành 'http://qdrant:6333' nếu chạy trong Docker
```

## 3. Khởi động Services với Docker

```bash
# Khởi động PostgreSQL, Redis, Qdrant
docker-compose up -d

# Xem logs
docker-compose logs -f

# Dừng services
docker-compose down
```

## 4. Tạo Database và Migrations

```bash
# Tạo migrations (khi có models)
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Tạo superuser (nếu cần)
python manage.py createsuperuser
```

## 5. Test Kết nối

**QUAN TRỌNG:** Phải dùng Python từ conda environment taichinh!

```bash
# Cách 1: Dùng Python trực tiếp từ conda (Khuyên dùng)
C:\Users\ADMIN\anaconda3\envs\taichinh\python.exe test_connections.py

# Cách 2: Activate conda environment trước
conda activate taichinh
python test_connections.py

# Cách 3: Dùng script helper (Windows)
run_test.bat

# Cách 4: Dùng script helper (Linux/Mac)
chmod +x run_test.sh
./run_test.sh
```

## 6. Chạy Django Server

```bash
# Development server
python manage.py runserver

# Hoặc chạy trên port khác
python manage.py runserver 8000
```

## 7. Chạy Celery Worker (cho background tasks)

```bash
# Terminal 1: Celery worker
celery -A core worker -l info

# Terminal 2: Celery beat (cho periodic tasks)
celery -A core beat -l info
```

## Cấu trúc Project

```
App-QuanLyTaiChinh/
├── app/                    # Main app
│   ├── qdrant_client.py    # Qdrant service
│   └── ...
├── core/                   # Django project settings
│   ├── settings.py         # Main settings (đã config DB, Redis, Qdrant)
│   ├── celery.py           # Celery configuration
│   └── ...
├── docker-compose.yml      # Docker services
├── .env                    # Environment variables
├── requirements.txt        # Python dependencies
└── test_connections.py     # Test script
```

## Troubleshooting

### PostgreSQL connection failed
- Kiểm tra Docker container đang chạy: `docker ps`
- Kiểm tra `.env` có đúng `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`
- Test connection: `psql -h localhost -U postgres -d finance_db`

### Redis connection failed
- Kiểm tra Redis đang chạy: `docker ps | grep redis`
- Test connection: `redis-cli -h localhost -p 6379 ping`

### Qdrant connection failed
- Kiểm tra Qdrant đang chạy: `docker ps | grep qdrant`
- Test connection: `curl http://localhost:6333/health`

