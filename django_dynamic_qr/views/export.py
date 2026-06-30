from django.views import View
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin

from django_dynamic_qr.models import QRCode
from django_dynamic_qr.engine.exporter import export_response


class QRExportView(LoginRequiredMixin, View):
    """
    GET /qr/<slug>/export/?fmt=png
    Allowed formats: png, svg, pdf, eps
    """

    ALLOWED_FORMATS = {"png", "svg", "pdf", "eps"}

    def get(self, request, slug):
        qr = get_object_or_404(QRCode, slug=slug, user=request.user)
        fmt = request.GET.get("fmt", "png").lower()
        if fmt not in self.ALLOWED_FORMATS:
            fmt = "png"
        return export_response(qr, fmt=fmt)
