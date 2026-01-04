"""
Transaction CRUD API endpoints
"""
from ninja import Router, File
from ninja.files import UploadedFile
from typing import List, Optional, Dict
from pydantic import BaseModel
from datetime import datetime
from ..models import Transaction, Wallet, Category
from ..services.nlp_service import nlp_service
from ..services.ocr_service import ocr_service
from ..services.budget_service import budget_service
from datetime import datetime as dt

router = Router(tags=["transactions"])


class TransactionIn(BaseModel):
    wallet_id: int
    category_id: Optional[int] = None
    amount: str
    description: str = ""
    transaction_type: str = "expense"
    contact_person: Optional[str] = None
    date: Optional[datetime] = None


class TransactionOut(BaseModel):
    id: int
    wallet_id: int
    wallet_name: str
    category_id: Optional[int]
    category_name: Optional[str]
    amount: str
    description: str
    transaction_type: str
    contact_person: Optional[str]
    date: str
    created_at: str
    
    class Config:
        from_attributes = True


@router.get("", response=List[TransactionOut], summary="List all transactions")
def list_transactions(
    request, 
    limit: int = 50, 
    offset: int = 0,
    start_date: str = None,
    end_date: str = None,
    wallet_id: int = None,
    transaction_type: str = None,
    category_id: int = None
):
    """
    Get all transactions with filtering and pagination.
    Dates should be in ISO format (YYYY-MM-DD).
    """
    qs = Transaction.objects.select_related('wallet', 'category').all()
    
    # Apply Filters
    if start_date:
        qs = qs.filter(date__gte=start_date)
    if end_date:
        # If end_date is just YYYY-MM-DD, we should include the whole day
        # If it has time, exact match
        if len(end_date) == 10:  # Date only
            qs = qs.filter(date__date__lte=end_date)
        else:
            qs = qs.filter(date__lte=end_date)
            
    if wallet_id:
        qs = qs.filter(wallet_id=wallet_id)
        
    if transaction_type:
        qs = qs.filter(transaction_type=transaction_type)
        
    if category_id:
        qs = qs.filter(category_id=category_id)
        
    transactions = qs[offset:offset+limit]
    
    return [
        {
            "id": t.id,
            "wallet_id": t.wallet.id,
            "wallet_name": t.wallet.name,
            "category_id": t.category.id if t.category else None,
            "category_name": t.category.name if t.category else None,
            "amount": str(t.amount),
            "description": t.description,
            "transaction_type": t.transaction_type,
            "contact_person": t.contact_person,
            "date": t.date.isoformat(),
            "created_at": t.created_at.isoformat(),
        }
        for t in transactions
    ]


@router.get("/{transaction_id}", response=TransactionOut, summary="Get transaction by ID")
def get_transaction(request, transaction_id: int):
    """Get a specific transaction"""
    transaction = Transaction.objects.select_related('wallet', 'category').get(id=transaction_id)
    return {
        "id": transaction.id,
        "wallet_id": transaction.wallet.id,
        "wallet_name": transaction.wallet.name,
        "category_id": transaction.category.id if transaction.category else None,
        "category_name": transaction.category.name if transaction.category else None,
        "amount": str(transaction.amount),
        "description": transaction.description,
        "transaction_type": transaction.transaction_type,
        "contact_person": transaction.contact_person,
        "date": transaction.date.isoformat(),
        "created_at": transaction.created_at.isoformat(),
    }


@router.post("", response=TransactionOut, summary="Create new transaction")
def create_transaction(request, data: TransactionIn):
    """Create a new transaction with budget checking"""
    wallet = Wallet.objects.get(id=data.wallet_id)
    category = Category.objects.get(id=data.category_id) if data.category_id else None
    
    # Check budget if this is an expense
    budget_warning = None
    if data.transaction_type == "expense" and category:
        transaction_date = data.date if data.date else dt.now()
        # Get period dates (simplified - assumes monthly)
        from datetime import date
        period_start = date(transaction_date.year, transaction_date.month, 1)
        from calendar import monthrange
        period_end = date(transaction_date.year, transaction_date.month, monthrange(transaction_date.year, transaction_date.month)[1])
        
        budget_check = budget_service.check_budget(category, data.amount, period_start, period_end)
        if budget_check.get("warning"):
            budget_warning = budget_check["warning"]
    
    transaction = Transaction.objects.create(
        wallet=wallet,
        category=category,
        amount=data.amount,
        description=data.description,
        transaction_type=data.transaction_type,
        contact_person=data.contact_person,
        date=data.date if data.date else None,
    )
    
    response = {
        "id": transaction.id,
        "wallet_id": transaction.wallet.id,
        "wallet_name": transaction.wallet.name,
        "category_id": transaction.category.id if transaction.category else None,
        "category_name": transaction.category.name if transaction.category else None,
        "amount": str(transaction.amount),
        "description": transaction.description,
        "transaction_type": transaction.transaction_type,
        "contact_person": transaction.contact_person,
        "date": transaction.date.isoformat(),
        "created_at": transaction.created_at.isoformat(),
    }
    
    if budget_warning:
        response["budget_warning"] = budget_warning
    
    return response


