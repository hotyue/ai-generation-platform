from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import jwt, JWTError

from backend.app.config import JWT_SECRET, JWT_ALGORITHM


def create_access_token(data: dict, expires_minutes: int = 60 * 24 * 7) -> str:
    """
    默认 7 天过期
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except JWTError:
        return None
