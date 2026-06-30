from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django_dynamic_qr.models.qr_code


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Folder",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255)),
                ("color", models.CharField(default="#6366f1", max_length=7)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="qr_folders", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["name"], "verbose_name": "Folder", "verbose_name_plural": "Folders", "unique_together": {("user", "name")}},
        ),
        migrations.CreateModel(
            name="QRCode",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255)),
                ("tags", models.CharField(blank=True, help_text="Comma-separated tags", max_length=500)),
                ("qr_type", models.CharField(choices=[("url","URL"),("vcard","vCard"),("vcard_plus","vCard+"),("pdf","PDF"),("menu","Menu"),("social","Social links"),("wifi","WiFi"),("email","Email"),("sms","SMS"),("whatsapp","WhatsApp"),("image","Image"),("text","Plain text"),("link_list","Link list"),("app_store","App store")], max_length=20)),
                ("slug", models.SlugField(default=django_dynamic_qr.models.qr_code._slug, max_length=32, unique=True)),
                ("type_data", models.JSONField(default=dict)),
                ("fg_color", models.CharField(default="#000000", max_length=7)),
                ("bg_color", models.CharField(default="#FFFFFF", max_length=7)),
                ("logo", models.ImageField(blank=True, null=True, upload_to="qr_logos/")),
                ("frame_style", models.CharField(choices=[("none","No frame"),("simple","Simple border"),("scan_me",'"Scan me" label'),("rounded","Rounded label")], default="none", max_length=20)),
                ("error_correction", models.CharField(choices=[("L","L — 7 %"),("M","M — 15 %"),("Q","Q — 25 %"),("H","H — 30 %")], default="H", max_length=1)),
                ("password", models.CharField(blank=True, max_length=128)),
                ("scan_limit_day", models.PositiveIntegerField(blank=True, help_text="Max scans per day (null = unlimited)", null=True)),
                ("active_from", models.DateTimeField(blank=True, null=True)),
                ("active_until", models.DateTimeField(blank=True, null=True)),
                ("allowed_countries", models.JSONField(default=list, help_text='List of ISO 3166-1 alpha-2 codes, e.g. ["IN","US"]')),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("folder", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="qr_codes", to="django_dynamic_qr.folder")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="qr_codes", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-created_at"], "verbose_name": "QR Code", "verbose_name_plural": "QR Codes"},
        ),
        migrations.CreateModel(
            name="ScanLog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("scanned_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("ip_address", models.GenericIPAddressField(blank=True, null=True)),
                ("country", models.CharField(blank=True, max_length=2)),
                ("city", models.CharField(blank=True, max_length=100)),
                ("device", models.CharField(choices=[("mobile","Mobile"),("tablet","Tablet"),("desktop","Desktop"),("unknown","Unknown")], default="unknown", max_length=10)),
                ("os", models.CharField(blank=True, max_length=50)),
                ("browser", models.CharField(blank=True, max_length=50)),
                ("referer", models.URLField(blank=True)),
                ("user_agent", models.TextField(blank=True)),
                ("qr_code", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="scans", to="django_dynamic_qr.qrcode")),
            ],
            options={"ordering": ["-scanned_at"], "verbose_name": "Scan log", "verbose_name_plural": "Scan logs", "indexes": [models.Index(fields=["qr_code","scanned_at"],name="dqr_scan_qr_scanned_idx"), models.Index(fields=["country"],name="dqr_scan_country_idx")]},
        ),
    ]