@router.put("/{transaction_id}", response=TransactionOut, summary="Update transaction")
def update_transaction(request, transaction_id: int, data: TransactionIn):
    """Update an existing transaction"""
    transaction = Transaction.objects.get(id=transaction_id)
    transaction.wallet = Wallet.objects.get(id=data.wallet_id)
    transaction.category = Category.objects.get(id=data.category_id) if data.category_id else None
    transaction.amount = data.amount
    transaction.description = data.description
    transaction.transaction_type = data.transaction_type
    transaction.contact_person = data.contact_person
    if data.date:
        transaction.date = data.date
    transaction.save()
    
    return {
        "id": transaction.id,
        "wallet_id": transaction.wallet.id,
        "wallet_name": transaction.wallet.name,
        "category_id": transaction.category.id if transaction.category else None,
        "category_name": transaction.category.name if transaction.category else None,
        "amount": str(transaction.amount),
        "description": transaction.description,
        "transaction_type": transaction.transaction_type,
        "contact_person": transaction.contact_person,
        "date": transaction.date.isoformat(),
        "created_at": transaction.created_at.isoformat(),
    }


@router.delete("/{transaction_id}", summary="Delete transaction")
def delete_transaction(request, transaction_id: int):
    """Delete a transaction"""
    transaction = Transaction.objects.get(id=transaction_id)
    transaction.delete()
    return {"success": True, "message": "Transaction deleted"}


class QuickAddRequest(BaseModel):
    text: str


class QuickAddResponse(BaseModel):
    transactions: List[Dict]
    message: str


@router.post("/parse/quick-add", response=QuickAddResponse, summary="Quick Add by Text (NLP)")
def quick_add_transactions(request, data: QuickAddRequest):
    """
    Parse natural language text and extract transaction information.
    Returns draft transactions for user confirmation.
    """
    # Parse text using NLP service
    parsed_transactions = nlp_service.parse_transactions(data.text)
    
    if not parsed_transactions:
        return {
            "transactions": [],
            "message": "Could not parse transactions from text. Please try again with clearer description."
        }
    
    # Map to category IDs if categories exist
    result_transactions = []
    for tx in parsed_transactions:
        # Find or create category
        category = None
        if tx.get('category'):
            category, _ = Category.objects.get_or_create(
                name=tx['category'],
                defaults={'icon': '', 'description': ''}
            )
        
        # Find wallet by type or create default
        wallet = Wallet.objects.filter(wallet_type=tx.get('wallet', 'cash')).first()
        if not wallet:
            wallet = Wallet.objects.filter(wallet_type='cash').first()
            if not wallet:
                wallet = Wallet.objects.create(
                    name="Tiền mặt",
                    wallet_type='cash'
                )
        
        result_transactions.append({
            "amount": str(tx['amount']),
            "category_id": category.id if category else None,
            "category_name": category.name if category else tx.get('category', 'Khác'),
            "wallet_id": wallet.id,
            "wallet_name": wallet.name,
            "description": tx.get('description', ''),
            "transaction_type": tx.get('type', 'expense'),
            "date": tx.get('date', datetime.now()).isoformat() if isinstance(tx.get('date'), datetime) else None,
        })
    
    return {
        "transactions": result_transactions,
        "message": f"Found {len(result_transactions)} transaction(s). Please review and confirm."
    }


@router.post("/parse/receipt", summary="Upload Receipt (OCR)")
def upload_receipt(request, file: UploadedFile = File(...)):
    """
    Upload receipt image and extract transaction information using OCR.
    Returns extracted data for user confirmation.
    """
    # Read image data
    image_data = file.read()
    
    # Process with OCR service
    extracted = ocr_service.process_receipt(image_data, file.name)
    
    if extracted.get('error'):
        return {
            "success": False,
            "error": extracted['error'],
            "data": None
        }
    
    # Map to transaction format
    result = {
        "merchant": extracted.get('merchant'),
        "amount": extracted.get('amount'),
        "date": extracted.get('date'),
        "items": extracted.get('items', []),
        "raw_text": extracted.get('description', ''),
        "category": extracted.get('category'),
    }
    
    # Find or create category
    category_id = None
    if result['category']:
        category, _ = Category.objects.get_or_create(
            name=result['category'],
            defaults={'icon': '', 'description': ''}
        )
        category_id = category.id
    
    # Find default wallet
    wallet = Wallet.objects.filter(wallet_type='cash').first()
    if not wallet:
        wallet = Wallet.objects.create(
            name="Tiền mặt",
            wallet_type='cash'
        )
    
    result['category_id'] = category_id
    result['wallet_id'] = wallet.id
    result['wallet_name'] = wallet.name
    
    return {
        "success": True,
        "data": result,
        "message": "Receipt processed successfully. Please review and confirm."
    }

