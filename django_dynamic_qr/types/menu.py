from django.shortcuts import render
from .base import BaseQRType


class MenuType(BaseQRType):
    """
    Restaurant menu QR — renders a hosted menu landing page.
    type_data keys:
        restaurant_name, logo_url, categories: [
            {name, items: [{name, description, price, image_url}]}
        ]
    """
    type_id = "menu"
    has_landing_page = True

    def get_destination(self) -> str:
        return self.qr.get_redirect_url()

    def respond(self, request):
        return render(request, "django_dynamic_qr/menu.html", {
            "qr": self.qr,
            "data": self.data,
        })

    def validate(self):
        errors = []
        if not self.get("restaurant_name"):
            errors.append("Restaurant name is required.")
        if not self.get("categories"):
            errors.append("At least one menu category is required.")
        return errors
