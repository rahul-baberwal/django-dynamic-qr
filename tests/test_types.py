"""
Basic tests for QR type handlers.
Run with: pytest tests/ (after pip install -e . and pip install pytest-django)
"""
import pytest
from django_dynamic_qr.types import registry, URLType, WiFiType, VCardType


class FakeQR:
    def __init__(self, type_data):
        self.type_data = type_data
    def get_redirect_url(self):
        return "https://example.com/qr/abc123/"


def test_url_type_destination():
    qr = FakeQR({"url": "https://anthropic.com"})
    handler = URLType(qr)
    assert handler.get_destination() == "https://anthropic.com"


def test_url_type_validation_fails_without_url():
    qr = FakeQR({})
    handler = URLType(qr)
    errors = handler.validate()
    assert len(errors) == 1


def test_wifi_type_is_static():
    qr = FakeQR({"ssid": "MyNetwork", "password": "secret", "security": "WPA"})
    handler = WiFiType(qr)
    assert handler.is_static is True
    content = handler.get_destination()
    assert "WIFI:T:WPA;S:MyNetwork;P:secret" in content


def test_vcard_type_generates_valid_vcard():
    qr = FakeQR({"first_name": "Rakesh", "last_name": "Mishra", "phone": "+911234567890"})
    handler = VCardType(qr)
    content = handler.get_destination()
    assert "BEGIN:VCARD" in content
    assert "FN:Rakesh Mishra" in content
    assert "END:VCARD" in content


def test_all_14_types_registered():
    expected = {
        "url", "vcard", "vcard_plus", "pdf", "menu", "social",
        "wifi", "email", "sms", "whatsapp", "image", "text",
        "link_list", "app_store",
    }
    assert set(registry.keys()) == expected


@pytest.mark.parametrize("type_id", [
    "url", "vcard", "vcard_plus", "pdf", "menu", "social",
    "wifi", "email", "sms", "whatsapp", "image", "text",
    "link_list", "app_store",
])
def test_handler_has_type_id_set(type_id):
    handler_class = registry[type_id]
    assert handler_class.type_id == type_id
