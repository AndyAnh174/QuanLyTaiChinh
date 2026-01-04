"""
Celery tasks for recurring transactions
"""
from celery import shared_task
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from ..models import RecurringTransaction, Transaction, Wallet, Category


@shared_task
def process_recurring_transactions():
    """
    Process recurring transactions that are due.
    This task should be scheduled to run daily.
    """
    today = date.today()
    due_recurring = RecurringTransaction.objects.filter(
        next_run_date__lte=today,
        is_active=True
    )
    
    created_count = 0
    for recurring in due_recurring:
        try:
            # Create transaction from recurring template
            transaction = Transaction.objects.create(
                wallet=recurring.wallet,
                category=recurring.category,
                amount=recurring.amount,
                description=recurring.description or recurring.name,
                transaction_type=recurring.transaction_type,
                date=today,
                recurring_transaction=recurring,
            )
            
            # Update next_run_date based on frequency
            if recurring.frequency == 'daily':
                recurring.next_run_date = today + timedelta(days=1)
            elif recurring.frequency == 'weekly':
                recurring.next_run_date = today + timedelta(weeks=1)
            elif recurring.frequency == 'monthly':
                recurring.next_run_date = today + relativedelta(months=1)
            elif recurring.frequency == 'yearly':
                recurring.next_run_date = today + relativedelta(years=1)
            
            recurring.save()
            created_count += 1
        except Exception as e:
            print(f"Error processing recurring transaction {recurring.id}: {e}")
    
    return f"Created {created_count} transactions from recurring templates"

