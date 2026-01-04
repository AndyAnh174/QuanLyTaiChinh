"""
Celery tasks for anomaly detection
"""
from celery import shared_task
from ..services.anomaly_service import anomaly_service
from django.core.cache import cache


@shared_task
def detect_spending_anomalies():
    """
    Detect spending anomalies and cache results.
    This task should be scheduled to run daily.
    """
    anomalies = anomaly_service.detect_anomalies()
    
    # Cache anomalies for 24 hours
    cache.set('spending_anomalies', anomalies, 86400)
    
    return f"Detected {len(anomalies)} anomalies"

