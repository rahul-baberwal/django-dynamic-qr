"""
Lightweight IP geolocation.

Backends:
  - ip-api  : free, no key needed, 45 req/min limit
  - maxmind : requires local DB file (MAXMIND_DB_PATH in settings)
  - None    : disabled
"""
import logging
from django_dynamic_qr.settings import get_setting

logger = logging.getLogger(__name__)


def get_geo(ip: str) -> dict:
    """Return {'country': 'IN', 'city': 'Kota'} or empty dict."""
    if not ip or ip in ("127.0.0.1", "::1"):
        return {}
    backend = get_setting("GEO_BACKEND")
    if backend == "ip-api":
        return _ip_api(ip)
    elif backend == "maxmind":
        return _maxmind(ip)
    return {}


def _ip_api(ip: str) -> dict:
    try:
        import urllib.request, json
        url = f"http://ip-api.com/json/{ip}?fields=countryCode,city,status"
        with urllib.request.urlopen(url, timeout=2) as resp:
            data = json.loads(resp.read())
        if data.get("status") == "success":
            return {"country": data.get("countryCode", ""), "city": data.get("city", "")}
    except Exception as exc:
        logger.debug("ip-api geo lookup failed: %s", exc)
    return {}


def _maxmind(ip: str) -> dict:
    try:
        import geoip2.database
        db_path = get_setting("MAXMIND_DB_PATH")
        with geoip2.database.Reader(db_path) as reader:
            resp = reader.city(ip)
            return {
                "country": resp.country.iso_code or "",
                "city": resp.city.name or "",
            }
    except Exception as exc:
        logger.debug("MaxMind geo lookup failed: %s", exc)
    return {}
