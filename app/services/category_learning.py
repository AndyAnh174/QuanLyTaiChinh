"""
Category learning service - learns from user corrections
"""
from typing import Optional
from django.core.cache import cache
from ..models import Category, Transaction


class CategoryLearningService:
    """
    Service for learning category mappings from user corrections
    """
    
    CACHE_PREFIX = "category_mapping"
    CACHE_TTL = 86400 * 30  # 30 days
    
    def learn_mapping(self, merchant: str, category: Category) -> None:
        """
        Learn a category mapping from user correction
        
        Args:
            merchant: Merchant/description pattern
            category: Correct category
        """
        cache_key = f"{self.CACHE_PREFIX}:{merchant.lower()}"
        cache.set(cache_key, category.id, self.cache_ttl)
    
    def get_learned_category(self, merchant: str) -> Optional[Category]:
        """
        Get learned category for a merchant
        
        Args:
            merchant: Merchant/description pattern
        
        Returns:
            Category if found, None otherwise
        """
        cache_key = f"{self.CACHE_PREFIX}:{merchant.lower()}"
        category_id = cache.get(cache_key)
        
        if category_id:
            try:
                return Category.objects.get(id=category_id)
            except Category.DoesNotExist:
                cache.delete(cache_key)
                return None
        
        return None
    
    def learn_from_transaction(self, transaction: Transaction) -> None:
        """
        Learn from a transaction if it has category and description
        
        Args:
            transaction: Transaction instance
        """
        if transaction.category and transaction.description:
            # Extract merchant name from description (first few words)
            words = transaction.description.split()[:3]
            merchant = " ".join(words)
            if merchant:
                self.learn_mapping(merchant, transaction.category)
    
    def sync_to_database(self) -> None:
        """
        Sync learned mappings from cache to database.
        This can be called periodically to persist mappings.
        """
        # This would require a model to store mappings permanently
        # For now, mappings are only in cache
        pass


# Singleton instance
category_learning_service = CategoryLearningService()

