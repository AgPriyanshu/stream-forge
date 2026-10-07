from datetime import datetime, timedelta, timezone

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from models import User
from settings import settings

hasher = PasswordHasher()

# Verified against when the email is unknown, so timing doesn't reveal valid emails.
DUMMY_HASH = hasher.hash("dummy-password")


def hash_password(password: str) -> str:
    return hasher.hash(password)


def verify_password(password_hash: str, password: str) -> bool:
    try:
        return hasher.verify(password_hash, password)
    except VerifyMismatchError:
        return False


def create_access_token(user: User) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user.id),
        "tenant_id": str(user.tenant_id),
        "role": "authenticated",
        "key": settings.jwt_consumer_key,
        "iat": now,
        "exp": now + timedelta(minutes=settings.access_token_ttl_minutes),
    }

    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
