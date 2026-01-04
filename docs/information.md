Dựa trên Tech Stack "cực chiến" bạn đã chọn (Django Ninja, Qdrant, Gemini, Ollama), dưới đây là bản **Tài liệu Đặc tả Tính năng (Feature Specification Document)**.

Bạn có thể dùng tài liệu này để làm `README.md` trên Github hoặc làm kim chỉ nam để dev từng module.

---

# TÊN DỰ ÁN: AI SMART FINANCE (Tên tạm)

## 1. Tổng quan (Overview)

Ứng dụng quản lý tài chính cá nhân đa nền tảng (PWA), tập trung vào việc giảm thiểu thao tác nhập liệu thủ công thông qua AI (NLP & OCR) và cung cấp khả năng phân tích dữ liệu tài chính sâu bằng ngôn ngữ tự nhiên (RAG).

**Tech Stack cốt lõi:**

* **BE:** Python (Django Ninja).
* **DB:** PostgreSQL (Transactional), Qdrant (Vector Search self host).
* **AI:** Gemini (Vision/Reasoning), Ollama/bge-m3 (Embedding ollama url http://222.253.80.30:11434/).
* **FE:** PWA (dùng htmlcss thuần của django lun).

---

## 2. Danh sách Tính năng chi tiết (Feature List)

### Module 1: Nhập liệu Thông minh (Smart Input - AI Core)

*Mục tiêu: Giảm thời gian nhập giao dịch từ 30s xuống còn 3-5s.*

#### 1.1. Quick Add by Text (NLP)

* **Mô tả:** Người dùng nhập câu nói tự nhiên, hệ thống tự trích xuất thông tin.
* **Input:** "Sáng nay ăn phở 45k tiền mặt, rồi ghé Circle K mua nước 10k quẹt Momo."
* **Process (Backend):**
* LLM (Gemini/Local LLM) phân tích câu.
* Tách thành 2 giao dịch riêng biệt.
* Mapping danh mục: "phở"  Ăn uống, "Circle K"  Cửa hàng tiện lợi.


* **Output:** Tự động tạo 2 record transaction trong PostgreSQL chờ user confirm.

#### 1.2. Scan & Log (OCR & Vision)

* **Mô tả:** Chụp/Upload ảnh hóa đơn hoặc ảnh chụp màn hình chuyển khoản.
* **Công nghệ:** Gemini Vision API.
* **Tính năng:**
* Tự động detect Merchant Name (Tên quán).
* Tự động detect Total Amount.
* Tách line items (danh sách món ăn/hàng hóa) để lưu chi tiết (nếu cần).
* Tự động phân loại Category dựa trên tên món hàng.



---

### Module 2: Quản lý & Tìm kiếm (Core Management & Search)

#### 2.1. Quản lý Đa ví (Multi-wallet)

* Hỗ trợ ví Tiền mặt, Ngân hàng, Thẻ tín dụng, Ví điện tử.
* **Tính năng đặc biệt:** Exclude from Total (Ví dụ: Ví tiết kiệm không tính vào dòng tiền chi tiêu hàng ngày).

#### 2.2. Semantic Search (Tìm kiếm ngữ nghĩa - Qdrant)

* **Vấn đề cũ:** Search "Nhậu" sẽ không ra nếu record ghi là "Bia tươi Sài Gòn".
* **Giải pháp AI (bge-m3):**
* User search: "Hôm bữa đi nhậu hết bao nhiêu?"
* Hệ thống vector hóa câu search  so khớp với vector description trong Qdrant.
* Kết quả trả về: Các giao dịch bia, mồi, karaoke,... dù không khớp từ khóa chính xác.



#### 2.3. Auto-Categorization (Tự học)

* Hệ thống ghi nhớ thói quen sửa lại của user.
* Ví dụ: Lần 1 AI đoán "Highlands" là "Ăn uống", user sửa thành "Hẹn hò". Lần 2 AI sẽ auto set "Hẹn hò".

---

### Module 3: Trợ lý Tài chính (AI Financial Agent - RAG)

*Đây là tính năng "Killer Feature" khác biệt hoàn toàn với các app truyền thống.*

#### 3.1. Chat with Data (Hỏi đáp dữ liệu)

* **User:** "Tháng này tui tiêu lố ngân sách mục Cafe chưa?"
* **Luồng xử lý:**
1. Agent query PostgreSQL lấy tổng tiền mục Cafe tháng hiện tại.
2. Agent lấy Budget mục Cafe.
3. LLM so sánh và trả lời: "Tháng này bạn đặt budget 500k, đã tiêu 450k. Chỉ còn dư 50k (đủ 1 ly nữa thôi nhé!)."



#### 3.2. Anomalies Detection (Cảnh báo bất thường)

* Phát hiện chi tiêu tăng đột biến so với trung bình 3 tháng trước.
* Ví dụ: "Cảnh báo: Tiền điện tháng này tăng 40% so với tháng trước."

#### 3.3. Sentiment/Diary Analysis

* Cho phép user attach note dài (như nhật ký) vào giao dịch.
* AI phân tích xem cảm xúc của user khi tiêu tiền (Vui, Hối hận, Cần thiết) để báo cáo mức độ "Chi tiêu hạnh phúc".

---

### Module 4: Hệ thống & PWA (System & Non-functional)

#### 4.1. Offline Mode (PWA)

* Cho phép nhập liệu, chụp ảnh khi không có mạng.
* Dữ liệu lưu vào `IndexedDB` hoặc `LocalStorage`.
* Background Sync: Khi có mạng, tự động đẩy về Django API.

#### 4.2. Self-hosted Optimization

* Tùy chọn switch giữa OpenAI/Gemini (Cloud) và Ollama (Local Server của bạn) trong cài đặt để tiết kiệm chi phí hoặc bảo mật dữ liệu.

#### 4.3. Access Code Protection (Bảo vệ bằng Mã truy cập)

* **Mô tả:** Hệ thống yêu cầu nhập mã truy cập khi lần đầu truy cập web để ngăn người khác vào ứng dụng.
* **Tính năng:**
* Màn hình nhập mã truy cập hiển thị khi chưa xác thực.
* Mã truy cập được lưu vào `LocalStorage` hoặc `SessionStorage` sau khi nhập đúng.
* Mã được mã hóa (hash) trước khi lưu để bảo mật.
* Có thể đổi mã truy cập trong phần Settings (yêu cầu nhập mã cũ trước khi đổi).
* Mã mặc định có thể được set trong Django settings hoặc database.
* **Luồng xử lý:**
1. User truy cập web → Kiểm tra có mã đã lưu trong storage chưa.
2. Nếu chưa có → Hiển thị form nhập mã.
3. User nhập mã → Backend verify mã (so sánh hash).
4. Nếu đúng → Lưu token/session vào storage, cho phép truy cập.
5. Nếu sai → Hiển thị thông báo lỗi, yêu cầu nhập lại.
* **Bảo mật:**
* Mã truy cập được hash bằng bcrypt/argon2 trước khi lưu trong database.
* Có thể set số lần nhập sai tối đa (rate limiting) để chống brute force.
* Token/session có thể có thời gian hết hạn (optional).

#### 4.4. Redis Cache & Task Queue

* **Mô tả:** Sử dụng Redis cho caching, session storage, và task queue (Celery) để tối ưu hiệu năng và xử lý background jobs.
* **Tính năng:**
* **Caching:**
* Cache kết quả query phức tạp (dashboard stats, budget calculations).
* Cache AI embeddings để tránh tính toán lại.
* Cache semantic search results với TTL phù hợp.
* **Session Storage:**
* Lưu session data thay vì database để tăng tốc độ.
* Hỗ trợ distributed sessions nếu scale nhiều server.
* **Task Queue (Celery):**
* Background tasks cho Recurring Transactions (tự động tạo giao dịch định kỳ).
* Async tasks cho OCR processing (Gemini Vision API).
* Async tasks cho vector embedding và sync với Qdrant.
* Async tasks cho budget warnings và notifications.
* **Rate Limiting:**
* Giới hạn số lần nhập sai access code (chống brute force).
* Giới hạn số request API per user/IP.
* **Triển khai:**
* Redis connection pool để tối ưu performance.
* Sử dụng `django-redis` cho Django cache backend.
* Sử dụng `celery` với Redis broker và result backend.
* Cấu hình TTL (Time To Live) phù hợp cho từng loại cache.
* **Cấu hình Django:**
```python
# settings.py
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': f'redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/0',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Celery Configuration
CELERY_BROKER_URL = f'redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/1'
CELERY_RESULT_BACKEND = f'redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/2'
```

---

### Module 5: Tính năng Cốt lõi - Cổ điển (Core Features)

*Mục tiêu: Bổ sung các tính năng "nhàm chán" nhưng cần thiết để thay thế hoàn toàn Money Lover.*

#### 5.1. Quản lý Ngân sách (Budgets) - *Quan trọng nhất*

* **Mô tả:** Cho phép user đặt limit cho từng Category theo tuần/tháng và cảnh báo khi sắp vượt quá.
* **Tính năng:**
* User có thể tạo budget cho từng category (ví dụ: Ăn uống 5 triệu/tháng).
* Hệ thống tự động tính tổng chi tiêu trong period và so sánh với budget.
* Cảnh báo real-time khi chi tiêu đạt 80%, 100%, 120% budget.
* **AI Integration:** Khi user nhập "Ăn lẩu 500k", AI check ngay budget và warning: *"Cẩn thận, bữa lẩu này làm lố ngân sách rồi đó!"*
* **Triển khai:**
* Table `Budget` (category_id, amount, period: 'monthly'/'weekly', start_date, end_date).
* API endpoint tính toán tổng chi tiêu theo category trong period.
* Real-time notification khi tạo transaction mới.

#### 5.2. Giao dịch định kỳ (Recurring Transactions)

* **Mô tả:** Tự động tạo giao dịch cho các khoản chi tiêu/thu nhập định kỳ (tiền nhà, Netflix, lương, Spotify...).
* **Tính năng:**
* User tạo một lần, hệ thống tự động sinh transaction mỗi chu kỳ.
* Hỗ trợ các chu kỳ: daily, weekly, monthly, yearly.
* Có thể tạm dừng hoặc xóa recurring transaction.
* **Triển khai:**
* Table `RecurringTransaction` (name, amount, frequency, next_run_date, is_active).
* Dùng **Celery** hoặc **Django-Q** để tự động sinh transaction khi đến ngày.
* Background task chạy định kỳ check và tạo transaction mới.

#### 5.3. Sổ nợ (Debts & Loans)

* **Mô tả:** Quản lý ai nợ mình, mình nợ ai - tách biệt khỏi chi tiêu thường.
* **Tính năng:**
* Ghi nhận cho vay (tiền ra nhưng không mất đi).
* Ghi nhận đi vay (tiền vào nhưng không phải thu nhập).
* Theo dõi thu nợ và trả nợ.
* Liên kết với contact person (tên người vay/nợ).
* **Triển khai:**
* Thêm field `transaction_type` vào Transaction với các loại: `expense`, `income`, `debt_loan`, `debt_borrow`, `debt_collect`, `debt_repay`.
* Thêm field `contact_person` để lưu tên người liên quan.
* Dashboard riêng hiển thị tổng nợ phải thu và phải trả.

#### 5.4. Dashboard trực quan (Visual Reports)

* **Mô tả:** Màn hình Home với biểu đồ tổng quan dòng tiền, giúp user nắm bắt tình hình tài chính nhanh chóng.
* **Tính năng:**
* Biểu đồ tròn (Pie Chart) phân bổ chi tiêu theo category.
* Biểu đồ cột (Bar Chart) so sánh thu/chi theo tháng.
* Biểu đồ đường (Line Chart) xu hướng chi tiêu theo thời gian.
* Cards hiển thị số liệu tổng quan: Tổng thu, Tổng chi, Số dư, Budget status.
* **Triển khai:**
* API endpoint trả về data đã aggregate (`GROUP BY category`, `SUM by month`).
* Frontend dùng Chart.js hoặc D3.js để vẽ biểu đồ.
* Có thể filter theo khoảng thời gian (tuần, tháng, quý, năm).

---

## 3. Phân tích Khoảng trống (Gap Analysis)

### 3.1. So sánh với Money Lover (Feature Matrix)

| Tính năng | Money Lover (Truyền thống) | App của Bạn (AI Power) | Đánh giá |
| --- | --- | --- | --- |
| **Nhập liệu** | Chọn icon -> Nhập số -> Chọn ngày (Lâu) | **Chat/OCR (Cực nhanh)** | **Bạn thắng** |
| **Tìm kiếm** | Theo từ khóa/ngày (Hạn chế) | **Semantic Search (Tìm theo ý nghĩa)** | **Bạn thắng** |
| **Phân tích** | Biểu đồ tĩnh | **Hỏi đáp AI (RAG Insight)** | **Bạn thắng** |
| **Ngân sách** | Có, cảnh báo rõ ràng | *Cần bổ sung (Module 5.1)* | Cần bổ sung gấp |
| **Định kỳ** | Tự động thêm hàng tháng | *Cần bổ sung (Module 5.2)* | Cần bổ sung |
| **Sổ nợ** | Quản lý vay/nợ riêng | *Cần bổ sung (Module 5.3)* | Cần bổ sung |
| **Dashboard** | Biểu đồ đầy đủ | *Cần bổ sung (Module 5.4)* | Cần bổ sung |
| **Liên kết NH** | Có (nhưng hay lỗi/tốn phí) | *Không (Dùng AI đọc màn hình)* | Giải pháp của bạn an toàn hơn |
| **Sự kiện/Du lịch** | Chế độ "Đi du lịch" | *Chưa có* | Có thể làm sau (Low priority) |

### 3.2. Những thứ ĐANG THIẾU (Missing Features)

Hiện tại, ứng dụng đang là một **"Công cụ nhập liệu và tìm kiếm siêu việt"** (AI Input & Search Engine), nhưng để thay thế được Money Lover - một **"Hệ thống quản lý tài chính toàn diện"**, cần bổ sung 4 mảng lớn:

#### A. Ngân sách (Budgets) - *Quan trọng nhất*

Money Lover giữ chân user vì nó báo: *"Bạn đã tiêu lố 80% tiền ăn tháng này rồi!"*.

* **Logic:** Cho phép user đặt limit cho từng Category theo tuần/tháng.
* **Triển khai:** Xem Module 5.1.

#### B. Giao dịch định kỳ (Recurring Transactions)

Tiền nhà, tiền Netflix, tiền lương, tiền Spotify... tháng nào cũng như tháng nào.

* **Logic:** Không ai muốn nhập tay mấy cái này mỗi tháng cả.
* **Triển khai:** Xem Module 5.2.

#### C. Sổ nợ (Debts & Loans)

"Tao cho thằng A mượn 500k", "Đang nợ thẻ tín dụng 10tr".

* **Logic:** Quản lý ai nợ mình, mình nợ ai. Money Lover tách cái này ra khỏi chi tiêu thường.
* **Triển khai:** Xem Module 5.3.

#### D. Dashboard trực quan (Visual Reports)

AI Chat (RAG) rất ngầu, nhưng đôi khi user chỉ muốn nhìn nhanh một cái **Biểu đồ tròn (Pie Chart)** xem tháng này tiền đi về đâu.

* **Logic:** Màn hình Home phải có biểu đồ tổng quan dòng tiền.
* **Triển khai:** Xem Module 5.4.

### 3.3. Kết luận

* **Nếu làm MVP cá nhân:** Phiên bản hiện tại (AI Input + Search) là **đủ để gây nghiện** vì nó giải quyết nỗi đau lớn nhất là "lười nhập".

* **Nếu muốn làm sản phẩm hoàn chỉnh:** Bắt buộc phải có **Budget (Module 5.1)** và **Recurring Transactions (Module 5.2)**. Đây là 2 tính năng "cốt lõi - cổ điển" mà user cần dùng mỗi ngày.

---

### 4. Cấu trúc Database (Gợi ý sơ bộ cho Django Models)

Dưới đây là bản nháp schema để bạn hình dung cách lưu trữ vector song song với data thường.

```python
# models.py trong Django
from django.db import models
from django.contrib.postgres.fields import ArrayField # Cần thiết cho Vector nếu lưu trong PG (hoặc dùng Qdrant ID)
from django.contrib.auth.hashers import make_password, check_password

class AccessCode(models.Model):
    """Model lưu mã truy cập đã được hash"""
    code_hash = models.CharField(max_length=255) # Mã đã được hash
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    @classmethod
    def verify_code(cls, raw_code: str) -> bool:
        """Verify mã truy cập"""
        access_code = cls.objects.filter(is_active=True).first()
        if not access_code:
            return False
        return check_password(raw_code, access_code.code_hash)
    
    @classmethod
    def set_code(cls, raw_code: str):
        """Set mã truy cập mới"""
        code_hash = make_password(raw_code)
        access_code, created = cls.objects.get_or_create(id=1)
        access_code.code_hash = code_hash
        access_code.is_active = True
        access_code.save()

class Wallet(models.Model):
    name = models.CharField(max_length=100)
    balance = models.DecimalField(max_digits=15, decimal_places=2)
    wallet_type = models.CharField(max_length=50) # 'cash', 'bank', 'credit_card', 'e_wallet'
    exclude_from_total = models.BooleanField(default=False) # Ví tiết kiệm không tính vào tổng
    # ...

class Category(models.Model):
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, blank=True) # Icon name hoặc emoji
    # ...

# 1. Quản lý Ngân sách (Budgets)
class Budget(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2) # Ví dụ: 5 triệu
    period = models.CharField(max_length=20, default='monthly') # 'monthly', 'weekly'
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def get_spent_amount(self):
        """Tính tổng đã chi tiêu trong period"""
        from django.db.models import Sum
        return Transaction.objects.filter(
            category=self.category,
            date__gte=self.start_date,
            date__lte=self.end_date,
            transaction_type__in=['expense', 'debt_repay']
        ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    def get_remaining_amount(self):
        """Tính số tiền còn lại"""
        return self.amount - self.get_spent_amount()
    
    def get_percentage_used(self):
        """Tính % đã sử dụng"""
        if self.amount == 0:
            return 0
        return (self.get_spent_amount() / self.amount) * 100

# 2. Giao dịch định kỳ (Recurring)
class RecurringTransaction(models.Model):
    name = models.CharField(max_length=100) # "Tiền nhà", "Netflix", "Lương"
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    frequency = models.CharField(max_length=20) # 'daily', 'weekly', 'monthly', 'yearly'
    next_run_date = models.DateField()
    is_active = models.BooleanField(default=True)
    transaction_type = models.CharField(max_length=20, default='expense') # 'expense' hoặc 'income'
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Transaction(models.Model):
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    description = models.TextField(blank=True) # Text gốc: "Ăn phở 50k"
    
    # Loại giao dịch
    TYPE_CHOICES = [
        ('expense', 'Chi tiêu'),
        ('income', 'Thu nhập'),
        ('debt_loan', 'Cho vay'), # Tiền ra khỏi ví nhưng không mất đi
        ('debt_borrow', 'Đi vay'), # Tiền vào ví nhưng không phải thu nhập
        ('debt_collect', 'Thu nợ'),
        ('debt_repay', 'Trả nợ')
    ]
    transaction_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='expense')
    contact_person = models.CharField(max_length=100, null=True, blank=True) # Tên người vay/nợ
    
    # Metadata cho AI
    raw_ocr_text = models.TextField(blank=True, null=True) # Text full từ hóa đơn
    qdrant_point_id = models.UUIDField(null=True) # ID mapping sang Qdrant
    
    # Link với RecurringTransaction (nếu được tạo tự động)
    recurring_transaction = models.ForeignKey(
        RecurringTransaction, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    
    date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Trigger async task để update vector bên Qdrant tại đây
        # Check budget và cảnh báo nếu vượt quá
        super().save(*args, **kwargs)
        
        # TODO: Trigger budget check và notification nếu cần

```

**Bước tiếp theo:**
Bạn có muốn tui đi sâu vào thiết kế **API Spec (Swagger/OpenAPI)** cho các endpoint quan trọng trong Django Ninja không? Hay là bạn muốn xem trước **cấu trúc prompt** gửi cho Gemini?