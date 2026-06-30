from .base import BaseQRType
from .url import URLType
from .vcard import VCardType
from .vcard_plus import VCardPlusType
from .pdf import PDFType
from .menu import MenuType
from .social_links import SocialLinksType
from .wifi import WiFiType
from .email_type import EmailType
from .sms import SMSType
from .whatsapp import WhatsAppType
from .image import ImageType
from .plain_text import PlainTextType
from .link_list import LinkListType
from .app_store import AppStoreType

# Central registry: type_id → handler class
registry: dict[str, type[BaseQRType]] = {}


def _register(*classes):
    for cls in classes:
        registry[cls.type_id] = cls


_register(
    URLType, VCardType, VCardPlusType, PDFType, MenuType,
    SocialLinksType, WiFiType, EmailType, SMSType, WhatsAppType,
    ImageType, PlainTextType, LinkListType, AppStoreType,
)

__all__ = [
    "BaseQRType", "registry",
    "URLType", "VCardType", "VCardPlusType", "PDFType", "MenuType",
    "SocialLinksType", "WiFiType", "EmailType", "SMSType", "WhatsAppType",
    "ImageType", "PlainTextType", "LinkListType", "AppStoreType",
]
