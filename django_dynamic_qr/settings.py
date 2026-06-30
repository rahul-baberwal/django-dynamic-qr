from django.conf import settings as django_settings

DEFAULTS = {
    "SHORT_URL_BASE": "",          # e.g. "https://yourdomain.com"
    "DEFAULT_ERROR_CORRECTION": "H",
    "DEFAULT_BOX_SIZE": 10,
    "DEFAULT_BORDER": 4,
    "LOGO_MAX_RATIO": 0.25,        # logo occupies max 25 % of QR area
    "SCAN_LOG_ASYNC": False,       # set True to use Celery task
    "GEO_BACKEND": "ip-api",       # "ip-api" | "maxmind" | None
    "MAXMIND_DB_PATH": None,
    "EXPORT_FORMATS": ["png", "svg", "pdf", "eps"],
    "ENABLE_REST_API": True,
    "API_TOKEN_AUTH": True,
    "UPLOAD_TO": "qr_codes/",
    "LOGO_UPLOAD_TO": "qr_logos/",
    "SCAN_LOG_ENABLED": True,
}


def get_setting(key):
    user_settings = getattr(django_settings, "DJANGO_DYNAMIC_QR", {})
    return user_settings.get(key, DEFAULTS[key])
