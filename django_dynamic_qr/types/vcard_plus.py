from django.shortcuts import render
from .base import BaseQRType


class VCardPlusType(BaseQRType):
    """
    Dynamic vCard+ — renders a rich hosted landing page with photo,
    social links, and a "Save contact" button.
    type_data keys: first_name, last_name, phone, email, company, title,
                    address, website, photo_url, bio,
                    socials: {platform: url, ...}
    """
    type_id = "vcard_plus"
    has_landing_page = True

    def get_destination(self) -> str:
        return self.qr.get_redirect_url()

    def respond(self, request):
        return render(request, "django_dynamic_qr/vcard_plus.html", {
            "qr": self.qr,
            "data": self.data,
        })

    def validate(self):
        errors = []
        if not (self.get("first_name") or self.get("last_name")):
            errors.append("At least first or last name is required.")
        return errors
