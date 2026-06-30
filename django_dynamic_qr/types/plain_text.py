from .base import BaseQRType


class PlainTextType(BaseQRType):
    """
    Plain text QR — works fully offline, no internet required.
    type_data keys: text (str)
    """
    type_id = "text"
    is_static = True

    def get_destination(self) -> str:
        return self.get("text", "")

    def validate(self):
        errors = []
        if not self.get("text"):
            errors.append("Text content is required.")
        return errors
