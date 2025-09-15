import re, unicodedata
from typing import Optional
_NON_ALNUM = re.compile(r"[^a-z0-9]+"); _DASH_DUP = re.compile(r"-{2,}")
def slugify(text: str, max_length: Optional[int] = 80) -> str:
    if not text: return ""
    text = unicodedata.normalize("NFKD", text).encode("ascii","ignore").decode("ascii")
    text = text.lower().strip(); text = _NON_ALNUM.sub("-", text); text = _DASH_DUP.sub("-", text).strip("-")
    if max_length and len(text) > max_length: text = text[:max_length].rstrip("-")
    return text
