import re, uuid
_EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
_PHONE_RE = re.compile(r"^[0-9+()\-\s]{6,20}$")
_IBAN_RE = re.compile(r"^[A-Z]{2}[0-9]{2}[A-Z0-9]{1,30}$")
def is_email(value: str) -> bool: return bool(_EMAIL_RE.match(value or ""))
def is_phone(value: str) -> bool: return bool(_PHONE_RE.match(value or ""))
def is_iban(value: str) -> bool: return bool(_IBAN_RE.match(value or ""))
def is_uuid(value: str) -> bool:
    try: uuid.UUID(str(value)); return True
    except Exception: return False
