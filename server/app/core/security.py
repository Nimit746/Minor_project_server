import uuid
from datetime import datetime, timedelta, timezone
from functools import lru_cache

import bcrypt
import jwt

from app.config.settings import get_settings
from app.core.exceptions import UnauthorizedException


# ---------- Password hashing (CPU-bound: call via asyncio.to_thread in async code) ----------
def hash_password(plain_password: str) -> str:
    return bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except ValueError:
        return False


@lru_cache
def dummy_hash() -> str:
    """Used to keep login timing constant when the email doesn't exist."""
    return hash_password("not-a-real-password")


# ---------- JWT ----------
def _create_token(subject: str, token_type: str, expires: timedelta, extra: dict | None = None) -> str:
    s = get_settings()
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "type": token_type,
        "iat": now,
        "exp": now + expires,
        "jti": uuid.uuid4().hex,
    }
    if extra:
        payload.update(extra)
    return jwt.encode(payload, s.JWT_SECRET_KEY, algorithm=s.JWT_ALGORITHM)


def create_access_token(subject: str, extra_claims: dict | None = None) -> str:
    s = get_settings()
    return _create_token(subject, "access", timedelta(minutes=s.ACCESS_TOKEN_EXPIRE_MINUTES), extra_claims)


def create_refresh_token(subject: str) -> str:
    s = get_settings()
    return _create_token(subject, "refresh", timedelta(days=s.REFRESH_TOKEN_EXPIRE_DAYS))


def decode_token(token: str, expected_type: str = "access") -> dict:
    """Decode + validate. Raises UnauthorizedException on any problem.

    The `type` check stops a refresh token from being used as an access token (and vice versa).
    """
    s = get_settings()
    try:
        payload = jwt.decode(
            token,
            s.JWT_SECRET_KEY,
            algorithms=[s.JWT_ALGORITHM],
            options={"require": ["exp", "sub", "type"]},
        )
    except jwt.ExpiredSignatureError:
        raise UnauthorizedException("Token expired")
    except jwt.InvalidTokenError:
        raise UnauthorizedException("Invalid token")
    if payload.get("type") != expected_type:
        raise UnauthorizedException("Invalid token type")
    return payload
