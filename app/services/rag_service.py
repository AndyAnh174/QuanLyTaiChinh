"""
RAG (Retrieval Augmented Generation) service for financial data queries
"""
from typing import Dict, Any, List
from datetime import datetime, timedelta
from django.db.models import Sum, Count, Q, Avg
from django.utils import timezone
from .ai_service import ai_service
from ..models import Transaction, Budget, Category


from ..data.app_docs import APP_FEATURES

class RAGService:
    """
    Service for querying financial data and generating natural language responses
    """
    
    SYSTEM_PROMPT = """You are a helpful financial assistant for the 'AI Smart Finance' application. 
Answer questions about personal finances based on the provided data, and explain app features using the provided documentation.

Rules:
1. Be concise, friendly, and helpful.
2. Use Vietnamese language.
3. Format numbers with commas (e.g., 1,000,000 VNĐ).
4. If data is not available, say so clearly.
5. If the user asks about app functions, use the 'System Documentation' section.
6. Provide actionable insights when possible.

Data provided will be in JSON format. Use it to answer the user's question accurately."""

    def query_financial_data(self, question: str, session_id: int = None) -> Dict[str, Any]:
        """
        Query financial data and generate natural language response with session history.
        
        Args:
            question: User's natural language question
            session_id: Optional ID of the existing chat session
        
        Returns:
            Dictionary containing answer and session_id
        """
        from ..models import ChatSession, ChatMessage
        
        # Get or Create Session
        if session_id:
            try:
                session = ChatSession.objects.get(id=session_id)
            except ChatSession.DoesNotExist:
                # Fallback to new session if not found
                session = ChatSession.objects.create(title=question[:50])
        else:
            session = ChatSession.objects.create(title=question[:50])
            
        # 1. Save User Message
        ChatMessage.objects.create(session=session, role='user', content=question)
        
        # 2. Get Chat History (Last 5 messages for context)
        history = ChatMessage.objects.filter(session=session).order_by('created_at')[:10] # Get last 10 messages
        history_text = ""
        for msg in history:
            history_text += f"{msg.role}: {msg.content}\n"
        
        # 3. Get Financial Data Context
        data_context = self._extract_data_context(question)
        context_text = self._format_context(data_context)
        
        # 4. Generate response using AI
        prompt = f'''History of current conversation:
{history_text}

Question: {question}

--- SYSTEM DOCUMENTATION (Features & Tech Stack) ---
{APP_FEATURES}

--- USER FINANCIAL DATA (JSON) ---
{context_text}

Answer:'''
        
        response_text = ai_service.generate_text(prompt, self.SYSTEM_PROMPT)
        
        # 5. Save Assistant Message
        ChatMessage.objects.create(session=session, role='assistant', content=response_text)
        
        return {
            "answer": response_text,
            "session_id": session.id
        }
    
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
        # Check for specific date patterns using Regex
        import re
        # Pattern: ngày dd/mm/yyyy or dd/mm
        date_pattern = r'ngày (\d{1,2})[/-](\d{1,2})(?:[/-](\d{4}))?'
        match = re.search(date_pattern, question_lower)
        
        if match:
            day = int(match.group(1))
            month = int(match.group(2))
            year = int(match.group(3)) if match.group(3) else now.year
            
            try:
                # Set range to that specific full day (00:00:00 to 23:59:59)
                start_date = datetime(year, month, day, 0, 0, 0)
                end_date = datetime(year, month, day, 23, 59, 59)
            except ValueError:
                # Fallback if invalid date
                start_date = current_month_start
                end_date = now
        
        # Check for relative time references if no specific date matched
        elif "hôm nay" in question_lower:
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = now
        elif "hôm qua" in question_lower:
            yesterday = now - timedelta(days=1)
            start_date = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)
        elif "tháng này" in question_lower or "tháng hiện tại" in question_lower:
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
        
        # Calculate Real Wallet Balance (Total Assets)
        from ..models import Wallet
        wallets = Wallet.objects.all()
        real_wallet_balance = sum(w.balance for w in wallets)
        
        context['period'] = {
            'start': start_date.isoformat(),
            'end': end_date.isoformat(),
            'note': 'This data is for the specific period derived from the question (default: current month). For "Current Balance", use real_wallet_balance.'
        }
        context['totals'] = {
            'period_income': float(total_income),
            'period_expense': float(total_expense),
            'period_balance': float(total_income - total_expense),
            'real_wallet_balance': float(real_wallet_balance), # This is the true "Current Balance"
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
            
                for item in category_breakdown
            ]

        # Add List of Transactions (Limit 10 newest) for specific queries
        # This helps AI answer "List my transactions" or "What did I buy?"
        recent_tx = transactions.select_related('category', 'wallet').order_by('-date')[:15]
        context['transactions_list'] = [
            {
                "date": tx.date.strftime("%Y-%m-%d %H:%M"),
                "desc": tx.description,
                "amount": float(tx.amount),
                "type": tx.transaction_type,
                "category": tx.category.name if tx.category else "Uncategorized",
                "wallet": tx.wallet.name
            }
            for tx in recent_tx
        ]
        
        return context
    
    def _format_context(self, context: Dict[str, Any]) -> str:
        """Format context data as text for LLM"""
        import json
        return json.dumps(context, indent=2, ensure_ascii=False)


# Singleton instance
rag_service = RAGService()

