from django.db import models


class ScanLog(models.Model):
    DEVICE_CHOICES = [
        ("mobile", "Mobile"),
        ("tablet", "Tablet"),
        ("desktop", "Desktop"),
        ("unknown", "Unknown"),
    ]

    qr_code = models.ForeignKey(
        "django_dynamic_qr.QRCode",
        on_delete=models.CASCADE,
        related_name="scans",
    )
    scanned_at = models.DateTimeField(auto_now_add=True, db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    country = models.CharField(max_length=2, blank=True)   # ISO 3166-1 alpha-2
    city = models.CharField(max_length=100, blank=True)
    device = models.CharField(max_length=10, choices=DEVICE_CHOICES, default="unknown")
    os = models.CharField(max_length=50, blank=True)
    browser = models.CharField(max_length=50, blank=True)
    referer = models.URLField(blank=True)
    user_agent = models.TextField(blank=True)

    class Meta:
        ordering = ["-scanned_at"]
        verbose_name = "Scan log"
        verbose_name_plural = "Scan logs"
        indexes = [
            models.Index(fields=["qr_code", "scanned_at"]),
            models.Index(fields=["country"]),
        ]

    def __str__(self):
        return f"Scan of {self.qr_code.name} at {self.scanned_at:%Y-%m-%d %H:%M}"
