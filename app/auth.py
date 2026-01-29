import os
import hashlib
from datetime import datetime, timedelta

import bcrypt
from jose import JWTError, jwt

SECRET_KEY = os.getenv("SECRET_KEY", "neonhire-clean-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24


def _prehash(password: str) -> bytes:
    # always 32 bytes output
    return hashlib.sha256(password.encode("utf-8")).digest()


def hash_password(password: str) -> str:
    pre = _prehash(password)  # 32 bytes
    hashed = bcrypt.hashpw(pre, bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    pre = _prehash(plain_password)  # 32 bytes
    return bcrypt.checkpw(pre, hashed_password.encode("utf-8"))


def create_access_token(subject: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub": subject, "exp": expire}
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> str:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        subject = payload.get("sub")
        if not subject:
            raise JWTError("Missing subject")
        return subject
    except JWTError as exc:
        raise JWTError("Invalid token") from exc
