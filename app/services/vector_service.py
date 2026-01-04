"""
Vector service for syncing transaction vectors with Qdrant
"""
from typing import Optional, List
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from ..models import Transaction
from ..qdrant_client import get_qdrant_service
from .embedding_service import embedding_service
import uuid


class VectorService:
    """
    Service for managing transaction vectors in Qdrant
    """
    
    def __init__(self):
        self.qdrant = get_qdrant_service()
    
    def sync_transaction(self, transaction: Transaction) -> bool:
        """
        Sync a transaction to Qdrant as a vector
        
        Args:
            transaction: Transaction instance
        
        Returns:
            Success status
        """
        try:
            # Generate embedding for transaction description
            text = self._build_search_text(transaction)
            embedding = embedding_service.get_embedding(text)
            
            # Prepare payload
            payload = {
                "transaction_id": transaction.id,
                "description": transaction.description,
                "category": transaction.category.name if transaction.category else None,
                "amount": float(transaction.amount),
                "transaction_type": transaction.transaction_type,
                "date": transaction.date.isoformat(),
            }
            
            # Use transaction ID as point ID (Qdrant supports uint64)
            point_id = transaction.id
            if not point_id:
                # Fallback for unsaved objects? Should be saved by now.
                # If no ID, we can't sync reliably with Int ID requirement.
                print("Warning: Transaction has no ID, skipping sync")
                return False
            
            # Upsert to Qdrant
            # Note: qdrant_client accepts int or str for id
            success = self.qdrant.upsert_point(
                point_id=point_id,
                vector=embedding,
                payload=payload
            )
            
            # Note: We don't store UUID anymore since we use DB Int ID
            
            return success
            
            return success
        except Exception as e:
            print(f"Error syncing transaction to Qdrant: {e}")
            return False
    
    def delete_transaction(self, transaction_id: int, point_id: Optional[str] = None) -> bool:
        """
        Delete transaction vector from Qdrant
        
        Args:
            transaction_id: Transaction ID
            point_id: Optional Qdrant point ID (if not provided, uses transaction_id)
        
        Returns:
            Success status
        """
        try:
            # Use int ID to match sync method
            # point_id argument is now somewhat redundant if we always use transaction_id as point_id
            pid = transaction_id
            return self.qdrant.delete_point(pid)
        except Exception as e:
            print(f"Error deleting transaction from Qdrant: {e}")
            return False
    
    def sync_batch(self, transactions: List[Transaction]) -> int:
        """
        Sync multiple transactions to Qdrant in batch
        
        Args:
            transactions: List of Transaction instances
        
        Returns:
            Number of successfully synced transactions
        """
        success_count = 0
        for transaction in transactions:
            if self.sync_transaction(transaction):
                success_count += 1
        return success_count
    
    def _build_search_text(self, transaction: Transaction) -> str:
        """Build searchable text from transaction"""
        parts = []
        if transaction.description:
            parts.append(transaction.description)
        if transaction.category:
            parts.append(transaction.category.name)
        if transaction.contact_person:
            parts.append(transaction.contact_person)
        return " ".join(parts)
    
    def _is_uuid(self, value: str) -> bool:
        """Check if string is a valid UUID"""
        try:
            uuid.UUID(value)
            return True
        except:
            return False


# Singleton instance
vector_service = VectorService()


# Signal handlers for automatic sync
@receiver(post_save, sender=Transaction)
def sync_transaction_to_qdrant(sender, instance, created, **kwargs):
    """Automatically sync transaction to Qdrant on save"""
    # Only sync if description exists (has content to embed)
    if instance.description:
        vector_service.sync_transaction(instance)


@receiver(post_delete, sender=Transaction)
def delete_transaction_from_qdrant(sender, instance, **kwargs):
    """Automatically delete transaction from Qdrant on delete"""
    if instance.qdrant_point_id:
        vector_service.delete_transaction(
            instance.id,
            str(instance.qdrant_point_id)
        )
    else:
        vector_service.delete_transaction(instance.id)

