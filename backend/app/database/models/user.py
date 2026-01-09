"""User and authentication models."""

from sqlalchemy import Column, String, Boolean, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database.base import Base
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User(Base):
    """User model for authentication and profile."""
    
    email = Column(String(254), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    hashed_password = Column(String(128), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    # Profile fields from coach config
    athlete_context = Column(Text, nullable=True)  # Analysis context
    planning_context = Column(Text, nullable=True)  # Planning context
    
    # Relationships
    # garmin_account = relationship("GarminAccount", back_populates="user", uselist=False)
    # training_configs = relationship("TrainingConfig", back_populates="user")
    # analyses = relationship("Analysis", back_populates="user")
    
    def verify_password(self, password: str) -> bool:
        """Verify password against hash."""
        return pwd_context.verify(password, self.hashed_password)
    
    @classmethod
    def hash_password(cls, password: str) -> str:
        """Hash a password."""
        return pwd_context.hash(password)
    
    def set_password(self, password: str):
        """Set password (hashes it automatically)."""
        self.hashed_password = self.hash_password(password)


class GarminAccount(Base):
    """Garmin Connect account integration."""
    
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)  # Foreign key to User
    email = Column(String(254), nullable=False)  # Garmin Connect email
    encrypted_password = Column(String(512), nullable=True)  # Encrypted Garmin password (optional)
    
    # Connection status
    is_connected = Column(Boolean, default=False, nullable=False)
    last_sync = Column(DateTime(timezone=True), nullable=True)
    sync_error = Column(Text, nullable=True)
    
    # Data extraction settings
    activities_days = Column(String(10), default="21", nullable=False)
    metrics_days = Column(String(10), default="56", nullable=False)
    
    # Relationships
    # user = relationship("User", back_populates="garmin_account")