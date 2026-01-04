"""
Django models for AI Smart Finance application
"""
from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.db.models import Sum
from django.utils import timezone
import uuid


class AccessCode(models.Model):
    """Model lưu mã truy cập đã được hash"""
    code_hash = models.CharField(max_length=255)  # Mã đã được hash
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Access Code"
        verbose_name_plural = "Access Codes"
    
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
        return access_code


class Wallet(models.Model):
    """Ví tiền - hỗ trợ đa ví"""
    WALLET_TYPES = [
        ('cash', 'Tiền mặt'),
        ('bank', 'Ngân hàng'),
        ('credit_card', 'Thẻ tín dụng'),
        ('e_wallet', 'Ví điện tử'),
    ]
    
    name = models.CharField(max_length=100, verbose_name="Tên ví")
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="Số dư")
    wallet_type = models.CharField(max_length=50, choices=WALLET_TYPES, default='cash', verbose_name="Loại ví")
    exclude_from_total = models.BooleanField(
        default=False, 
        verbose_name="Không tính vào tổng",
        help_text="Ví tiết kiệm không tính vào dòng tiền chi tiêu hàng ngày"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Ví"
        verbose_name_plural = "Ví"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.get_wallet_type_display()})"


class Category(models.Model):
    """Danh mục giao dịch"""
    name = models.CharField(max_length=100, verbose_name="Tên danh mục")
    icon = models.CharField(max_length=50, blank=True, verbose_name="Icon", help_text="Icon name hoặc emoji")
    description = models.TextField(blank=True, verbose_name="Mô tả")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Danh mục"
        verbose_name_plural = "Danh mục"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class RecurringTransaction(models.Model):
    """Giao dịch định kỳ"""
    FREQUENCY_CHOICES = [
        ('daily', 'Hàng ngày'),
        ('weekly', 'Hàng tuần'),
        ('monthly', 'Hàng tháng'),
        ('yearly', 'Hàng năm'),
    ]
    
    TRANSACTION_TYPE_CHOICES = [
        ('expense', 'Chi tiêu'),
        ('income', 'Thu nhập'),
    ]
    
    name = models.CharField(max_length=100, verbose_name="Tên giao dịch")
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, verbose_name="Ví")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Danh mục")
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Số tiền")
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default='monthly', verbose_name="Tần suất")
    next_run_date = models.DateField(verbose_name="Ngày chạy tiếp theo")
    is_active = models.BooleanField(default=True, verbose_name="Đang hoạt động")
    transaction_type = models.CharField(
        max_length=20, 
        choices=TRANSACTION_TYPE_CHOICES, 
        default='expense',
        verbose_name="Loại giao dịch"
    )
    description = models.TextField(blank=True, verbose_name="Mô tả")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Giao dịch định kỳ"
        verbose_name_plural = "Giao dịch định kỳ"
        ordering = ['next_run_date']
    
    def __str__(self):
        return f"{self.name} - {self.get_frequency_display()}"


class Budget(models.Model):
    """Ngân sách theo danh mục"""
    PERIOD_CHOICES = [
        ('weekly', 'Hàng tuần'),
        ('monthly', 'Hàng tháng'),
    ]
    
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="Danh mục")
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Số tiền")
    period = models.CharField(max_length=20, choices=PERIOD_CHOICES, default='monthly', verbose_name="Chu kỳ")
    start_date = models.DateField(verbose_name="Ngày bắt đầu")
    end_date = models.DateField(verbose_name="Ngày kết thúc")
    is_active = models.BooleanField(default=True, verbose_name="Đang hoạt động")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Ngân sách"
        verbose_name_plural = "Ngân sách"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.category.name} - {self.amount:,.0f} VNĐ/{self.get_period_display()}"
    
    def get_spent_amount(self):
        """Tính tổng đã chi tiêu trong period"""
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
        spent = self.get_spent_amount()
        return (spent / self.amount) * 100


class Transaction(models.Model):
    """Giao dịch tài chính"""
    TYPE_CHOICES = [
        ('expense', 'Chi tiêu'),
        ('income', 'Thu nhập'),
        ('debt_loan', 'Cho vay'),  # Tiền ra khỏi ví nhưng không mất đi
        ('debt_borrow', 'Đi vay'),  # Tiền vào ví nhưng không phải thu nhập
        ('debt_collect', 'Thu nợ'),
        ('debt_repay', 'Trả nợ')
    ]
    
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, verbose_name="Ví")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Danh mục")
    amount = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Số tiền")
    description = models.TextField(blank=True, verbose_name="Mô tả", help_text="Text gốc: 'Ăn phở 50k'")
    
    # Loại giao dịch
    transaction_type = models.CharField(
        max_length=20, 
        choices=TYPE_CHOICES, 
        default='expense',
        verbose_name="Loại giao dịch"
    )
    contact_person = models.CharField(
        max_length=100, 
        null=True, 
        blank=True, 
        verbose_name="Người liên quan",
        help_text="Tên người vay/nợ"
    )
    
    # Metadata cho AI
    raw_ocr_text = models.TextField(
        blank=True, 
        null=True, 
        verbose_name="Text từ OCR",
        help_text="Text full từ hóa đơn"
    )
    qdrant_point_id = models.UUIDField(
        null=True, 
        blank=True,
        verbose_name="Qdrant Point ID",
        help_text="ID mapping sang Qdrant"
    )
    
    # Link với RecurringTransaction (nếu được tạo tự động)
    recurring_transaction = models.ForeignKey(
        RecurringTransaction, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name="Giao dịch định kỳ"
    )
    
    date = models.DateTimeField(default=timezone.now, verbose_name="Ngày giao dịch")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    
    class Meta:
        verbose_name = "Giao dịch"
        verbose_name_plural = "Giao dịch"
        ordering = ['-date', '-created_at']
        indexes = [
            models.Index(fields=['-date']),
            models.Index(fields=['category', 'date']),
            models.Index(fields=['transaction_type', 'date']),
        ]
    
    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.amount:,.0f} VNĐ - {self.description[:50]}"


class ChatSession(models.Model):
    """Phiên chat với AI"""
    title = models.CharField(max_length=200, default="New Chat", verbose_name="Tiêu đề")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Chat Session"
        verbose_name_plural = "Chat Sessions"
        ordering = ['-updated_at']
        
    def __str__(self):
        return self.title


class ChatMessage(models.Model):
    """Tin nhắn trong phiên chat"""
    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
        ('system', 'System')
    ]
    
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages', verbose_name="Phiên chat")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, verbose_name="Vai trò")
    content = models.TextField(verbose_name="Nội dung")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Chat Message"
        verbose_name_plural = "Chat Messages"
        ordering = ['created_at']
        
    def __str__(self):
        return f"{self.role}: {self.content[:50]}"
    


