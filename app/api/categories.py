"""
Category CRUD API endpoints
"""
from ninja import Router
from typing import List
from pydantic import BaseModel
from ..models import Category

router = Router(tags=["categories"])


class CategoryIn(BaseModel):
    name: str
    icon: str = ""
    description: str = ""


class CategoryOut(BaseModel):
    id: int
    name: str
    icon: str
    description: str
    created_at: str


@router.get("", response=List[CategoryOut], summary="List all categories")
def list_categories(request):
    """Get all categories"""
    categories = Category.objects.all()
    return [
        {
            "id": cat.id,
            "name": cat.name,
            "icon": cat.icon,
            "description": cat.description,
            "created_at": cat.created_at.isoformat() if cat.created_at else "",
        }
        for cat in categories
    ]


@router.get("/{category_id}", response=CategoryOut, summary="Get category by ID")
def get_category(request, category_id: int):
    """Get a specific category"""
    cat = Category.objects.get(id=category_id)
    return {
        "id": cat.id,
        "name": cat.name,
        "icon": cat.icon,
        "description": cat.description,
        "created_at": cat.created_at.isoformat() if cat.created_at else "",
    }


@router.post("", response=CategoryOut, summary="Create new category")
def create_category(request, data: CategoryIn):
    """Create a new category"""
    cat = Category.objects.create(**data.dict())
    return {
        "id": cat.id,
        "name": cat.name,
        "icon": cat.icon,
        "description": cat.description,
        "created_at": cat.created_at.isoformat() if cat.created_at else "",
    }


@router.put("/{category_id}", response=CategoryOut, summary="Update category")
def update_category(request, category_id: int, data: CategoryIn):
    """Update an existing category"""
    cat = Category.objects.get(id=category_id)
    for key, value in data.dict().items():
        setattr(cat, key, value)
    cat.save()
    return {
        "id": cat.id,
        "name": cat.name,
        "icon": cat.icon,
        "description": cat.description,
        "created_at": cat.created_at.isoformat() if cat.created_at else "",
    }


@router.delete("/{category_id}", summary="Delete category")
def delete_category(request, category_id: int):
    """Delete a category"""
    category = Category.objects.get(id=category_id)
    category.delete()
    return {"success": True, "message": "Category deleted"}

