from django.apps import AppConfig


class DjangoDynamicQRConfig(AppConfig):
    name = "django_dynamic_qr"
    verbose_name = "Django Dynamic QR"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self):
        from django_dynamic_qr.types import registry  # noqa: F401 — triggers registration
