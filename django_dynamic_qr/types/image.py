from django.shortcuts import render
from .base import BaseQRType


class ImageType(BaseQRType):
    """
    Image gallery QR — renders a hosted gallery landing page.
    type_data keys: title, images: [{url, caption}]
    """
    type_id = "image"
    has_landing_page = True

    def get_destination(self) -> str:
        return self.qr.get_redirect_url()

    def respond(self, request):
        return render(request, "django_dynamic_qr/image_gallery.html", {
            "qr": self.qr,
            "data": self.data,
        })

    def validate(self):
        errors = []
        if not self.get("images"):
            errors.append("At least one image URL is required.")
        return errors
