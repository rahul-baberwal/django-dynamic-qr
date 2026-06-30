from django.shortcuts import render
from .base import BaseQRType

SUPPORTED_PLATFORMS = [
    "instagram", "twitter", "facebook", "linkedin", "youtube",
    "tiktok", "pinterest", "snapchat", "github", "telegram",
    "whatsapp", "website", "email",
]


class SocialLinksType(BaseQRType):
    """
    Social links hub — renders a landing page with social profile buttons.
    type_data keys:
        title, bio, avatar_url,
        links: [{platform, url, label}]
    """
    type_id = "social"
    has_landing_page = True

    def get_destination(self) -> str:
        return self.qr.get_redirect_url()

    def respond(self, request):
        return render(request, "django_dynamic_qr/social_links.html", {
            "qr": self.qr,
            "data": self.data,
        })

    def validate(self):
        errors = []
        if not self.get("links"):
            errors.append("At least one social link is required.")
        return errors
