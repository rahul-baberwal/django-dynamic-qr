"""
Management command: generate_qr

Usage:
    python manage.py generate_qr <slug> --fmt png --output /tmp/qr.png
"""
import sys
from django.core.management.base import BaseCommand, CommandError
from django_dynamic_qr.models import QRCode
from django_dynamic_qr.engine.exporter import export_qr_code


class Command(BaseCommand):
    help = "Export a QR code image by slug"

    def add_arguments(self, parser):
        parser.add_argument("slug", type=str, help="QR code slug")
        parser.add_argument("--fmt", default="png", choices=["png", "svg", "pdf", "eps"])
        parser.add_argument("--output", default=None, help="Output file path (default: stdout)")

    def handle(self, *args, **options):
        slug = options["slug"]
        fmt = options["fmt"]
        output = options["output"]

        try:
            qr = QRCode.objects.get(slug=slug)
        except QRCode.DoesNotExist:
            raise CommandError(f"QR code with slug '{slug}' not found.")

        data = export_qr_code(qr, fmt=fmt)

        if output:
            with open(output, "wb") as f:
                f.write(data)
            self.stdout.write(self.style.SUCCESS(f"Saved to {output}"))
        else:
            sys.stdout.buffer.write(data)
