from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.http import HttpResponse

from django_dynamic_qr.models import QRCode, ScanLog, Folder
from django_dynamic_qr.engine.exporter import export_qr_code
from django_dynamic_qr.analytics.exporters import export_scan_csv
from django_dynamic_qr.bulk.zip_exporter import export_zip


@admin.register(Folder)
class FolderAdmin(admin.ModelAdmin):
    list_display = ["name", "color", "user", "created_at"]
    list_filter = ["user"]
    search_fields = ["name"]


class ScanLogInline(admin.TabularInline):
    model = ScanLog
    extra = 0
    readonly_fields = ["scanned_at", "country", "city", "device", "os", "browser", "ip_address"]
    can_delete = False
    max_num = 20
    ordering = ["-scanned_at"]


def export_png(modeladmin, request, queryset):
    if queryset.count() == 1:
        qr = queryset.first()
        data = export_qr_code(qr, "png")
        resp = HttpResponse(data, content_type="image/png")
        resp["Content-Disposition"] = f'attachment; filename="qr-{qr.slug}.png"'
        return resp
    return export_zip(queryset, fmt="png")
export_png.short_description = "Export selected as PNG / ZIP"


def export_svg(modeladmin, request, queryset):
    return export_zip(queryset, fmt="svg")
export_svg.short_description = "Export selected as SVG ZIP"


def export_scans_csv(modeladmin, request, queryset):
    if queryset.count() == 1:
        return export_scan_csv(queryset.first())
    return HttpResponse("Select a single QR code to export its scans.", status=400)
export_scans_csv.short_description = "Export scan logs as CSV"


def activate_qr(modeladmin, request, queryset):
    queryset.update(is_active=True)
activate_qr.short_description = "Activate selected QR codes"


def deactivate_qr(modeladmin, request, queryset):
    queryset.update(is_active=False)
deactivate_qr.short_description = "Deactivate selected QR codes"


@admin.register(QRCode)
class QRCodeAdmin(admin.ModelAdmin):
    list_display = [
        "name", "qr_type", "slug", "is_active",
        "total_scans", "qr_preview", "created_at",
    ]
    list_filter = ["qr_type", "is_active", "folder", "created_at"]
    search_fields = ["name", "slug", "tags"]
    readonly_fields = ["slug", "total_scans", "qr_preview_large", "created_at", "updated_at"]
    inlines = [ScanLogInline]
    actions = [export_png, export_svg, export_scans_csv, activate_qr, deactivate_qr]

    fieldsets = [
        ("Identity", {"fields": ["name", "tags", "qr_type", "folder", "slug"]}),
        ("Content", {"fields": ["type_data"]}),
        ("Design", {"fields": ["fg_color", "bg_color", "logo", "frame_style", "error_correction"]}),
        ("Access control", {
            "fields": ["password", "scan_limit_day", "active_from", "active_until",
                       "allowed_countries", "is_active"],
            "classes": ["collapse"],
        }),
        ("Stats", {"fields": ["total_scans", "qr_preview_large", "created_at", "updated_at"]}),
    ]

    def qr_preview(self, obj):
        try:
            data = export_qr_code(obj, "png")
            import base64
            b64 = base64.b64encode(data).decode()
            return format_html(
                '<img src="data:image/png;base64,{}" style="width:60px;height:60px;" />', b64
            )
        except Exception:
            return "—"
    qr_preview.short_description = "Preview"

    def qr_preview_large(self, obj):
        try:
            data = export_qr_code(obj, "png")
            import base64
            b64 = base64.b64encode(data).decode()
            return format_html(
                '<img src="data:image/png;base64,{}" style="width:200px;height:200px;" />', b64
            )
        except Exception:
            return "—"
    qr_preview_large.short_description = "QR Preview"


@admin.register(ScanLog)
class ScanLogAdmin(admin.ModelAdmin):
    list_display = ["qr_code", "scanned_at", "country", "city", "device", "browser"]
    list_filter = ["device", "country", "scanned_at"]
    search_fields = ["qr_code__name", "ip_address", "city"]
    readonly_fields = [f.name for f in ScanLog._meta.fields]
    date_hierarchy = "scanned_at"
