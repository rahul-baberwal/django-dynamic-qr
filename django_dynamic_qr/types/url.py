from .base import BaseQRType


class URLType(BaseQRType):
    """
    URL QR — dynamic redirect to any web address.
    type_data keys: url (str)
    """
    type_id = "url"

    def get_destination(self) -> str:
        return self.get("url", "")

    def validate(self):
        errors = []
        if not self.get("url"):
            errors.append("URL is required.")
        return errors
