"""
High-level export helper that works from a QRCode model instance.
"""
from django.http import HttpResponse
from .generator import generate_qr

MIME_TYPES = {
    "png": "image/png",
    "svg": "image/svg+xml",
    "pdf": "application/pdf",
    "eps": "application/postscript",
}


def export_qr_code(qr_code, fmt: str = "png") -> bytes:
    """Return raw bytes for the given QRCode instance in the requested format."""
    handler = qr_code.get_type_handler()
    content = handler.to_qr_content()

    logo_path = None
    if qr_code.logo:
        try:
            logo_path = qr_code.logo.path
        except Exception:
            pass

    return generate_qr(
        content=content,
        fg_color=qr_code.fg_color,
        bg_color=qr_code.bg_color,
        error_correction=qr_code.error_correction,
        logo_path=logo_path,
        fmt=fmt,
    )


def export_response(qr_code, fmt: str = "png") -> HttpResponse:
    """Return a Django HttpResponse serving the QR image as a download."""
    data = export_qr_code(qr_code, fmt)
    mime = MIME_TYPES.get(fmt, "application/octet-stream")
    slug = qr_code.slug
    response = HttpResponse(data, content_type=mime)
    response["Content-Disposition"] = f'attachment; filename="qr-{slug}.{fmt}"'
    return response
