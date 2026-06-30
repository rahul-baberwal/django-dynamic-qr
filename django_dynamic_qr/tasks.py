"""
Optional Celery tasks for async scan logging.
Only active when Celery is installed and SCAN_LOG_ASYNC = True.
"""
try:
    from celery import shared_task

    @shared_task(ignore_result=True)
    def log_scan_task(qr_pk: int, data: dict):
        from django_dynamic_qr.models import QRCode, ScanLog
        try:
            qr = QRCode.objects.get(pk=qr_pk)
            ScanLog.objects.create(qr_code=qr, **data)
        except Exception:
            pass

except ImportError:
    pass  # Celery not installed — sync logging used instead
