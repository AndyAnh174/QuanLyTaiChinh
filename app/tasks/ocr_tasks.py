"""
Celery tasks for async OCR processing
"""
from celery import shared_task
from ..services.ocr_service import ocr_service
from ..models import Transaction, Wallet, Category


@shared_task
def process_receipt_ocr(image_data: bytes, filename: str = None):
    """
    Process receipt image asynchronously using OCR
    
    Args:
        image_data: Image bytes
        filename: Optional filename
    
    Returns:
        Extracted transaction data
    """
    try:
        extracted = ocr_service.process_receipt(image_data, filename)
        return extracted
    except Exception as e:
        print(f"Error processing OCR: {e}")
        return {"error": str(e)}

