"""
Access control guards for QR code scans.
Run AccessGuard(qr_code, request).check() before logging or redirecting.
"""
from dataclasses import dataclass, field
from django.http import HttpResponse
from django.utils import timezone


@dataclass
class AccessResult:
    allowed: bool = True
    reason: str = ""
    response: HttpResponse = field(default=None)


class AccessGuard:
    def __init__(self, qr_code, request):
        self.qr = qr_code
        self.request = request

    def check(self) -> AccessResult:
        for guard in (
            self._check_active,
            self._check_schedule,
            self._check_geo,
            self._check_scan_limit,
            self._check_password,
        ):
            result = guard()
            if not result.allowed:
                return result
        return AccessResult(allowed=True)

    # ------------------------------------------------------------------ #

    def _check_active(self) -> AccessResult:
        if not self.qr.is_active:
            return self._deny("QR code is inactive.", self._render("deactivated.html"))
        return AccessResult()

    def _check_schedule(self) -> AccessResult:
        now = timezone.now()
        if self.qr.active_from and now < self.qr.active_from:
            return self._deny("QR code is not active yet.", self._render("not_yet.html"))
        if self.qr.active_until and now > self.qr.active_until:
            return self._deny("QR code has expired.", self._render("expired.html"))
        return AccessResult()

    def _check_geo(self) -> AccessResult:
        allowed = self.qr.allowed_countries
        if not allowed:
            return AccessResult()
        from django_dynamic_qr.analytics.geo import get_geo
        from django_dynamic_qr.analytics.logger import _get_ip
        ip = _get_ip(self.request)
        geo = get_geo(ip)
        country = geo.get("country", "")
        if country and country not in allowed:
            return self._deny(f"Access denied from {country}.", self._render("geo_blocked.html"))
        return AccessResult()

    def _check_scan_limit(self) -> AccessResult:
        limit = self.qr.scan_limit_day
        if limit is None:
            return AccessResult()
        from django_dynamic_qr.models import ScanLog
        today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        count = ScanLog.objects.filter(qr_code=self.qr, scanned_at__gte=today_start).count()
        if count >= limit:
            return self._deny("Daily scan limit reached.", self._render("scan_limit.html"))
        return AccessResult()

    def _check_password(self) -> AccessResult:
        if not self.qr.password:
            return AccessResult()
        submitted = self.request.GET.get("p") or self.request.POST.get("password", "")
        if submitted != self.qr.password:
            resp = self._render("password.html")
            return self._deny("Password required.", resp)
        return AccessResult()

    # ------------------------------------------------------------------ #

    def _deny(self, reason: str, response: HttpResponse) -> AccessResult:
        return AccessResult(allowed=False, reason=reason, response=response)

    def _render(self, template_name: str) -> HttpResponse:
        from django.shortcuts import render
        return render(
            self.request,
            f"django_dynamic_qr/access/{template_name}",
            {"qr": self.qr},
        )
