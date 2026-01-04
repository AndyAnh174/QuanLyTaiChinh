"""
Celery tasks for async vector operations
"""
from celery import shared_task
from ..services.vector_service import vector_service
from ..models import Transaction


@shared_task
def sync_transaction_vector(transaction_id: int):
    """
    Sync a transaction to Qdrant asynchronously
    
    Args:
        transaction_id: Transaction ID to sync
    
    Returns:
        Success status
    """
    try:
        transaction = Transaction.objects.get(id=transaction_id)
        success = vector_service.sync_transaction(transaction)
        return {"success": success, "transaction_id": transaction_id}
    except Transaction.DoesNotExist:
        return {"success": False, "error": "Transaction not found"}
    except Exception as e:
        print(f"Error syncing transaction vector: {e}")
        return {"success": False, "error": str(e)}


@shared_task
def sync_transactions_batch(transaction_ids: list):
    """
    Sync multiple transactions to Qdrant in batch
    
    Args:
        transaction_ids: List of transaction IDs
    
    Returns:
        Number of successfully synced transactions
    """
    try:
        transactions = Transaction.objects.filter(id__in=transaction_ids)
        count = vector_service.sync_batch(list(transactions))
        return {"synced": count, "total": len(transaction_ids)}
    except Exception as e:
        print(f"Error in batch sync: {e}")
        return {"synced": 0, "total": len(transaction_ids), "error": str(e)}

@shared_task
def delete_transaction_vector(transaction_id: int):
    """
    Delete a transaction vector from Qdrant asynchronously
    """
    try:
        success = vector_service.delete_transaction(transaction_id)
        return {"success": success, "transaction_id": transaction_id}
    except Exception as e:
        print(f"Error deleting transaction vector: {e}")
        return {"success": False, "error": str(e)}
