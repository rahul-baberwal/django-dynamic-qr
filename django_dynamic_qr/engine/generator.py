"""
QR image generator.

Dependencies: qrcode[pil], Pillow, segno
Install: pip install "qrcode[pil]" pillow segno
"""
import io
from django_dynamic_qr.settings import get_setting

_EC_MAP = {"L": 1, "M": 0, "Q": 3, "H": 2}   # qrcode constants


def _qr_module():
    import qrcode
    return qrcode


def generate_qr(
    content: str,
    fg_color: str = "#000000",
    bg_color: str = "#FFFFFF",
    box_size: int = None,
    border: int = None,
    error_correction: str = None,
    logo_path: str = None,
    logo_max_ratio: float = None,
    fmt: str = "png",
) -> bytes:
    """
    Generate a QR code and return raw bytes.

    :param content: String to encode.
    :param fmt: "png" | "svg" | "pdf" | "eps"
    :returns: Raw image bytes.
    """
    fmt = fmt.lower()
    box_size = box_size or get_setting("DEFAULT_BOX_SIZE")
    border = border or get_setting("DEFAULT_BORDER")
    ec = error_correction or get_setting("DEFAULT_ERROR_CORRECTION")
    logo_max_ratio = logo_max_ratio or get_setting("LOGO_MAX_RATIO")

    if fmt == "svg":
        return _generate_svg(content, fg_color, bg_color, ec)
    elif fmt in ("pdf", "eps"):
        return _generate_segno(content, fg_color, bg_color, ec, fmt)
    else:
        return _generate_png(content, fg_color, bg_color, box_size, border, ec, logo_path, logo_max_ratio)


def _generate_png(content, fg_color, bg_color, box_size, border, ec, logo_path, logo_max_ratio):
    import qrcode
    from PIL import Image

    ec_const = {
        "L": qrcode.constants.ERROR_CORRECT_L,
        "M": qrcode.constants.ERROR_CORRECT_M,
        "Q": qrcode.constants.ERROR_CORRECT_Q,
        "H": qrcode.constants.ERROR_CORRECT_H,
    }.get(ec, qrcode.constants.ERROR_CORRECT_H)

    qr = qrcode.QRCode(
        error_correction=ec_const,
        box_size=box_size,
        border=border,
    )
    qr.add_data(content)
    qr.make(fit=True)

    img = qr.make_image(fill_color=fg_color, back_color=bg_color).convert("RGBA")

    if logo_path:
        img = _overlay_logo(img, logo_path, logo_max_ratio)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def _overlay_logo(qr_img, logo_path, ratio):
    from PIL import Image
    logo = Image.open(logo_path).convert("RGBA")
    qr_w, qr_h = qr_img.size
    max_logo_size = int(min(qr_w, qr_h) * ratio)
    logo.thumbnail((max_logo_size, max_logo_size), Image.LANCZOS)
    logo_w, logo_h = logo.size
    pos = ((qr_w - logo_w) // 2, (qr_h - logo_h) // 2)
    qr_img.paste(logo, pos, mask=logo)
    return qr_img


def _generate_svg(content, fg_color, bg_color, ec):
    import segno
    qr = segno.make(content, error=ec.lower(), micro=False)
    buf = io.BytesIO()
    qr.save(buf, kind="svg", dark=fg_color, light=bg_color, scale=10)
    return buf.getvalue()


def _generate_segno(content, fg_color, bg_color, ec, fmt):
    import segno
    qr = segno.make(content, error=ec.lower(), micro=False)
    buf = io.BytesIO()
    qr.save(buf, kind=fmt, dark=fg_color, light=bg_color, scale=10)
    return buf.getvalue()
