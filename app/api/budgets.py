"""
Budget Management API endpoints
"""
from ninja import Router
from typing import List, Optional
from pydantic import BaseModel
from datetime import date
from ..models import Budget, Category
from ..services.budget_service import budget_service

router = Router(tags=["budgets"])


class BudgetIn(BaseModel):
    category_id: int
    amount: str
    period: str = "monthly"
    start_date: date
    end_date: date


class BudgetOut(BaseModel):
    id: int
    category_id: int
    category_name: str
    amount: str
    period: str
    start_date: str
    end_date: str
    is_active: bool
    created_at: str


class BudgetStatusOut(BaseModel):
    budget_id: int
    category: str
    amount: float
    spent: float
    remaining: float
    percentage: float
    status: str
    period: str
    start_date: str
    end_date: str


@router.get("", response=List[BudgetOut], summary="List all budgets")
def list_budgets(request):
    """Get all budgets"""
    budgets = Budget.objects.select_related('category').all()
    return [
        {
            "id": b.id,
            "category_id": b.category.id,
            "category_name": b.category.name,
            "amount": str(b.amount),
            "period": b.period,
            "start_date": b.start_date.isoformat(),
            "end_date": b.end_date.isoformat(),
            "is_active": b.is_active,
            "created_at": b.created_at.isoformat(),
        }
        for b in budgets
    ]


@router.get("/{budget_id}", response=BudgetOut, summary="Get budget by ID")
def get_budget(request, budget_id: int):
    """Get a specific budget"""
    budget = Budget.objects.select_related('category').get(id=budget_id)
    return {
        "id": budget.id,
        "category_id": budget.category.id,
        "category_name": budget.category.name,
        "amount": str(budget.amount),
        "period": budget.period,
        "start_date": budget.start_date.isoformat(),
        "end_date": budget.end_date.isoformat(),
        "is_active": budget.is_active,
        "created_at": budget.created_at.isoformat(),
    }


@router.get("/{budget_id}/status", response=BudgetStatusOut, summary="Get budget status")
def get_budget_status(request, budget_id: int):
    """Get budget status with spent/remaining amounts"""
    budget = Budget.objects.select_related('category').get(id=budget_id)
    status = budget_service.get_budget_status(budget)
    return status


@router.post("", response=BudgetOut, summary="Create new budget")
def create_budget(request, data: BudgetIn):
    """Create a new budget"""
    category = Category.objects.get(id=data.category_id)
    budget = Budget.objects.create(
        category=category,
        amount=data.amount,
        period=data.period,
        start_date=data.start_date,
        end_date=data.end_date,
    )
    return {
        "id": budget.id,
        "category_id": budget.category.id,
        "category_name": budget.category.name,
        "amount": str(budget.amount),
        "period": budget.period,
        "start_date": budget.start_date.isoformat(),
        "end_date": budget.end_date.isoformat(),
        "is_active": budget.is_active,
        "created_at": budget.created_at.isoformat(),
    }


@router.put("/{budget_id}", response=BudgetOut, summary="Update budget")
def update_budget(request, budget_id: int, data: BudgetIn):
    """Update an existing budget"""
    budget = Budget.objects.get(id=budget_id)
    budget.category = Category.objects.get(id=data.category_id)
    budget.amount = data.amount
    budget.period = data.period
    budget.start_date = data.start_date
    budget.end_date = data.end_date
    budget.save()
    
    return {
        "id": budget.id,
        "category_id": budget.category.id,
        "category_name": budget.category.name,
        "amount": str(budget.amount),
        "period": budget.period,
        "start_date": budget.start_date.isoformat(),
        "end_date": budget.end_date.isoformat(),
        "is_active": budget.is_active,
        "created_at": budget.created_at.isoformat(),
    }


@router.delete("/{budget_id}", summary="Delete budget")
def delete_budget(request, budget_id: int):
    """Delete a budget"""
    budget = Budget.objects.get(id=budget_id)
    budget.delete()
    return {"success": True, "message": "Budget deleted"}

