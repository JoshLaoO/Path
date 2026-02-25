from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from config import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY

# BCrypt has a 72-byte password limit.
BCRYPT_MAX_PASSWORD_BYTES = 72


def _to_bcrypt_bytes(password: str) -> bytes:
    """Encode password to bytes and truncate to bcrypt's 72-byte limit."""
    return password.encode("utf-8")[:BCRYPT_MAX_PASSWORD_BYTES]


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(_to_bcrypt_bytes(password), salt)
    return hashed.decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(
        _to_bcrypt_bytes(plain),
        hashed.encode("utf-8"),
    )


def create_access_token(subject: str | int) -> str:
    """Create a JWT with sub=subject (user id)."""
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": str(subject), "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict | None:
    """Decode and validate JWT; return payload or None if invalid."""
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.InvalidTokenError:
        return None
