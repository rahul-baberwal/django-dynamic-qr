from .base import BaseQRType


class WiFiType(BaseQRType):
    """
    WiFi QR — static, encoded directly (no redirect needed).
    type_data keys: ssid, password, security (WPA|WEP|nopass), hidden (bool)
    """
    type_id = "wifi"
    is_static = True

    def get_destination(self) -> str:
        d = self.data
        ssid = d.get("ssid", "")
        password = d.get("password", "")
        security = d.get("security", "WPA")
        hidden = "true" if d.get("hidden") else "false"
        return f"WIFI:T:{security};S:{ssid};P:{password};H:{hidden};;"

    def validate(self):
        errors = []
        if not self.get("ssid"):
            errors.append("SSID (network name) is required.")
        return errors
