from django.urls import path, include

app_name = "dqr"

urlpatterns = [
    path("qr/", include("django_dynamic_qr.views.urls")),
    path("api/qr/", include("django_dynamic_qr.api.urls")),
]
