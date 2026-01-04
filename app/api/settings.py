"""
Settings and System Data API endpoints
"""
from ninja import Router
from ..models import Transaction, Budget, RecurringTransaction, Wallet, Category, ChatSession

router = Router(tags=["settings"])

@router.post("/reset-data", summary="Reset all user data")
def reset_data(request):
    """
    Delete all user-generated data:
    - Transactions
    - Budgets
    - Recurring Transactions
    - Chat History (Sessions & Messages)
    - Wallets (Reset to default/empty)
    - Categories (Optional: could keep defaults, but for now we wipe)
    """
    # 1. Delete Transactions (this updates wallet balances via signals, but we'll wipe wallets anyway)
    Transaction.objects.all().delete()
    
    # 2. Delete Budgets
    Budget.objects.all().delete()
    
    # 3. Delete Recurring
    RecurringTransaction.objects.all().delete()
    
    # 4. Delete Chat History
    ChatSession.objects.all().delete()
    
    # 5. Reset Wallets (Delete all and create default 'Tiền mặt' or just delete all)
    # Deleting all is cleaner, the app logic elsewhere creates default wallet if missing.
    Wallet.objects.all().delete()
    
    # 6. Categories - Let's keep them for convenience or wipe? 
    # User said "Delete ALL data", usually implies a factory reset.
    Category.objects.all().delete()
    
    return {"success": True, "message": "All data has been reset successfully."}
