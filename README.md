# django-dynamic-qr

A full-featured, self-hosted dynamic QR code package for Django — a QRFY-equivalent you own completely.

14 QR types · short-URL redirects · per-scan analytics · password/schedule/geo access control · bulk CSV/ZIP · REST API · Django admin with live previews.

## Features

- **14 QR types**: URL, vCard, vCard+ (rich landing page), PDF, Restaurant Menu, Social Links hub, WiFi, Email, SMS, WhatsApp, Image Gallery, Plain Text, Link List, App Store (smart iOS/Android redirect)
- **Dynamic short URLs** — edit destination after printing, no reprint needed
- **Design engine** — custom colors, logo overlay, frame styles, 4 error-correction levels
- **Export formats** — PNG, SVG, PDF, EPS
- **Analytics** — scan count, device/OS/browser, country/city geolocation, daily trend, CSV/XLSX export
- **Access control** — password protection, daily scan limits, scheduled activation/expiry, country allow-list
- **Bulk operations** — CSV import, ZIP export of multiple QR images
- **REST API** — full DRF viewsets with token auth (optional)
- **Django admin** — inline scan logs, live QR thumbnail preview, bulk actions
- **Async-ready** — optional Celery task for non-blocking scan logging

## Installation

```bash
pip install django-dynamic-qr[api]
# or, from local source:
pip install -e /path/to/django-dynamic-qr
```

### 1. Add to `INSTALLED_APPS`

```python
INSTALLED_APPS = [
    ...
    "django_dynamic_qr",
    "rest_framework",   # only if using the REST API
]
```

### 2. Include URLs

```python
# project/urls.py
from django.urls import path, include

urlpatterns = [
    ...
    path("", include("django_dynamic_qr.urls")),
]
```

This mounts:
- `/qr/<slug>/` — the redirect / landing-page endpoint (this is what your QR images encode)
- `/qr/<slug>/export/` — download the QR image
- `/api/qr/...` — REST API (if DRF installed)

### 3. Configure settings (all optional — sane defaults provided)

```python
DJANGO_DYNAMIC_QR = {
    "SHORT_URL_BASE": "https://yourdomain.com",   # IMPORTANT: set this in production
    "DEFAULT_ERROR_CORRECTION": "H",
    "DEFAULT_BOX_SIZE": 10,
    "DEFAULT_BORDER": 4,
    "LOGO_MAX_RATIO": 0.25,
    "SCAN_LOG_ASYNC": False,        # True if Celery is configured
    "GEO_BACKEND": "ip-api",        # "ip-api" | "maxmind" | None
    "MAXMIND_DB_PATH": None,
    "ENABLE_REST_API": True,
    "UPLOAD_TO": "qr_codes/",
    "LOGO_UPLOAD_TO": "qr_logos/",
}
```

### 4. Migrate

```bash
python manage.py migrate django_dynamic_qr
```

### 5. Make sure `MEDIA_URL` / `MEDIA_ROOT` are configured (for logo uploads) and your urls.py serves media in development.

## Usage

### Create a QR code programmatically

```python
from django_dynamic_qr.models import QRCode

qr = QRCode.objects.create(
    user=request.user,
    name="My Website",
    qr_type="url",
    type_data={"url": "https://example.com"},
    fg_color="#111111",
    bg_color="#FFFFFF",
)

print(qr.get_redirect_url())   # https://yourdomain.com/qr/AbC123Xy/
```

### Export the QR image

```python
from django_dynamic_qr.engine.exporter import export_qr_code

png_bytes = export_qr_code(qr, fmt="png")
svg_bytes = export_qr_code(qr, fmt="svg")
```

Or via the built-in view: `GET /qr/<slug>/export/?fmt=svg`

### Update the destination — no reprint needed

```python
qr.type_data = {"url": "https://example.com/new-page"}
qr.save()
# The printed QR code, slug, and image stay identical.
# Anyone scanning it is now redirected to the new URL.
```

### Add access control

```python
from django.utils import timezone
import datetime

qr.password = "secret123"
qr.scan_limit_day = 500
qr.active_from = timezone.now()
qr.active_until = timezone.now() + datetime.timedelta(days=30)
qr.allowed_countries = ["IN", "US", "GB"]
qr.save()
```

### Bulk import from CSV

CSV format:
```csv
name,qr_type,data
My Website,url,"{""url"": ""https://example.com""}"
Office WiFi,wifi,"{""ssid"": ""OfficeNet"", ""password"": ""pass123"", ""security"": ""WPA""}"
```

```python
from django_dynamic_qr.bulk import import_from_csv

created, errors = import_from_csv(csv_file, user=request.user)
```

### Management command

```bash
python manage.py generate_qr <slug> --fmt png --output qr.png
```

## REST API (optional, requires `djangorestframework`)

```
GET    /api/qr/                          list QR codes
POST   /api/qr/                          create
GET    /api/qr/<id>/                     retrieve
PATCH  /api/qr/<id>/                     update destination (dynamic!)
DELETE /api/qr/<id>/
GET    /api/qr/<id>/export/?fmt=png      download image
GET    /api/qr/<id>/analytics/           scan stats summary
GET    /api/qr/<id>/analytics/export/    download scan logs CSV/XLSX
POST   /api/qr/bulk-import/              CSV bulk create
GET    /api/qr/bulk-export/?fmt=svg      ZIP export
```

## Type payload reference

| Type | `type_data` keys |
|---|---|
| `url` | `url` |
| `vcard` | `first_name, last_name, phone, email, company, title, address, website` |
| `vcard_plus` | same as vcard + `photo_url, bio, socials: {platform: url}` |
| `pdf` | `pdf_url, title` |
| `menu` | `restaurant_name, logo_url, categories: [{name, items: [{name, description, price, image_url}]}]` |
| `social` | `title, bio, avatar_url, links: [{platform, url, label}]` |
| `wifi` | `ssid, password, security, hidden` |
| `email` | `to, subject, body` |
| `sms` | `phone, message` |
| `whatsapp` | `phone, message` |
| `image` | `title, images: [{url, caption}]` |
| `text` | `text` |
| `link_list` | `title, description, links: [{label, url, icon}]` |
| `app_store` | `ios_url, android_url, fallback_url` |

## Extending with a custom QR type

```python
# myapp/qr_types.py
from django_dynamic_qr.types.base import BaseQRType
from django_dynamic_qr.types import registry

class CalendarEventType(BaseQRType):
    type_id = "calendar_event"
    is_static = True

    def get_destination(self):
        d = self.data
        return f"BEGIN:VEVENT\nSUMMARY:{d['title']}\nDTSTART:{d['start']}\nEND:VEVENT"

registry["calendar_event"] = CalendarEventType
```

Import this module in your app's `ready()` to register it at startup.

## License

MIT
