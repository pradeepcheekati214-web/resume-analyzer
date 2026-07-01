"""
Password hashing and JWT token utilities.
"""
import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

import bcrypt
from jose import JWTError, jwt

from app.core.config import settings

logger = logging.getLogger(__name__)

# Bcrypt hard-limits input to 72 bytes. We enforce this before calling bcrypt
# so it works identically across all bcrypt versions (4.x raises, older ones truncate silently).
_MAX_PW_BYTES = 72


def _to_bytes(plain_password: str) -> bytes:
    b = plain_password.encode("utf-8")
    return b[:_MAX_PW_BYTES]


# ---------------------------------------------------------------------------
# Password helpers  (using bcrypt directly — avoids passlib version conflicts)
# ---------------------------------------------------------------------------
def hash_password(plain_password: str) -> str:
    hashed = bcrypt.hashpw(_to_bytes(plain_password), bcrypt.gensalt(rounds=12))
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(
            _to_bytes(plain_password),
            hashed_password.encode("utf-8"),
        )
    except Exception:
        return False


# ---------------------------------------------------------------------------
# JWT helpers
# ---------------------------------------------------------------------------
def create_access_token(subject: Any, expires_delta: Optional[timedelta] = None) -> str:
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    payload = {"sub": str(subject), "exp": expire, "type": "access"}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(subject: Any) -> str:
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {"sub": str(subject), "exp": expire, "type": "refresh"}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> Optional[dict]:
    """Decode and validate a JWT. Returns the payload dict or None on failure."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError as exc:
        logger.debug("JWT decode failed: %s", exc)
        return None


def get_subject_from_token(token: str) -> Optional[str]:
    payload = decode_token(token)
    if payload is None:
        return None
    return payload.get("sub")
