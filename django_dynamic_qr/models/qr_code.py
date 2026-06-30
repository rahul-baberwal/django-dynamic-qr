import secrets
from django.db import models
from django.conf import settings
from django.urls import reverse
from .folder import Folder
from django_dynamic_qr.settings import get_setting


def _slug():
    return secrets.token_urlsafe(8)


class QRCode(models.Model):
    TYPE_CHOICES = [
        ("url", "URL"),
        ("vcard", "vCard"),
        ("vcard_plus", "vCard+"),
        ("pdf", "PDF"),
        ("menu", "Menu"),
        ("social", "Social links"),
        ("wifi", "WiFi"),
        ("email", "Email"),
        ("sms", "SMS"),
        ("whatsapp", "WhatsApp"),
        ("image", "Image"),
        ("text", "Plain text"),
        ("link_list", "Link list"),
        ("app_store", "App store"),
    ]

    FRAME_CHOICES = [
        ("none", "No frame"),
        ("simple", "Simple border"),
        ("scan_me", '"Scan me" label'),
        ("rounded", "Rounded label"),
    ]

    ERROR_CORRECTION_CHOICES = [
        ("L", "L — 7 %"),
        ("M", "M — 15 %"),
        ("Q", "Q — 25 %"),
        ("H", "H — 30 %"),
    ]

    # --- identity ---
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="qr_codes",
    )
    folder = models.ForeignKey(
        Folder,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="qr_codes",
    )
    name = models.CharField(max_length=255)
    tags = models.CharField(max_length=500, blank=True, help_text="Comma-separated tags")
    qr_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    slug = models.SlugField(unique=True, default=_slug, max_length=32)

    # --- payload (stored as JSON per type) ---
    type_data = models.JSONField(default=dict)

    # --- design ---
    fg_color = models.CharField(max_length=7, default="#000000")
    bg_color = models.CharField(max_length=7, default="#FFFFFF")
    logo = models.ImageField(
        upload_to=get_setting("LOGO_UPLOAD_TO"), null=True, blank=True
    )
    frame_style = models.CharField(max_length=20, choices=FRAME_CHOICES, default="none")
    error_correction = models.CharField(
        max_length=1, choices=ERROR_CORRECTION_CHOICES, default="H"
    )

    # --- access control ---
    password = models.CharField(max_length=128, blank=True)
    scan_limit_day = models.PositiveIntegerField(
        null=True, blank=True, help_text="Max scans per day (null = unlimited)"
    )
    active_from = models.DateTimeField(null=True, blank=True)
    active_until = models.DateTimeField(null=True, blank=True)
    allowed_countries = models.JSONField(
        default=list, help_text='List of ISO 3166-1 alpha-2 codes, e.g. ["IN","US"]'
    )
    is_active = models.BooleanField(default=True)

    # --- timestamps ---
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "QR Code"
        verbose_name_plural = "QR Codes"

    def __str__(self):
        return f"{self.name} ({self.qr_type})"

    def get_redirect_url(self):
        base = get_setting("SHORT_URL_BASE").rstrip("/")
        path = reverse("dqr:redirect", kwargs={"slug": self.slug})
        return f"{base}{path}"

    def get_type_handler(self):
        from django_dynamic_qr.types import registry
        handler_class = registry.get(self.qr_type)
        if handler_class is None:
            raise ValueError(f"No handler registered for QR type: {self.qr_type}")
        return handler_class(self)

    @property
    def total_scans(self):
        return self.scans.count()

    @property
    def tag_list(self):
        return [t.strip() for t in self.tags.split(",") if t.strip()]
