"""FastAPI dependencies for authentication and database."""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from app.database.base import get_db
from app.database.models.user import User
from app.core.security import verify_token

security = HTTPBearer()

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Get current user from JWT token."""
    
    # Verify the token
    user_id = verify_token(credentials.credentials)
    if user_id is None:
        raise credentials_exception
    
    # Get the user from database
    try:
        query = select(User).where(User.id == UUID(user_id))
        result = await db.execute(query)
        user = result.scalar_one_or_none()
    except Exception:
        raise credentials_exception
    
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    
    return user