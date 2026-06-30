from .base import BaseQRType


class AppStoreType(BaseQRType):
    """
    App store QR — redirects to iOS App Store or Google Play based on device.
    type_data keys: ios_url, android_url, fallback_url
    """
    type_id = "app_store"

    def get_destination(self) -> str:
        return self.get("fallback_url") or self.get("ios_url") or self.get("android_url", "")

    def respond(self, request):
        from django.http import HttpResponseRedirect
        ua = request.META.get("HTTP_USER_AGENT", "").lower()
        if "android" in ua and self.get("android_url"):
            return HttpResponseRedirect(self.data["android_url"])
        if any(kw in ua for kw in ("iphone", "ipad", "ipod")) and self.get("ios_url"):
            return HttpResponseRedirect(self.data["ios_url"])
        return HttpResponseRedirect(self.get_destination())

    def validate(self):
        errors = []
        if not self.get("ios_url") and not self.get("android_url"):
            errors.append("At least one of iOS URL or Android URL is required.")
        return errors
