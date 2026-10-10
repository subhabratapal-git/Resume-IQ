import os

from datetime import datetime, timedelta, timezone

import jwt

from jwt.exceptions import InvalidTokenError

from pwdlib import PasswordHash


password_hash = PasswordHash.recommended()


SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development").lower()

if not SECRET_KEY:
    if ENVIRONMENT == "production":
        raise RuntimeError("CRITICAL: JWT_SECRET_KEY environment variable is mandatory in production!")
    SECRET_KEY = "resumeiq-local-development-secret-key-change-before-deployment"

ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_HOURS = 24


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:

    return password_hash.verify(
        plain_password,
        hashed_password
    )


def create_access_token(user_id: int, token_version: int = 1) -> str:

    now = datetime.now(timezone.utc)

    expire = now + timedelta(
        hours=ACCESS_TOKEN_EXPIRE_HOURS
    )

    payload = {
        "sub": str(user_id),
        "ver": int(token_version or 1),
        "iat": now,
        "exp": expire
    }

    token = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return token



def decode_access_token(token: str):

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        return payload

    except InvalidTokenError:
        return None
  
  
  