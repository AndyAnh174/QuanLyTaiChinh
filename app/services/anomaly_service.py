"""
Anomaly detection service for spending patterns
"""
from typing import List, Dict
from datetime import datetime, timedelta
from django.db.models import Sum, Avg
from django.utils import timezone
from ..models import Transaction, Category


class AnomalyService:
    """
    Service for detecting anomalies in spending patterns
    """
    
    ANOMALY_THRESHOLD = 0.4  # 40% increase is considered anomaly
    
    def detect_anomalies(self) -> List[Dict]:
        """
        Detect spending anomalies by comparing current month with 3-month average
        
        Returns:
            List of anomaly dictionaries
        """
        now = timezone.now()
        current_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Get last 3 months (excluding current month)
        anomalies = []
        
        # Get all categories with expenses
        categories = Category.objects.filter(
            transaction__transaction_type='expense'
        ).distinct()
        
        for category in categories:
            # Calculate 3-month average (months 1-3 before current)
            month3_start = (current_month_start - timedelta(days=90)).replace(day=1)
            month3_end = current_month_start - timedelta(days=1)
            
            avg_expense = Transaction.objects.filter(
                category=category,
                transaction_type='expense',
                date__gte=month3_start,
                date__lte=month3_end
            ).aggregate(Avg('amount'))['amount__avg'] or 0
            
            if avg_expense == 0:
                continue
            
            # Calculate current month expense
            current_expense = Transaction.objects.filter(
                category=category,
                transaction_type='expense',
                date__gte=current_month_start,
                date__lte=now
            ).aggregate(Sum('amount'))['amount__sum'] or 0
            
            # Check for anomaly
            if current_expense > 0:
                increase = (current_expense - avg_expense) / avg_expense
                
                if increase >= self.ANOMALY_THRESHOLD:
                    anomalies.append({
                        'category': category.name,
                        'current_month': float(current_expense),
                        'average': float(avg_expense),
                        'increase_percentage': increase * 100,
                        'message': f"Tiền {category.name} tháng này tăng {increase * 100:.1f}% so với trung bình 3 tháng trước."
                    })
        
        return anomalies


# Singleton instance
anomaly_service = AnomalyService()

