from urllib.parse import urlencode
from .base import BaseQRType


class EmailType(BaseQRType):
    """
    Email QR — opens a pre-addressed compose window.
    type_data keys: to, subject (optional), body (optional)
    """
    type_id = "email"
    is_static = True

    def get_destination(self) -> str:
        d = self.data
        params = {}
        if d.get("subject"):
            params["subject"] = d["subject"]
        if d.get("body"):
            params["body"] = d["body"]
        to = d.get("to", "")
        qs = urlencode(params)
        return f"mailto:{to}{'?' + qs if qs else ''}"

    def validate(self):
        errors = []
        if not self.get("to"):
            errors.append("Recipient email address is required.")
        return errors
