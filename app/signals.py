from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from .models import Transaction
from decimal import Decimal

def get_signed_amount(instance):
    """
    Returns the amount with the correct sign based on transaction type.
    Positive for adding to wallet, Negative for subtracting.
    """
    # Types that increase balance
    if instance.transaction_type in ['income', 'debt_borrow', 'debt_collect']:
        return Decimal(str(instance.amount))
    # Types that decrease balance
    elif instance.transaction_type in ['expense', 'debt_loan', 'debt_repay']:
        return -Decimal(str(instance.amount))
    return Decimal(0)

@receiver(post_save, sender=Transaction)
def update_wallet_balance_on_save(sender, instance, created, **kwargs):
    """
    Update wallet balance when a transaction is created.
    Note: Updates are handled by pre_save to account for diffs.
    So this handles ONLY newly created transactions.
    """
    if created:
        wallet = instance.wallet
        amount_to_add = get_signed_amount(instance)
        wallet.balance += amount_to_add
        wallet.save()

@receiver(pre_save, sender=Transaction)
def update_wallet_balance_on_change(sender, instance, **kwargs):
    """
    Handle updates to an existing transaction.
    Reverts the old effect and applies the new effect.
    """
    if instance.pk:  # Existing instance
        try:
            old_instance = Transaction.objects.get(pk=instance.pk)
            wallet = old_instance.wallet
            
            # Revert old transaction (subtract the signed amount)
            # If it was +100 income, we subtract 100. If it was -50 expense, we subtract -50 (add 50).
            wallet.balance -= get_signed_amount(old_instance)
            wallet.save()
            
            # Now apply the new transaction to the NEW wallet (could be different)
            # But wait, post_save handles 'created', but here we are in update.
            # post_save won't see 'created=True' for updates.
            # We must apply the new amount here OR let post_save handle it if we flag it.
            # Actually, simpler: Revert old here. Apply new here.
            
            new_wallet = instance.wallet
            new_wallet.balance += get_signed_amount(instance)
            new_wallet.save()
            
        except Transaction.DoesNotExist:
            pass  # Should not happen

@receiver(post_delete, sender=Transaction)
def update_wallet_balance_on_delete(sender, instance, **kwargs):
    """
    Revert transaction effect when deleted.
    And delete vector from Qdrant.
    """
    wallet = instance.wallet
    # If it was income (+), we subtract. If expense (-), we add (subtract negative).
    wallet.balance -= get_signed_amount(instance)
    wallet.save()
    
    # Trigger Synchronous Vector Deletion
    try:
        from app.services.vector_service import vector_service
        vector_service.delete_transaction(instance.id)
    except Exception as e:
        print(f"Signal Error: Could not delete vector: {e}")

@receiver(post_save, sender=Transaction)
def sync_vector_on_save(sender, instance, **kwargs):
    """
    Sync vector to Qdrant on save (create/update).
    """
    if instance.description:
        try:
            from app.services.vector_service import vector_service
            vector_service.sync_transaction(instance)
        except Exception as e:
            print(f"Signal Error: Could not sync vector: {e}")
