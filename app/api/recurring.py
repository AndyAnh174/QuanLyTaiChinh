"""
Recurring Transaction API endpoints
"""
from ninja import Router
from typing import List, Optional
from pydantic import BaseModel
from datetime import date
from ..models import RecurringTransaction, Wallet, Category

router = Router(tags=["recurring"])


class RecurringTransactionIn(BaseModel):
    name: str
    wallet_id: int
    category_id: Optional[int] = None
    amount: str
    frequency: str = "monthly"
    next_run_date: date
    transaction_type: str = "expense"
    description: str = ""


class RecurringTransactionOut(BaseModel):
    id: int
    name: str
    wallet_id: int
    wallet_name: str
    category_id: Optional[int]
    category_name: Optional[str]
    amount: str
    frequency: str
    next_run_date: str
    is_active: bool
    transaction_type: str
    description: str
    created_at: str


@router.get("", response=List[RecurringTransactionOut], summary="List all recurring transactions")
def list_recurring_transactions(request):
    """Get all recurring transactions"""
    recurring = RecurringTransaction.objects.select_related('wallet', 'category').all()
    return [
        {
            "id": r.id,
            "name": r.name,
            "wallet_id": r.wallet.id,
            "wallet_name": r.wallet.name,
            "category_id": r.category.id if r.category else None,
            "category_name": r.category.name if r.category else None,
            "amount": str(r.amount),
            "frequency": r.frequency,
            "next_run_date": r.next_run_date.isoformat(),
            "is_active": r.is_active,
            "transaction_type": r.transaction_type,
            "description": r.description,
            "created_at": r.created_at.isoformat(),
        }
        for r in recurring
    ]


@router.get("/{recurring_id}", response=RecurringTransactionOut, summary="Get recurring transaction by ID")
def get_recurring_transaction(request, recurring_id: int):
    """Get a specific recurring transaction"""
    recurring = RecurringTransaction.objects.select_related('wallet', 'category').get(id=recurring_id)
    return {
        "id": recurring.id,
        "name": recurring.name,
        "wallet_id": recurring.wallet.id,
        "wallet_name": recurring.wallet.name,
        "category_id": recurring.category.id if recurring.category else None,
        "category_name": recurring.category.name if recurring.category else None,
        "amount": str(recurring.amount),
        "frequency": recurring.frequency,
        "next_run_date": recurring.next_run_date.isoformat(),
        "is_active": recurring.is_active,
        "transaction_type": recurring.transaction_type,
        "description": recurring.description,
        "created_at": recurring.created_at.isoformat(),
    }


@router.post("", response=RecurringTransactionOut, summary="Create new recurring transaction")
def create_recurring_transaction(request, data: RecurringTransactionIn):
    """Create a new recurring transaction"""
    wallet = Wallet.objects.get(id=data.wallet_id)
    category = Category.objects.get(id=data.category_id) if data.category_id else None
    
    recurring = RecurringTransaction.objects.create(
        name=data.name,
        wallet=wallet,
        category=category,
        amount=data.amount,
        frequency=data.frequency,
        next_run_date=data.next_run_date,
        transaction_type=data.transaction_type,
        description=data.description,
    )
    
    return {
        "id": recurring.id,
        "name": recurring.name,
        "wallet_id": recurring.wallet.id,
        "wallet_name": recurring.wallet.name,
        "category_id": recurring.category.id if recurring.category else None,
        "category_name": recurring.category.name if recurring.category else None,
        "amount": str(recurring.amount),
        "frequency": recurring.frequency,
        "next_run_date": recurring.next_run_date.isoformat(),
        "is_active": recurring.is_active,
        "transaction_type": recurring.transaction_type,
        "description": recurring.description,
        "created_at": recurring.created_at.isoformat(),
    }


@router.put("/{recurring_id}", response=RecurringTransactionOut, summary="Update recurring transaction")
def update_recurring_transaction(request, recurring_id: int, data: RecurringTransactionIn):
    """Update an existing recurring transaction"""
    recurring = RecurringTransaction.objects.get(id=recurring_id)
    recurring.name = data.name
    recurring.wallet = Wallet.objects.get(id=data.wallet_id)
    recurring.category = Category.objects.get(id=data.category_id) if data.category_id else None
    recurring.amount = data.amount
    recurring.frequency = data.frequency
    recurring.next_run_date = data.next_run_date
    recurring.transaction_type = data.transaction_type
    recurring.description = data.description
    recurring.save()
    
    return {
        "id": recurring.id,
        "name": recurring.name,
        "wallet_id": recurring.wallet.id,
        "wallet_name": recurring.wallet.name,
        "category_id": recurring.category.id if recurring.category else None,
        "category_name": recurring.category.name if recurring.category else None,
        "amount": str(recurring.amount),
        "frequency": recurring.frequency,
        "next_run_date": recurring.next_run_date.isoformat(),
        "is_active": recurring.is_active,
        "transaction_type": recurring.transaction_type,
        "description": recurring.description,
        "created_at": recurring.created_at.isoformat(),
    }


@router.delete("/{recurring_id}", summary="Delete recurring transaction")
def delete_recurring_transaction(request, recurring_id: int):
    """Delete a recurring transaction"""
    recurring = RecurringTransaction.objects.get(id=recurring_id)
    recurring.delete()
    return {"success": True, "message": "Recurring transaction deleted"}


@router.post("/{recurring_id}/toggle", summary="Toggle recurring transaction active status")
def toggle_recurring_transaction(request, recurring_id: int):
    """Toggle active status of a recurring transaction"""
    recurring = RecurringTransaction.objects.get(id=recurring_id)
    recurring.is_active = not recurring.is_active
    recurring.save()
    return {
        "success": True,
        "is_active": recurring.is_active,
        "message": f"Recurring transaction {'activated' if recurring.is_active else 'deactivated'}"
    }

