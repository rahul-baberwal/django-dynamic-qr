from django.db.models import Count
from django.http import HttpResponse
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django_dynamic_qr.models import QRCode, ScanLog, Folder
from django_dynamic_qr.engine.exporter import export_qr_code
from django_dynamic_qr.analytics.exporters import export_scan_csv, export_scan_xlsx
from django_dynamic_qr.bulk.csv_importer import import_from_csv
from django_dynamic_qr.bulk.zip_exporter import export_zip
from .serializers import QRCodeSerializer, ScanLogSerializer, FolderSerializer, AnalyticsSummarySerializer


class FolderViewSet(viewsets.ModelViewSet):
    serializer_class = FolderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Folder.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class QRCodeViewSet(viewsets.ModelViewSet):
    serializer_class = QRCodeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = QRCode.objects.filter(user=self.request.user).select_related("folder")
        folder = self.request.query_params.get("folder")
        qr_type = self.request.query_params.get("type")
        if folder:
            qs = qs.filter(folder_id=folder)
        if qr_type:
            qs = qs.filter(qr_type=qr_type)
        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    # --- Export single QR image ---
    @action(detail=True, methods=["get"], url_path="export")
    def export(self, request, pk=None):
        qr = self.get_object()
        fmt = request.query_params.get("fmt", "png").lower()
        if fmt not in {"png", "svg", "pdf", "eps"}:
            fmt = "png"
        data = export_qr_code(qr, fmt=fmt)
        mime_map = {"png": "image/png", "svg": "image/svg+xml",
                    "pdf": "application/pdf", "eps": "application/postscript"}
        resp = HttpResponse(data, content_type=mime_map[fmt])
        resp["Content-Disposition"] = f'attachment; filename="qr-{qr.slug}.{fmt}"'
        return resp

    # --- Analytics summary ---
    @action(detail=True, methods=["get"], url_path="analytics")
    def analytics(self, request, pk=None):
        qr = self.get_object()
        today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        scans = qr.scans.all()
        today_count = scans.filter(scanned_at__gte=today).count()
        top_countries = list(
            scans.values("country").annotate(count=Count("id"))
            .order_by("-count").values_list("country", "count")[:10]
        )
        top_devices = list(
            scans.values("device").annotate(count=Count("id"))
            .order_by("-count").values_list("device", "count")
        )
        # last 30 days daily counts
        from django.db.models.functions import TruncDate
        daily = list(
            scans.filter(scanned_at__gte=today - timezone.timedelta(days=30))
            .annotate(date=TruncDate("scanned_at"))
            .values("date").annotate(count=Count("id"))
            .order_by("date").values_list("date", "count")
        )
        data = {
            "total_scans": scans.count(),
            "scans_today": today_count,
            "top_countries": top_countries,
            "top_devices": top_devices,
            "daily_counts": daily,
        }
        return Response(AnalyticsSummarySerializer(data).data)

    # --- Export scan logs ---
    @action(detail=True, methods=["get"], url_path="analytics/export")
    def analytics_export(self, request, pk=None):
        qr = self.get_object()
        fmt = request.query_params.get("fmt", "csv").lower()
        if fmt == "xlsx":
            return export_scan_xlsx(qr)
        return export_scan_csv(qr)

    # --- Bulk CSV import ---
    @action(detail=False, methods=["post"], url_path="bulk-import")
    def bulk_import(self, request):
        csv_file = request.FILES.get("file")
        if not csv_file:
            return Response({"error": "No file uploaded."}, status=status.HTTP_400_BAD_REQUEST)
        created, errors = import_from_csv(csv_file, user=request.user)
        return Response({"created": created, "errors": errors})

    # --- Bulk ZIP export ---
    @action(detail=False, methods=["get"], url_path="bulk-export")
    def bulk_export(self, request):
        ids = request.query_params.getlist("id")
        fmt = request.query_params.get("fmt", "png")
        qs = self.get_queryset()
        if ids:
            qs = qs.filter(pk__in=ids)
        return export_zip(qs, fmt=fmt)
