"""
Dashboard API endpoints for visual reports
"""
from ninja import Router
from typing import List, Dict
from pydantic import BaseModel
from datetime import datetime, timedelta
from django.db.models import Sum, Count, Q
from django.core.cache import cache
from django.utils import timezone
from ..models import Transaction, Budget, Wallet

router = Router(tags=["dashboard"])


class SummaryCard(BaseModel):
    total_income: float
    total_expense: float
    balance: float  # income - expense trong period
    transaction_count: int
    current_balance: float  # Tổng số dư hiện tại từ các ví
    available_balance: float  # Số dư khả dụng (không tính tiết kiệm)


class CategoryBreakdown(BaseModel):
    category: str
    amount: float
    percentage: float


class MonthlyComparison(BaseModel):
    month: str
    income: float
    expense: float
    balance: float


@router.get("/summary", response=SummaryCard, summary="Get financial summary")
def get_summary(request, start_date: str = None, end_date: str = None):
    """
    Get total income, expense, balance, and transaction count
    """
    # Parse dates or use defaults (current month)
    if start_date:
        start = datetime.fromisoformat(start_date)
    else:
        start = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    if end_date:
        end = datetime.fromisoformat(end_date)
    else:
        end = timezone.now()
    
    
    # Calculate totals
    # No caching for real-time updates
    
    # Calculate totals
    income = Transaction.objects.filter(
        transaction_type='income',
        date__gte=start,
        date__lte=end
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    expense = Transaction.objects.filter(
        transaction_type='expense',
        date__gte=start,
        date__lte=end
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    count = Transaction.objects.filter(
        date__gte=start,
        date__lte=end
    ).count()
    
    # Tính tổng số dư từ các ví
    wallets = Wallet.objects.all()
    current_balance = sum(float(w.balance) for w in wallets)
    available_balance = sum(float(w.balance) for w in wallets if not w.exclude_from_total)
    
    result = {
        "total_income": float(income),
        "total_expense": float(expense),
        "balance": float(income - expense),
        "transaction_count": count,
        "current_balance": current_balance,
        "available_balance": available_balance,
    }
    
    
    # Return result directly
    # cache.set(cache_key, result, 300)
    
    return result


@router.get("/category-breakdown", response=List[CategoryBreakdown], summary="Get category breakdown for pie chart")
def get_category_breakdown(request, start_date: str = None, end_date: str = None):
    """
    Get spending breakdown by category for pie chart
    """
    # Parse dates
    if start_date:
        start = datetime.fromisoformat(start_date)
    else:
        start = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    if end_date:
        end = datetime.fromisoformat(end_date)
    else:
        end = timezone.now()
    
    
    # No caching for real-time updates
    
    # Aggregate by category
    transactions = Transaction.objects.filter(
        transaction_type='expense',
        date__gte=start,
        date__lte=end,
        category__isnull=False
    ).values('category__name').annotate(
        total=Sum('amount')
    ).order_by('-total')
    
    total_expense = sum(t['total'] for t in transactions)
    
    result = [
        {
            "category": t['category__name'],
            "amount": float(t['total']),
            "percentage": (float(t['total']) / float(total_expense) * 100) if total_expense > 0 else 0
        }
        for t in transactions
    ]
    
    
    # Return result directly
    # cache.set(cache_key, result, 300)
    return result


@router.get("/monthly-comparison", response=List[MonthlyComparison], summary="Get monthly comparison for bar chart")
def get_monthly_comparison(request, months: int = 6):
    """
    Get income/expense comparison for last N months.
    Only returns months that have at least one transaction.
    """
    
    # No caching for real-time updates
    
    result = []
    now = timezone.now()
    
    for i in range(months - 1, -1, -1):
        month_start = (now - timedelta(days=30 * i)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if i == 0:
            month_end = now
        else:
            month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        # Check if there are any transactions in this month
        has_transactions = Transaction.objects.filter(
            date__gte=month_start,
            date__lte=month_end
        ).exists()
        
        if not has_transactions:
            continue  # Skip months with no transactions
        
        income = Transaction.objects.filter(
            transaction_type='income',
            date__gte=month_start,
            date__lte=month_end
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        expense = Transaction.objects.filter(
            transaction_type='expense',
            date__gte=month_start,
            date__lte=month_end
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        result.append({
            "month": month_start.strftime("%Y-%m"),
            "income": float(income),
            "expense": float(expense),
            "balance": float(income - expense),
        })
    
    
    # Return result directly
    # cache.set(cache_key, result, 300)
    return result


@router.get("/trends", summary="Get spending trends for line chart")
def get_trends(request, days: int = 30):
    """
    Get daily spending trends for line chart
    """
    
    # No caching for real-time updates
    
    end_date = timezone.now()
    start_date = end_date - timedelta(days=days)
    
    # Aggregate by date
    transactions = Transaction.objects.filter(
        date__gte=start_date,
        date__lte=end_date
    ).extra(
        select={'day': "DATE(date)"}
    ).values('day', 'transaction_type').annotate(
        total=Sum('amount')
    )
    
    # Group by date
    daily_data = {}
    for t in transactions:
        day = t['day'].strftime('%Y-%m-%d')
        if day not in daily_data:
            daily_data[day] = {'income': 0, 'expense': 0}
        daily_data[day][t['transaction_type']] = float(t['total'])
    
    result = [
        {
            "date": day,
            "income": data['income'],
            "expense": data['expense'],
            "balance": data['income'] - data['expense'],
        }
        for day, data in sorted(daily_data.items())
    ]
    
    
    # Return result directly
    # cache.set(cache_key, result, 300)
    return result

