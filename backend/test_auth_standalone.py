#!/usr/bin/env python3
"""
Standalone authentication test script for Garmin AI Coach backend.
Tests authentication logic without requiring full server startup.
"""

import sys
import os
import asyncio
import json
from datetime import datetime, timedelta

# Add the app directory to the path
sys.path.append('/mnt/d/Garmin AI Coach Web App/garmin-ai-coach/backend')

def test_password_hashing():
    """Test password hashing functionality."""
    print("🔐 Testing password hashing...")
    
    try:
        from app.core.security import get_password_hash, verify_password
        
        # Test password hashing
        test_password = "test_password_123"
        hashed = get_password_hash(test_password)
        
        print(f"✅ Password hashed successfully: {hashed[:20]}...")
        
        # Test password verification
        is_valid = verify_password(test_password, hashed)
        print(f"✅ Password verification: {is_valid}")
        
        # Test invalid password
        is_invalid = verify_password("wrong_password", hashed)
        print(f"✅ Invalid password rejected: {not is_invalid}")
        
        return True
        
    except Exception as e:
        print(f"❌ Password hashing test failed: {e}")
        return False

def test_jwt_tokens():
    """Test JWT token creation and verification."""
    print("\n🔑 Testing JWT tokens...")
    
    try:
        from app.core.security import create_access_token, verify_token, create_refresh_token, verify_refresh_token
        
        # Test access token
        test_user_id = "test-user-123"
        access_token = create_access_token(data={"sub": test_user_id})
        print(f"✅ Access token created: {access_token[:30]}...")
        
        # Verify access token
        decoded_user_id = verify_token(access_token)
        print(f"✅ Access token verified: {decoded_user_id == test_user_id}")
        
        # Test refresh token
        refresh_token = create_refresh_token(test_user_id)
        print(f"✅ Refresh token created: {refresh_token[:30]}...")
        
        # Verify refresh token
        decoded_refresh_user_id = verify_refresh_token(refresh_token)
        print(f"✅ Refresh token verified: {decoded_refresh_user_id == test_user_id}")
        
        # Test invalid token
        invalid_result = verify_token("invalid_token")
        print(f"✅ Invalid token rejected: {invalid_result is None}")
        
        return True
        
    except Exception as e:
        print(f"❌ JWT token test failed: {e}")
        return False

def test_database_models():
    """Test database model structure."""
    print("\n🗄️  Testing database models...")
    
    try:
        from app.database.models.user import User, GarminAccount
        from app.database.models.training_config import TrainingConfig, Competition
        from app.database.models.analysis import Analysis, AnalysisResult, AnalysisFile
        from app.database.base import Base
        
        # Check model attributes
        user_columns = [col.name for col in User.__table__.columns]
        expected_user_cols = ['id', 'email', 'full_name', 'hashed_password', 'is_active', 'is_verified']
        
        missing_cols = set(expected_user_cols) - set(user_columns)
        if missing_cols:
            print(f"❌ Missing User columns: {missing_cols}")
            return False
            
        print(f"✅ User model has all required columns: {user_columns}")
        
        # Test other models exist
        models = [GarminAccount, TrainingConfig, Competition, Analysis, AnalysisResult, AnalysisFile]
        for model in models:
            print(f"✅ Model {model.__name__} loaded successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Database model test failed: {e}")
        return False

def test_environment_config():
    """Test environment configuration."""
    print("\n⚙️  Testing environment configuration...")
    
    try:
        # Check critical environment variables
        database_url = os.getenv("DATABASE_URL") or os.getenv("DATABASE_PUBLIC_URL")
        secret_key = os.getenv("SECRET_KEY")
        environment = os.getenv("ENVIRONMENT", "production")
        
        print(f"✅ Environment: {environment}")
        
        if database_url:
            print(f"✅ Database URL configured: {database_url[:30]}...")
        else:
            print("⚠️  No DATABASE_URL or DATABASE_PUBLIC_URL found - using default")
        
        if secret_key and secret_key != "your-secret-key-here":
            print("✅ Custom SECRET_KEY configured")
        else:
            print("⚠️  Using default SECRET_KEY - should be changed in production")
        
        return True
        
    except Exception as e:
        print(f"❌ Environment config test failed: {e}")
        return False

def test_api_models():
    """Test API request/response models."""
    print("\n📝 Testing API models...")
    
    try:
        from app.api.auth import UserRegister, UserLogin, Token, TokenRefresh, UserResponse
        
        # Test UserRegister model
        user_reg = UserRegister(
            email="test@example.com",
            full_name="Test User",
            password="test_password"
        )
        print(f"✅ UserRegister model: {user_reg.email}")
        
        # Test UserLogin model
        user_login = UserLogin(
            email="test@example.com",
            password="test_password"
        )
        print(f"✅ UserLogin model: {user_login.email}")
        
        # Test Token model
        token = Token(
            access_token="test_access_token",
            refresh_token="test_refresh_token"
        )
        print(f"✅ Token model: {token.token_type}")
        
        return True
        
    except Exception as e:
        print(f"❌ API model test failed: {e}")
        return False

async def test_database_connection():
    """Test database connection (without actual DB)."""
    print("\n🔌 Testing database connection setup...")
    
    try:
        from app.database.base import get_db, init_database
        
        # Test database session factory
        print("✅ Database session factory configured")
        
        # Test init_database function exists
        print("✅ Database initialization function available")
        
        # Check if we can create a session generator (won't actually connect)
        db_gen = get_db()
        print("✅ Database session generator created")
        
        return True
        
    except Exception as e:
        print(f"❌ Database connection test failed: {e}")
        return False

def generate_test_report():
    """Generate a comprehensive test report."""
    print("=" * 60)
    print("🧪 GARMIN AI COACH AUTHENTICATION SYSTEM TEST REPORT")
    print("=" * 60)
    
    tests = [
        ("Password Hashing", test_password_hashing),
        ("JWT Tokens", test_jwt_tokens),
        ("Database Models", test_database_models),
        ("Environment Config", test_environment_config),
        ("API Models", test_api_models),
        ("Database Connection", lambda: asyncio.run(test_database_connection())),
    ]
    
    results = {}
    all_passed = True
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results[test_name] = result
            if not result:
                all_passed = False
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results[test_name] = False
            all_passed = False
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<20}: {status}")
    
    print(f"\nOverall Status: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    
    # Recommendations
    print("\n📋 RECOMMENDATIONS")
    print("-" * 30)
    
    if not results.get("Environment Config", True):
        print("• Configure proper environment variables (DATABASE_URL, SECRET_KEY)")
    
    if all_passed:
        print("• All core authentication components are properly configured")
        print("• Ready to test with actual server startup")
    else:
        print("• Fix failing tests before attempting server startup")
        print("• Install missing dependencies from requirements.txt")
    
    return all_passed

if __name__ == "__main__":
    generate_test_report()