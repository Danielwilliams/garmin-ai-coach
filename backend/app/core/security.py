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

# Password hashing with explicit bcrypt configuration
pwd_context = CryptContext(
    schemes=["bcrypt"], 
    deprecated="auto",
    bcrypt__rounds=12,
    bcrypt__ident="2b",
    # Handle bcrypt backend selection more robustly
    bcrypt__default_rounds=12
)

# Token-related exceptions
credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    # Truncate password to 72 bytes for bcrypt compatibility
    password_bytes = plain_password.encode('utf-8')
    if len(password_bytes) > 72:
        # Safely truncate at byte boundary to avoid malformed UTF-8
        password_bytes = password_bytes[:72]
        while len(password_bytes) > 0:
            try:
                plain_password = password_bytes.decode('utf-8')
                break
            except UnicodeDecodeError:
                password_bytes = password_bytes[:-1]
        if len(password_bytes) == 0:
            # Fallback: use first 72 characters instead of bytes
            plain_password = plain_password[:72]
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    try:
        # Truncate password to 72 bytes for bcrypt compatibility
        password_bytes = password.encode('utf-8')
        if len(password_bytes) > 72:
            logger.warning(f"Password truncated from {len(password_bytes)} bytes to 72 bytes")
            # Safely truncate at byte boundary to avoid malformed UTF-8
            password_bytes = password_bytes[:72]
            while len(password_bytes) > 0:
                try:
                    password = password_bytes.decode('utf-8')
                    break
                except UnicodeDecodeError:
                    password_bytes = password_bytes[:-1]
            if len(password_bytes) == 0:
                # Fallback: use first 72 characters instead of bytes
                password = password[:72]
                logger.warning("Used character-based truncation fallback")
        
        return pwd_context.hash(password)
    except Exception as e:
        logger.error(f"Password hashing error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password processing failed"
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