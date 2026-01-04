"""
NLP service for parsing natural language transaction input
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from .ai_service import ai_service
from ..models import Category, Wallet


class NLPService:
    """
    Service for extracting transaction information from natural language
    """
    
    SYSTEM_PROMPT_TEMPLATE = """You are a financial transaction parser. Extract transaction information from Vietnamese natural language text.
Today is: {today}

Rules:
1. Extract multiple transactions if the text contains multiple expenses/income
2. For each transaction, extract:
   - amount: numeric value (remove 'k', 'tr', 'nghìn', 'triệu' and convert)
   - category: identify appropriate category
   - wallet: identify payment method
   - description: original text summary
   - date: specific date (YYYY-MM-DD), 'today', 'yesterday' mapped to actual date based on Today.
   - type: 'expense' (spending) or 'income' (receiving money)

3. Amount conversion:
   - "45k" = 45000
   - "1tr" = 1000000

4. Output JSON:
[
  {{
    "amount": 45000,
    "category": "Ăn uống",
    "wallet": "cash",
    "description": "Ăn phở",
    "date": "2026-01-04",
    "type": "expense"
  }}
]"""

    def parse_transactions(self, text: str) -> List[Dict[str, Any]]:
        """
        Parse natural language text into transaction objects
        """
        today_str = datetime.now().strftime("%A, %Y-%m-%d")
        system_prompt = self.SYSTEM_PROMPT_TEMPLATE.format(today=today_str)
        
        prompt = f"Parse this transaction text: {text}"
        
        try:
            response = ai_service.generate_text(prompt, system_prompt)
            # Extract JSON from response (might have markdown code blocks)
            import json
            import re
            
            # Try to find JSON in response
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                transactions = json.loads(json_match.group())
            else:
                # Try parsing entire response
                transactions = json.loads(response)
            
            # Validate and normalize transactions
            normalized = []
            for tx in transactions:
                normalized_tx = self._normalize_transaction(tx)
                if normalized_tx:
                    normalized.append(normalized_tx)
            
            return normalized
        except Exception as e:
            print(f"Error parsing transactions: {e}")
            return []
    
    def suggest_category(self, description: str, merchant: Optional[str] = None) -> Optional[str]:
        """
        Suggest category for a transaction based on description/merchant
        
        Args:
            description: Transaction description
            merchant: Merchant name (optional)
        
        Returns:
            Suggested category name or None
        """
        # Check learned mappings first (from category_learning service)
        from django.core.cache import cache
        if merchant:
            cache_key = f"category_mapping:{merchant.lower()}"
            cached_category = cache.get(cache_key)
            if cached_category:
                return cached_category
        
        # Use AI to suggest
        prompt = f"Suggest a category for this transaction: {description}"
        if merchant:
            prompt += f" at {merchant}"
        
        system_prompt = """Suggest a category from this list: Ăn uống, Mua sắm, Giao thông, Giải trí, Y tế, Giáo dục, Hóa đơn, Khác.
Return only the category name, nothing else."""
        
        try:
            category = ai_service.generate_text(prompt, system_prompt).strip()
            return category if category in ["Ăn uống", "Mua sắm", "Giao thông", "Giải trí", "Y tế", "Giáo dục", "Hóa đơn", "Khác"] else None
        except:
            return None
    
    def _normalize_transaction(self, tx: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Normalize and validate transaction data"""
        try:
            # Ensure required fields
            if 'amount' not in tx or not tx['amount']:
                return None
            
            # Normalize wallet type
            wallet_map = {
                'tiền mặt': 'cash',
                'cash': 'cash',
                'momo': 'e_wallet',
                'zalopay': 'e_wallet',
                'bank': 'bank',
                'ngân hàng': 'bank',
                'credit card': 'credit_card',
                'thẻ tín dụng': 'credit_card',
            }
            wallet_type = tx.get('wallet', 'cash').lower()
            tx['wallet'] = wallet_map.get(wallet_type, 'cash')
            
            # Parse date
            if 'date' in tx and tx['date']:
                try:
                    tx['date'] = datetime.fromisoformat(tx['date'].replace('Z', '+00:00'))
                except:
                    tx['date'] = datetime.now()
            else:
                tx['date'] = datetime.now()
            
            # Ensure category exists or set default
            if 'category' not in tx or not tx['category']:
                tx['category'] = 'Khác'
            
            return tx
        except Exception as e:
            print(f"Error normalizing transaction: {e}")
            return None


# Singleton instance
nlp_service = NLPService()

