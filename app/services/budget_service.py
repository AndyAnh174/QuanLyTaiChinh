"""
Budget service for budget calculations and warnings
"""
from typing import Dict, Optional
from decimal import Decimal
from ..models import Budget, Transaction, Category


class BudgetService:
    """
    Service for budget-related calculations and checks
    """
    
    WARNING_THRESHOLDS = [80, 100, 120]  # Percentage thresholds for warnings
    
    def check_budget(self, category: Category, amount: Decimal, period_start, period_end) -> Dict:
        """
        Check if a transaction would exceed budget
        
        Args:
            category: Category to check
            amount: Transaction amount
            period_start: Period start date
            period_end: Period end date
        
        Returns:
            Dictionary with budget status and warnings
        """
        # Find active budget for this category and period
        budget = Budget.objects.filter(
            category=category,
            start_date__lte=period_end,
            end_date__gte=period_start,
            is_active=True
        ).first()
        
        if not budget:
            return {
                "has_budget": False,
                "warning": None,
                "status": "ok"
            }
        
        # Calculate current spending
        # Ensure all are Decimal
        amount_dec = Decimal(str(amount))
        budget_amount = budget.amount
        current_spent = Decimal(str(budget.get_spent_amount()))
        
        new_total = current_spent + amount_dec
        
        if budget_amount > 0:
            percentage = (new_total / budget_amount) * 100
        else:
            percentage = 0
        
        # Determine warning level
        warning = None
        status = "ok"
        
        if percentage >= 120:
            warning = f"Cảnh báo: Giao dịch này sẽ làm bạn vượt quá {percentage:.1f}% ngân sách ({budget_amount:,.0f} VNĐ)!"
            status = "critical"
        elif percentage >= 100:
            warning = f"Cẩn thận: Giao dịch này sẽ làm bạn vượt quá ngân sách ({budget_amount:,.0f} VNĐ)!"
            status = "warning"
        elif percentage >= 80:
            remaining = budget.get_remaining_amount() - amount_dec
            warning = f"Lưu ý: Bạn đã sử dụng {percentage:.1f}% ngân sách. Còn {remaining:,.0f} VNĐ."
            status = "caution"
        
        return {
            "has_budget": True,
            "budget_id": budget.id,
            "budget_amount": float(budget_amount),
            "current_spent": float(current_spent),
            "new_total": float(new_total),
            "percentage": float(percentage),
            "remaining": float(budget.get_remaining_amount() - amount_dec),
            "warning": warning,
            "status": status
        }
    
    def get_budget_status(self, budget: Budget) -> Dict:
        """
        Get current status of a budget
        
        Args:
            budget: Budget instance
        
        Returns:
            Dictionary with budget status
        """
        spent = budget.get_spent_amount()
        remaining = budget.get_remaining_amount()
        percentage = budget.get_percentage_used()
        
        status = "ok"
        if percentage >= 120:
            status = "critical"
        elif percentage >= 100:
            status = "warning"
        elif percentage >= 80:
            status = "caution"
        
        return {
            "budget_id": budget.id,
            "category": budget.category.name,
            "amount": float(budget.amount),
            "spent": spent,
            "remaining": remaining,
            "percentage": percentage,
            "status": status,
            "period": budget.get_period_display(),
            "start_date": budget.start_date.isoformat(),
            "end_date": budget.end_date.isoformat(),
        }


# Singleton instance
budget_service = BudgetService()

