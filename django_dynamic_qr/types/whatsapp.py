from urllib.parse import quote
from .base import BaseQRType


class WhatsAppType(BaseQRType):
    """
    WhatsApp QR — opens a WhatsApp chat with optional pre-filled message.
    type_data keys: phone (intl format, digits only), message (optional)
    """
    type_id = "whatsapp"
    is_static = True

    def get_destination(self) -> str:
        phone = self.get("phone", "").strip().replace("+", "").replace(" ", "")
        message = self.get("message", "")
        url = f"https://wa.me/{phone}"
        if message:
            url += f"?text={quote(message)}"
        return url

    def validate(self):
        errors = []
        if not self.get("phone"):
            errors.append("WhatsApp phone number is required.")
        return errors
