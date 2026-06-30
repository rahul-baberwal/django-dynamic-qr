from rest_framework.routers import DefaultRouter
from .views import QRCodeViewSet, FolderViewSet

router = DefaultRouter()
router.register("folders", FolderViewSet, basename="folder")
router.register("", QRCodeViewSet, basename="qrcode")

urlpatterns = router.urls
