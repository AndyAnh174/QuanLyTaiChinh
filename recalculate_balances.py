import os
import django
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.conf import settings
from app.models import Wallet, Transaction
from app.signals import get_signed_amount

def recalculate_balances():
    print("--- DEBUG INFO ---")
    print(f"DB Host: {settings.DATABASES['default']['HOST']}")
    print(f"DB Name: {settings.DATABASES['default']['NAME']}")
    
    print("\nRecalculating wallet balances...")
    
    # 1. Reset all wallets to 0
    wallets = list(Wallet.objects.all())
    print(f"Found {len(wallets)} wallets.")
    for wallet in wallets:
        wallet.balance = Decimal(0)
        wallet.save()
        print(f"Reset '{wallet.name}' (ID: {wallet.id}) to 0")
    
    # 2. Re-process all transactions
    transactions = Transaction.objects.all().order_by('date', 'created_at')
    count = transactions.count()
    print(f"Found {count} transactions.")
    
    processed = 0
    for tx in transactions:
        wallet = tx.wallet
        amount = get_signed_amount(tx)
        print(f"Tx {tx.id}: {tx.transaction_type} {tx.amount} -> Wallet {wallet.id} ({amount})")
        wallet.balance += amount
        wallet.save()
        processed += 1
        
    print(f"Processed {processed} transactions.")

    # 3. Print final balances
    print("\n--- FINAL BALANCES ---")
    for wallet in Wallet.objects.all():
        print(f"Wallet '{wallet.name}' (ID: {wallet.id}): {wallet.balance:,.2f}")

if __name__ == '__main__':
    recalculate_balances()
