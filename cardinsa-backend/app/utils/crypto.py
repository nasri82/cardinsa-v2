import base64
import hashlib
import hmac
import os
from typing import Tuple

# Format: pbkdf2_sha256$<iterations>$<salt_b64>$<hash_b64>
ALGORITHM = "pbkdf2_sha256"
ITERATIONS = 120_000
SALT_BYTES = 16

def _pbkdf2(password: str, salt: bytes, iterations: int = ITERATIONS) -> bytes:
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)

def get_password_hash(password: str) -> str:
    salt = os.urandom(SALT_BYTES)
    dk = _pbkdf2(password, salt, ITERATIONS)
    return f"{ALGORITHM}${ITERATIONS}${base64.b64encode(salt).decode()}${base64.b64encode(dk).decode()}"

def verify_password(password: str, hashed: str) -> bool:
    try:
        algo, iter_str, salt_b64, hash_b64 = hashed.split("$", 3)
        if algo != ALGORITHM:
            return False
        iterations = int(iter_str)
        salt = base64.b64decode(salt_b64.encode())
        expected = base64.b64decode(hash_b64.encode())
        test = _pbkdf2(password, salt, iterations)
        return hmac.compare_digest(test, expected)
    except Exception:
        return False
