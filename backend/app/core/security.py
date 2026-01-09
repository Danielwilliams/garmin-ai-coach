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

# Password hashing with robust bcrypt configuration for production
pwd_context = CryptContext(
    schemes=["bcrypt"], 
    deprecated="auto",
    bcrypt__rounds=12,
    bcrypt__ident="2b",
    # Disable automatic backend detection to avoid version issues
    bcrypt__default_rounds=12
)

# Token-related exceptions
credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash with consistent truncation."""
    # Apply the same truncation logic as get_password_hash
    if len(plain_password) > 70:  # Leave some buffer under 72 bytes
        plain_password = plain_password[:70]
    
    # Additional safety check for byte length
    password_bytes = plain_password.encode('utf-8')
    if len(password_bytes) > 70:
        # If still too long, truncate by characters more aggressively
        plain_password = plain_password[:60]  # Even more conservative
    
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password with aggressive truncation for bcrypt compatibility."""
    try:
        # Aggressively truncate to ensure compatibility
        if len(password) > 70:  # Leave some buffer under 72 bytes
            password = password[:70]
            logger.warning(f"Password truncated to {len(password)} characters for bcrypt compatibility")
        
        # Additional safety check for byte length
        password_bytes = password.encode('utf-8')
        if len(password_bytes) > 70:
            # If still too long, truncate by characters more aggressively
            password = password[:60]  # Even more conservative
            logger.warning("Used aggressive character truncation for bcrypt compatibility")
        
        return pwd_context.hash(password)
    except Exception as e:
        logger.error(f"Password hashing error: {str(e)}")
        # Try one more fallback with even shorter password
        try:
            short_password = password[:50]  # Very conservative truncation
            logger.warning("Attempting fallback with 50-character password limit")
            return pwd_context.hash(short_password)
        except Exception as fallback_error:
            logger.error(f"Fallback password hashing also failed: {str(fallback_error)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Password processing failed - password may be too complex"
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