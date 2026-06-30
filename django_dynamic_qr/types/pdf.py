from .base import BaseQRType


class PDFType(BaseQRType):
    """
    PDF QR — redirects to a hosted or external PDF URL.
    type_data keys: pdf_url (str), title (str, optional)
    """
    type_id = "pdf"

    def get_destination(self) -> str:
        return self.get("pdf_url", "")

    def validate(self):
        errors = []
        if not self.get("pdf_url"):
            errors.append("PDF URL is required.")
        return errors
