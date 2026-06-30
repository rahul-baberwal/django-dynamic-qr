from .base import BaseQRType


class VCardType(BaseQRType):
    """
    Static vCard — encodes contact info directly into QR matrix.
    type_data keys: first_name, last_name, phone, email, company,
                    title, address, website
    """
    type_id = "vcard"
    is_static = True

    def get_destination(self) -> str:
        d = self.data
        lines = ["BEGIN:VCARD", "VERSION:3.0"]
        name = f"{d.get('last_name', '')};{d.get('first_name', '')}"
        lines.append(f"N:{name}")
        full = f"{d.get('first_name', '')} {d.get('last_name', '')}".strip()
        lines.append(f"FN:{full}")
        if d.get("company"):
            lines.append(f"ORG:{d['company']}")
        if d.get("title"):
            lines.append(f"TITLE:{d['title']}")
        if d.get("phone"):
            lines.append(f"TEL;TYPE=WORK,VOICE:{d['phone']}")
        if d.get("email"):
            lines.append(f"EMAIL:{d['email']}")
        if d.get("website"):
            lines.append(f"URL:{d['website']}")
        if d.get("address"):
            lines.append(f"ADR:;;{d['address']};;;;")
        lines.append("END:VCARD")
        return "\n".join(lines)

    def validate(self):
        errors = []
        if not (self.get("first_name") or self.get("last_name")):
            errors.append("At least first or last name is required.")
        return errors
