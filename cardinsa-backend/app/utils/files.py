from __future__ import annotations
import os
from pathlib import Path
from typing import Iterable
SAFE_CHARS = "-_.() "
def safe_filename(name: str, replace_with: str = "_") -> str:
    keep = set(chr(c) for c in range(ord('a'), ord('z')+1)) | set(chr(c) for c in range(ord('A'), ord('Z')+1)) | set(chr(c) for c in range(ord('0'), ord('9')+1)) | set(SAFE_CHARS)
    return "".join(c if c in keep else replace_with for c in name)
def ensure_dir(path: Path) -> None: path.mkdir(parents=True, exist_ok=True)
def build_storage_path(*parts: Iterable[str | os.PathLike]) -> Path:
    p = Path("."); 
    for part in parts:
        if isinstance(part, (list, tuple)):
            for sub in part: p = p / str(sub)
        else: p = p / str(part)
    ensure_dir(p); return p
def get_static_path(base_dir: str, type_name: str, owner_id: str, filename: str) -> Path:
    filename = safe_filename(filename); p = Path(base_dir) / type_name / owner_id / filename
    ensure_dir(p.parent); return p
def allowed_extension(filename: str, allowed: set[str]) -> bool:
    ext = (filename.rsplit(".", 1)[-1] or "").lower(); return ext in allowed
