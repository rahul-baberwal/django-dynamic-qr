from django.views import View
from django.shortcuts import get_object_or_404

from django_dynamic_qr.models import QRCode
from django_dynamic_qr.access import AccessGuard
from django_dynamic_qr.analytics import ScanLogger


class QRRedirectView(View):
    """
    The heart of dynamic QR: receive a slug, run access checks,
    log the scan, then delegate to the type handler.
    """

    def get(self, request, slug):
        qr = get_object_or_404(QRCode, slug=slug, is_active=True)

        # 1. Access control
        guard_result = AccessGuard(qr, request).check()
        if not guard_result.allowed:
            return guard_result.response

        # 2. Log the scan (async if Celery configured)
        ScanLogger(qr, request).log()

        # 3. Delegate to type handler (redirect or landing page)
        handler = qr.get_type_handler()
        return handler.respond(request)

    def post(self, request, slug):
        """POST is used by password-protected QR codes."""
        return self.get(request, slug)
