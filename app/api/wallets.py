"""
Wallet CRUD API endpoints
"""
from ninja import Router
from typing import List, Optional
from pydantic import BaseModel
from ..models import Wallet

router = Router(tags=["wallets"])


class TotalBalanceOut(BaseModel):
    """Tổng số dư tất cả các ví"""
    total_balance: float  # Tổng tất cả ví
    available_balance: float  # Tổng ví không tính tiết kiệm
    savings_balance: float  # Tổng ví tiết kiệm
    wallet_count: int
    wallets: List[dict]


@router.get("/total-balance", response=TotalBalanceOut, summary="Get total balance of all wallets")
def get_total_balance(request):
    """
    Lấy tổng số dư của tất cả các ví.
    - total_balance: Tổng tất cả ví
    - available_balance: Tổng ví chi tiêu hàng ngày (exclude_from_total=False)
    - savings_balance: Tổng ví tiết kiệm (exclude_from_total=True)
    """
    wallets = Wallet.objects.all()
    
    wallet_list = []
    total = 0
    available = 0
    savings = 0
    
    for w in wallets:
        balance = float(w.balance)
        total += balance
        
        if w.exclude_from_total:
            savings += balance
        else:
            available += balance
        
        wallet_list.append({
            "id": w.id,
            "name": w.name,
            "balance": balance,
            "wallet_type": w.wallet_type,
            "exclude_from_total": w.exclude_from_total,
        })
    
    return {
        "total_balance": total,
        "available_balance": available,
        "savings_balance": savings,
        "wallet_count": len(wallet_list),
        "wallets": wallet_list,
    }


class WalletIn(BaseModel):
    name: str
    wallet_type: str = "cash"
    exclude_from_total: bool = False


class WalletOut(BaseModel):
    id: int
    name: str
    balance: str
    wallet_type: str
    exclude_from_total: bool
    created_at: str


def _serialize_wallet(w):
    """Helper to serialize wallet to dict"""
    return {
        "id": w.id,
        "name": w.name,
        "balance": str(w.balance),
        "wallet_type": w.wallet_type,
        "exclude_from_total": w.exclude_from_total,
        "created_at": w.created_at.isoformat() if w.created_at else "",
    }


@router.get("", response=List[WalletOut], summary="List all wallets")
def list_wallets(request):
    """Get all wallets"""
    wallets = Wallet.objects.all()
    return [_serialize_wallet(w) for w in wallets]


@router.get("/{wallet_id}", response=WalletOut, summary="Get wallet by ID")
def get_wallet(request, wallet_id: int):
    """Get a specific wallet"""
    wallet = Wallet.objects.get(id=wallet_id)
    return _serialize_wallet(wallet)


@router.post("", response=WalletOut, summary="Create new wallet")
def create_wallet(request, data: WalletIn):
    """Create a new wallet"""
    wallet = Wallet.objects.create(**data.dict())
    return _serialize_wallet(wallet)


@router.put("/{wallet_id}", response=WalletOut, summary="Update wallet")
def update_wallet(request, wallet_id: int, data: WalletIn):
    """Update an existing wallet"""
    wallet = Wallet.objects.get(id=wallet_id)
    for key, value in data.dict().items():
        setattr(wallet, key, value)
    wallet.save()
    return _serialize_wallet(wallet)


@router.delete("/{wallet_id}", summary="Delete wallet")
def delete_wallet(request, wallet_id: int):
    """Delete a wallet"""
    wallet = Wallet.objects.get(id=wallet_id)
    wallet.delete()
    return {"success": True, "message": "Wallet deleted"}

