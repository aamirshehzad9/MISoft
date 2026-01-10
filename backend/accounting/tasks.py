from celery import shared_task
from accounting.services.recurring_service import RecurringTransactionService
import logging

logger = logging.getLogger(__name__)

@shared_task
def process_recurring_transactions():
    """
    Celery task to generate scheduled recurring transactions.
    Should be scheduled to run daily.
    """
    logger.info("Starting recurring transaction processing...")
    try:
        generated = RecurringTransactionService.generate_due_transactions()
        logger.info(f"Generated {len(generated)} recurring transactions: {generated}")
        return f"Generated {len(generated)} transactions"
    except Exception as e:
        logger.error(f"Error processing recurring transactions: {e}")
        raise e
