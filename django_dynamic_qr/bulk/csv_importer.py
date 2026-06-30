"""
Bulk-create QR codes from a CSV file.

Required CSV columns: name, qr_type, [type-specific columns as JSON string in 'data']
Example row: My Website,url,"{""url"": ""https://example.com""}"
"""
import csv
import io
import json


def import_from_csv(csv_file, user, folder=None) -> tuple[int, list[str]]:
    """
    Import QR codes from an uploaded CSV file.

    :param csv_file: file-like object (text or bytes)
    :param user: AUTH_USER_MODEL instance
    :param folder: optional Folder instance
    :returns: (created_count, error_list)
    """
    from django_dynamic_qr.models import QRCode

    if isinstance(csv_file.read(0), bytes):
        text = io.TextIOWrapper(csv_file, encoding="utf-8-sig")
    else:
        csv_file.seek(0)
        text = csv_file

    reader = csv.DictReader(text)
    created = 0
    errors = []

    for idx, row in enumerate(reader, start=2):
        try:
            name = row.get("name", "").strip()
            qr_type = row.get("qr_type", "").strip()
            raw_data = row.get("data", "{}")
            type_data = json.loads(raw_data)

            if not name or not qr_type:
                errors.append(f"Row {idx}: 'name' and 'qr_type' are required.")
                continue

            qr = QRCode(
                user=user,
                folder=folder,
                name=name,
                qr_type=qr_type,
                type_data=type_data,
            )
            # Validate via handler
            handler = qr.get_type_handler()
            handler_errors = handler.validate()
            if handler_errors:
                errors.append(f"Row {idx}: {'; '.join(handler_errors)}")
                continue

            qr.save()
            created += 1
        except json.JSONDecodeError as exc:
            errors.append(f"Row {idx}: Invalid JSON in 'data' column — {exc}")
        except Exception as exc:
            errors.append(f"Row {idx}: {exc}")

    return created, errors
