"""
Debts & Loans Management API endpoints
"""
from ninja import Router
from typing import Dict
from pydantic import BaseModel
from django.db.models import Sum, Q
from ..models import Transaction

router = Router(tags=["debts"])


class DebtSummary(BaseModel):
    total_debt_borrow: float  # Total money borrowed (not yet repaid)
    total_debt_repay: float  # Total money repaid
    net_debt: float  # Net debt (borrow - repay)
    total_loan: float  # Total money lent (not yet collected)
    total_collect: float  # Total money collected
    net_lending: float  # Net lending (loan - collect)


@router.get("/summary", response=DebtSummary, summary="Get debt and loan summary")
def get_debt_summary(request):
    """
    Calculate total debts and loans
    """
    # Calculate debts (money borrowed)
    debt_borrow = Transaction.objects.filter(
        transaction_type='debt_borrow'
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    debt_repay = Transaction.objects.filter(
        transaction_type='debt_repay'
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Calculate loans (money lent)
    debt_loan = Transaction.objects.filter(
        transaction_type='debt_loan'
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    debt_collect = Transaction.objects.filter(
        transaction_type='debt_collect'
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    return {
        "total_debt_borrow": float(debt_borrow),
        "total_debt_repay": float(debt_repay),
        "net_debt": float(debt_borrow - debt_repay),
        "total_loan": float(debt_loan),
        "total_collect": float(debt_collect),
        "net_lending": float(debt_loan - debt_collect),
    }


@router.get("", summary="List all debt/loan transactions")
def list_debts(request, debt_type: str = "all"):
    """
    List debt and loan transactions
    debt_type: 'all', 'borrow', 'repay', 'loan', 'collect'
    """
    if debt_type == "all":
        transactions = Transaction.objects.filter(
            transaction_type__in=['debt_borrow', 'debt_repay', 'debt_loan', 'debt_collect']
        ).select_related('wallet', 'category').order_by('-date')
    elif debt_type == "borrow":
        transactions = Transaction.objects.filter(transaction_type='debt_borrow')
    elif debt_type == "repay":
        transactions = Transaction.objects.filter(transaction_type='debt_repay')
    elif debt_type == "loan":
        transactions = Transaction.objects.filter(transaction_type='debt_loan')
    elif debt_type == "collect":
        transactions = Transaction.objects.filter(transaction_type='debt_collect')
    else:
        transactions = Transaction.objects.none()
    
    return [
        {
            "id": t.id,
            "transaction_type": t.transaction_type,
            "amount": str(t.amount),
            "description": t.description,
            "contact_person": t.contact_person,
            "date": t.date.isoformat(),
            "wallet": t.wallet.name,
            "category": t.category.name if t.category else None,
        }
        for t in transactions
    ]

