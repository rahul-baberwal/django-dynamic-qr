from django.shortcuts import render
from .base import BaseQRType


class LinkListType(BaseQRType):
    """
    Link list QR — renders a hosted page with multiple links/buttons.
    type_data keys: title, description,
                    links: [{label, url, icon (optional)}]
    """
    type_id = "link_list"
    has_landing_page = True

    def get_destination(self) -> str:
        return self.qr.get_redirect_url()

    def respond(self, request):
        return render(request, "django_dynamic_qr/link_list.html", {
            "qr": self.qr,
            "data": self.data,
        })

    def validate(self):
        errors = []
        if not self.get("links"):
            errors.append("At least one link is required.")
        return errors
