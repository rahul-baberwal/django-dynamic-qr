"""
Records a scan event for a QRCode instance.
Call ScanLogger(qr_code, request).log() inside the redirect view.
"""
import logging
from django_dynamic_qr.settings import get_setting

logger = logging.getLogger(__name__)


def _get_ip(request) -> str:
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "")


def _parse_ua(ua_string: str) -> dict:
    try:
        import user_agents
        ua = user_agents.parse(ua_string)
        if ua.is_mobile:
            device = "mobile"
        elif ua.is_tablet:
            device = "tablet"
        elif ua.is_pc:
            device = "desktop"
        else:
            device = "unknown"
        return {
            "device": device,
            "os": ua.os.family[:50],
            "browser": ua.browser.family[:50],
        }
    except ImportError:
        return {"device": "unknown", "os": "", "browser": ""}
    except Exception as exc:
        logger.debug("UA parse error: %s", exc)
        return {"device": "unknown", "os": "", "browser": ""}


class ScanLogger:
    def __init__(self, qr_code, request):
        self.qr = qr_code
        self.request = request

    def log(self):
        if not get_setting("SCAN_LOG_ENABLED"):
            return
        if get_setting("SCAN_LOG_ASYNC"):
            try:
                from django_dynamic_qr.tasks import log_scan_task
                log_scan_task.delay(self.qr.pk, self._build_data())
                return
            except ImportError:
                pass
        self._write(self._build_data())

    def _build_data(self) -> dict:
        ip = _get_ip(self.request)
        ua_string = self.request.META.get("HTTP_USER_AGENT", "")
        ua_info = _parse_ua(ua_string)
        from django_dynamic_qr.analytics.geo import get_geo
        geo = get_geo(ip)
        return {
            "ip_address": ip or None,
            "country": geo.get("country", ""),
            "city": geo.get("city", ""),
            "user_agent": ua_string[:500],
            "referer": self.request.META.get("HTTP_REFERER", "")[:500],
            **ua_info,
        }

    def _write(self, data: dict):
        from django_dynamic_qr.models import ScanLog
        try:
            ScanLog.objects.create(qr_code=self.qr, **data)
        except Exception as exc:
            logger.error("Failed to write scan log: %s", exc)
