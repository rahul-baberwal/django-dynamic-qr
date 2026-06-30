"""
Export multiple QR codes as a ZIP archive.
"""
import io
import zipfile
from django.http import HttpResponse


def export_zip(qr_codes, fmt: str = "png") -> HttpResponse:
    """
    Build a ZIP of QR images and return it as an HttpResponse.

    :param qr_codes: queryset or iterable of QRCode instances
    :param fmt: "png" | "svg" | "pdf" | "eps"
    """
    from django_dynamic_qr.engine.exporter import export_qr_code

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for qr in qr_codes:
            try:
                data = export_qr_code(qr, fmt=fmt)
                filename = f"{qr.slug}-{qr.name[:40]}.{fmt}".replace("/", "_")
                zf.writestr(filename, data)
            except Exception:
                pass  # skip failed individual exports

    buf.seek(0)
    response = HttpResponse(buf.read(), content_type="application/zip")
    response["Content-Disposition"] = 'attachment; filename="qr-codes.zip"'
    return response
