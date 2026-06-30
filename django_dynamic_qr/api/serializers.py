from rest_framework import serializers
from django_dynamic_qr.models import QRCode, ScanLog, Folder


class FolderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Folder
        fields = ["id", "name", "color", "created_at"]
        read_only_fields = ["id", "created_at"]


class QRCodeSerializer(serializers.ModelSerializer):
    total_scans = serializers.ReadOnlyField()
    redirect_url = serializers.SerializerMethodField()

    class Meta:
        model = QRCode
        fields = [
            "id", "name", "tags", "qr_type", "slug", "type_data",
            "fg_color", "bg_color", "logo", "frame_style", "error_correction",
            "password", "scan_limit_day", "active_from", "active_until",
            "allowed_countries", "is_active",
            "folder", "total_scans", "redirect_url",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "slug", "total_scans", "redirect_url", "created_at", "updated_at"]

    def get_redirect_url(self, obj):
        return obj.get_redirect_url()

    def validate(self, data):
        # Run type-handler validation
        qr_type = data.get("qr_type") or (self.instance.qr_type if self.instance else None)
        type_data = data.get("type_data") or (self.instance.type_data if self.instance else {})
        if qr_type and type_data:
            from django_dynamic_qr.types import registry
            handler_class = registry.get(qr_type)
            if handler_class:
                dummy_qr = type("_DummyQR", (), {"type_data": type_data, "get_redirect_url": lambda s: ""})()
                errors = handler_class(dummy_qr).validate()
                if errors:
                    raise serializers.ValidationError({"type_data": errors})
        return data


class ScanLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScanLog
        fields = [
            "id", "scanned_at", "country", "city",
            "device", "os", "browser", "referer",
        ]


class AnalyticsSummarySerializer(serializers.Serializer):
    total_scans = serializers.IntegerField()
    scans_today = serializers.IntegerField()
    top_countries = serializers.ListField()
    top_devices = serializers.ListField()
    daily_counts = serializers.ListField()
