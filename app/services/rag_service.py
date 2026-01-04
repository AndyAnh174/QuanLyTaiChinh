"""
RAG (Retrieval Augmented Generation) service for financial data queries
"""
from typing import Dict, Any, List
from datetime import datetime, timedelta
from django.db.models import Sum, Count, Q, Avg
from django.utils import timezone
from .ai_service import ai_service
from ..models import Transaction, Budget, Category


class RAGService:
    """
    Service for querying financial data and generating natural language responses
    """
    
    SYSTEM_PROMPT = """You are a helpful financial assistant. Answer questions about personal finances based on the provided data.

Rules:
1. Be concise and friendly
2. Use Vietnamese language
3. Format numbers with commas (e.g., 1,000,000 VNĐ)
4. If data is not available, say so clearly
5. Provide actionable insights when possible

Data provided will be in JSON format. Use it to answer the user's question accurately."""

    def query_financial_data(self, question: str) -> str:
        """
        Query financial data and generate natural language response
        
        Args:
            question: User's natural language question
        
        Returns:
            Natural language response
        """
        # Parse question to determine what data to fetch
        data_context = self._extract_data_context(question)
        
        # Format context for LLM
        context_text = self._format_context(data_context)
        
        # Generate response using AI
        prompt = f"Question: {question}\n\nData: {context_text}\n\nAnswer:"
        response = ai_service.generate_text(prompt, self.SYSTEM_PROMPT)
        
        return response
    
    def _extract_data_context(self, question: str) -> Dict[str, Any]:
        """
        Extract relevant financial data based on question
        
        Args:
            question: User question
        
        Returns:
            Dictionary with relevant data
        """
        question_lower = question.lower()
        context = {}
        now = timezone.now()
        current_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Check for time references
        if "tháng này" in question_lower or "tháng hiện tại" in question_lower:
            start_date = current_month_start
            end_date = now
        elif "tháng trước" in question_lower:
            end_date = current_month_start - timedelta(days=1)
            start_date = end_date.replace(day=1)
        else:
            # Default to current month
            start_date = current_month_start
            end_date = now
        
        # Check for category mentions
        category_name = None
        for cat in Category.objects.all():
            if cat.name.lower() in question_lower:
                category_name = cat.name
                break
        
        # Get transaction data
        transactions = Transaction.objects.filter(
            date__gte=start_date,
            date__lte=end_date
        )
        
        if category_name:
            transactions = transactions.filter(category__name=category_name)
        
        total_income = transactions.filter(transaction_type='income').aggregate(Sum('amount'))['amount__sum'] or 0
        total_expense = transactions.filter(transaction_type='expense').aggregate(Sum('amount'))['amount__sum'] or 0
        transaction_count = transactions.count()
        
        context['period'] = {
            'start': start_date.isoformat(),
            'end': end_date.isoformat(),
        }
        context['totals'] = {
            'income': float(total_income),
            'expense': float(total_expense),
            'balance': float(total_income - total_expense),
            'count': transaction_count,
        }
        
        # Get budget data if category is mentioned
        if category_name:
            budget = Budget.objects.filter(
                category__name=category_name,
                start_date__lte=end_date,
                end_date__gte=start_date,
                is_active=True
            ).first()
            
            if budget:
                context['budget'] = {
                    'amount': float(budget.amount),
                    'spent': float(budget.get_spent_amount()),
                    'remaining': float(budget.get_remaining_amount()),
                    'percentage': budget.get_percentage_used(),
                }
        
        # Get category breakdown if asking about spending
        if "tiêu" in question_lower or "chi" in question_lower:
            category_breakdown = Transaction.objects.filter(
                transaction_type='expense',
                date__gte=start_date,
                date__lte=end_date,
                category__isnull=False
            ).values('category__name').annotate(
                total=Sum('amount')
            ).order_by('-total')[:5]
            
            context['categories'] = [
                {
                    'name': item['category__name'],
                    'amount': float(item['total'])
                }
                for item in category_breakdown
            ]
        
        return context
    
    def _format_context(self, context: Dict[str, Any]) -> str:
        """Format context data as text for LLM"""
        import json
        return json.dumps(context, indent=2, ensure_ascii=False)


# Singleton instance
rag_service = RAGService()

