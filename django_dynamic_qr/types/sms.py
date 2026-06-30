from .base import BaseQRType


class SMSType(BaseQRType):
    """
    SMS QR — opens SMS app with pre-filled number and message.
    type_data keys: phone, message (optional)
    """
    type_id = "sms"
    is_static = True

    def get_destination(self) -> str:
        d = self.data
        phone = d.get("phone", "")
        message = d.get("message", "")
        return f"sms:{phone}{'?body=' + message if message else ''}"

    def validate(self):
        errors = []
        if not self.get("phone"):
            errors.append("Phone number is required.")
        return errors
