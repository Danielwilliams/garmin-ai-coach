"""Authentication and security utilities."""

import os
import logging
from datetime import datetime, timedelta
from typing import Optional, Union
from jose import JWTError, jwt
from fastapi import HTTPException, status
from passlib.context import CryptContext

logger = logging.getLogger(__name__)

# Security settings
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing with Argon2 - more reliable than bcrypt in production
pwd_context = CryptContext(
    schemes=["argon2", "scrypt", "pbkdf2_sha256"],  # Multiple secure schemes with fallbacks
    default="argon2",
    deprecated="auto",
    # Argon2 configuration (secure defaults)
    argon2__rounds=4,
    argon2__memory_cost=65536,  # 64 MB
    argon2__parallelism=1,
    # Scrypt fallback configuration
    scrypt__rounds=32768,
    scrypt__block_size=8,
    scrypt__parallelism=1,
    # PBKDF2 fallback configuration
    pbkdf2_sha256__rounds=100000
)

# Token-related exceptions
credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        logger.error(f"Password verification error: {str(e)}")
        return False


def get_password_hash(password: str) -> str:
    """Hash a password using Argon2/scrypt (no length limitations)."""
    try:
        return pwd_context.hash(password)
    except Exception as e:
        logger.error(f"Password hashing error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password hashing failed"
        )


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[str]:
    """Verify a JWT token and return the user ID."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
        return user_id
    except JWTError:
        return None


def create_refresh_token(user_id: str) -> str:
    """Create a refresh token (longer-lived)."""
    expire = datetime.utcnow() + timedelta(days=7)
    to_encode = {"sub": user_id, "exp": expire, "type": "refresh"}
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_refresh_token(token: str) -> Optional[str]:
    """Verify a refresh token and return user ID."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "refresh":
            return None
        user_id: str = payload.get("sub")
        return user_id
    except JWTError:
        return None