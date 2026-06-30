from django.urls import path
from .redirect import QRRedirectView
from .export import QRExportView

urlpatterns = [
    path("<slug:slug>/", QRRedirectView.as_view(), name="redirect"),
    path("<slug:slug>/export/", QRExportView.as_view(), name="export"),
]
