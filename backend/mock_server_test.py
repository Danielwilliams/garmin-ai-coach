#!/usr/bin/env python3
"""
Mock Server Test for Garmin AI Coach Authentication System
Simulates authentication flow without requiring full dependencies
"""

import json
import hashlib
import hmac
import base64
from datetime import datetime, timedelta
import uuid
import re

class MockPasswordContext:
    """Mock password hashing context"""
    
    def hash(self, password):
        """Simple hash for testing - NOT for production"""
        return hashlib.pbkdf2_hmac('sha256', password.encode(), b'salt', 100000).hex()
    
    def verify(self, password, hashed):
        """Verify password against hash"""
        return self.hash(password) == hashed

class MockJWTHandler:
    """Mock JWT token handler"""
    
    def __init__(self, secret_key="test-secret-key"):
        self.secret_key = secret_key
    
    def encode(self, payload):
        """Create a simple JWT-like token"""
        header = {"alg": "HS256", "typ": "JWT"}
        
        # Create signature-like string
        data = json.dumps(header) + json.dumps(payload)
        signature = hmac.new(
            self.secret_key.encode(),
            data.encode(),
            hashlib.sha256
        ).hexdigest()[:16]
        
        return f"{base64.b64encode(json.dumps(payload).encode()).decode()}.{signature}"
    
    def decode(self, token):
        """Decode JWT-like token"""
        try:
            payload_b64, signature = token.split('.')
            payload = json.loads(base64.b64decode(payload_b64).decode())
            
            # Check expiration
            if 'exp' in payload:
                exp_time = datetime.fromtimestamp(payload['exp'])
                if datetime.utcnow() > exp_time:
                    raise Exception("Token expired")
            
            return payload
        except:
            raise Exception("Invalid token")

class MockDatabase:
    """Mock database for testing"""
    
    def __init__(self):
        self.users = {}
    
    def add_user(self, email, full_name, hashed_password):
        """Add user to mock database"""
        user_id = str(uuid.uuid4())
        user = {
            'id': user_id,
            'email': email,
            'full_name': full_name,
            'hashed_password': hashed_password,
            'is_active': True,
            'is_verified': False,
            'created_at': datetime.utcnow().isoformat()
        }
        self.users[email] = user
        return user
    
    def get_user_by_email(self, email):
        """Get user by email"""
        return self.users.get(email)
    
    def get_user_by_id(self, user_id):
        """Get user by ID"""
        for user in self.users.values():
            if user['id'] == user_id:
                return user
        return None

class MockAuthenticationSystem:
    """Mock authentication system that simulates the actual FastAPI backend"""
    
    def __init__(self):
        self.pwd_context = MockPasswordContext()
        self.jwt_handler = MockJWTHandler()
        self.db = MockDatabase()
        self.access_token_expire_minutes = 30
    
    def validate_email(self, email):
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def register_user(self, email, full_name, password):
        """Register a new user"""
        # Validate input
        if not self.validate_email(email):
            return {"error": "Invalid email format"}, 400
        
        if len(password) < 8:
            return {"error": "Password must be at least 8 characters"}, 400
        
        if len(full_name.strip()) < 2:
            return {"error": "Full name must be at least 2 characters"}, 400
        
        # Check if user already exists
        if self.db.get_user_by_email(email):
            return {"error": "Email already registered"}, 400
        
        # Hash password and create user
        hashed_password = self.pwd_context.hash(password)
        user = self.db.add_user(email, full_name, hashed_password)
        
        # Return user response (without password)
        return {
            "id": user['id'],
            "email": user['email'],
            "full_name": user['full_name'],
            "is_active": user['is_active'],
            "is_verified": user['is_verified'],
            "created_at": user['created_at']
        }, 201
    
    def login_user(self, email, password):
        """Authenticate user and return tokens"""
        # Find user
        user = self.db.get_user_by_email(email)
        if not user:
            return {"error": "Incorrect email or password"}, 401
        
        # Verify password
        if not self.pwd_context.verify(password, user['hashed_password']):
            return {"error": "Incorrect email or password"}, 401
        
        if not user['is_active']:
            return {"error": "Inactive user"}, 400
        
        # Create tokens
        access_token = self.create_access_token(user['id'])
        refresh_token = self.create_refresh_token(user['id'])
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }, 200
    
    def create_access_token(self, user_id):
        """Create access token"""
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        payload = {
            "sub": user_id,
            "exp": expire.timestamp()
        }
        return self.jwt_handler.encode(payload)
    
    def create_refresh_token(self, user_id):
        """Create refresh token"""
        expire = datetime.utcnow() + timedelta(days=7)
        payload = {
            "sub": user_id,
            "exp": expire.timestamp(),
            "type": "refresh"
        }
        return self.jwt_handler.encode(payload)
    
    def verify_access_token(self, token):
        """Verify access token and return user"""
        try:
            payload = self.jwt_handler.decode(token)
            user_id = payload.get("sub")
            if not user_id:
                return None, 401
            
            user = self.db.get_user_by_id(user_id)
            if not user or not user['is_active']:
                return None, 401
            
            return user, 200
        except:
            return None, 401
    
    def refresh_tokens(self, refresh_token):
        """Refresh access token using refresh token"""
        try:
            payload = self.jwt_handler.decode(refresh_token)
            if payload.get("type") != "refresh":
                return {"error": "Invalid refresh token"}, 401
            
            user_id = payload.get("sub")
            user = self.db.get_user_by_id(user_id)
            
            if not user or not user['is_active']:
                return {"error": "User not found or inactive"}, 401
            
            # Create new tokens
            access_token = self.create_access_token(user_id)
            new_refresh_token = self.create_refresh_token(user_id)
            
            return {
                "access_token": access_token,
                "refresh_token": new_refresh_token,
                "token_type": "bearer"
            }, 200
            
        except:
            return {"error": "Invalid refresh token"}, 401
    
    def get_current_user(self, token):
        """Get current user from access token"""
        user, status = self.verify_access_token(token)
        if user:
            return {
                "id": user['id'],
                "email": user['email'],
                "full_name": user['full_name'],
                "is_active": user['is_active'],
                "is_verified": user['is_verified'],
                "created_at": user['created_at']
            }, 200
        else:
            return {"error": "Could not validate credentials"}, status

def run_authentication_tests():
    """Run comprehensive authentication flow tests"""
    print("🧪 MOCK AUTHENTICATION SYSTEM TESTS")
    print("=" * 50)
    
    auth_system = MockAuthenticationSystem()
    test_results = []
    
    # Test 1: User Registration
    print("\n1️⃣  Testing User Registration")
    print("-" * 30)
    
    # Valid registration
    result, status = auth_system.register_user(
        "test@example.com", 
        "Test User", 
        "testpassword123"
    )
    
    if status == 201:
        print("✅ User registration successful")
        print(f"   User ID: {result['id']}")
        print(f"   Email: {result['email']}")
        test_results.append(("User Registration - Valid", True))
    else:
        print(f"❌ User registration failed: {result}")
        test_results.append(("User Registration - Valid", False))
    
    # Duplicate registration
    result2, status2 = auth_system.register_user(
        "test@example.com", 
        "Another User", 
        "anotherpassword123"
    )
    
    if status2 == 400 and "already registered" in result2.get('error', ''):
        print("✅ Duplicate email rejected")
        test_results.append(("User Registration - Duplicate", True))
    else:
        print(f"❌ Duplicate email not properly rejected: {result2}")
        test_results.append(("User Registration - Duplicate", False))
    
    # Invalid email
    result3, status3 = auth_system.register_user(
        "invalid-email", 
        "Test User", 
        "testpassword123"
    )
    
    if status3 == 400 and "email" in result3.get('error', '').lower():
        print("✅ Invalid email rejected")
        test_results.append(("User Registration - Invalid Email", True))
    else:
        print(f"❌ Invalid email not properly rejected: {result3}")
        test_results.append(("User Registration - Invalid Email", False))
    
    # Test 2: User Login
    print("\n2️⃣  Testing User Login")
    print("-" * 30)
    
    # Valid login
    login_result, login_status = auth_system.login_user(
        "test@example.com", 
        "testpassword123"
    )
    
    if login_status == 200 and "access_token" in login_result:
        print("✅ User login successful")
        print(f"   Access token: {login_result['access_token'][:30]}...")
        print(f"   Refresh token: {login_result['refresh_token'][:30]}...")
        access_token = login_result['access_token']
        refresh_token = login_result['refresh_token']
        test_results.append(("User Login - Valid", True))
    else:
        print(f"❌ User login failed: {login_result}")
        test_results.append(("User Login - Valid", False))
        return test_results
    
    # Invalid credentials
    invalid_login, invalid_status = auth_system.login_user(
        "test@example.com", 
        "wrongpassword"
    )
    
    if invalid_status == 401:
        print("✅ Invalid credentials rejected")
        test_results.append(("User Login - Invalid Password", True))
    else:
        print(f"❌ Invalid credentials not properly rejected: {invalid_login}")
        test_results.append(("User Login - Invalid Password", False))
    
    # Test 3: Get Current User
    print("\n3️⃣  Testing Get Current User")
    print("-" * 30)
    
    user_result, user_status = auth_system.get_current_user(access_token)
    
    if user_status == 200 and user_result['email'] == "test@example.com":
        print("✅ Get current user successful")
        print(f"   Email: {user_result['email']}")
        print(f"   Full Name: {user_result['full_name']}")
        test_results.append(("Get Current User - Valid Token", True))
    else:
        print(f"❌ Get current user failed: {user_result}")
        test_results.append(("Get Current User - Valid Token", False))
    
    # Invalid token
    invalid_user, invalid_user_status = auth_system.get_current_user("invalid_token")
    
    if invalid_user_status == 401:
        print("✅ Invalid token rejected")
        test_results.append(("Get Current User - Invalid Token", True))
    else:
        print(f"❌ Invalid token not properly rejected: {invalid_user}")
        test_results.append(("Get Current User - Invalid Token", False))
    
    # Test 4: Token Refresh
    print("\n4️⃣  Testing Token Refresh")
    print("-" * 30)
    
    refresh_result, refresh_status = auth_system.refresh_tokens(refresh_token)
    
    if refresh_status == 200 and "access_token" in refresh_result:
        print("✅ Token refresh successful")
        print(f"   New access token: {refresh_result['access_token'][:30]}...")
        test_results.append(("Token Refresh - Valid", True))
    else:
        print(f"❌ Token refresh failed: {refresh_result}")
        test_results.append(("Token Refresh - Valid", False))
    
    # Invalid refresh token
    invalid_refresh, invalid_refresh_status = auth_system.refresh_tokens("invalid_refresh_token")
    
    if invalid_refresh_status == 401:
        print("✅ Invalid refresh token rejected")
        test_results.append(("Token Refresh - Invalid Token", True))
    else:
        print(f"❌ Invalid refresh token not properly rejected: {invalid_refresh}")
        test_results.append(("Token Refresh - Invalid Token", False))
    
    return test_results

def generate_test_summary(test_results):
    """Generate test summary"""
    print("\n" + "=" * 50)
    print("📊 AUTHENTICATION TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    success_rate = (passed / total) * 100
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<35}: {status}")
    
    print(f"\nResults: {passed}/{total} tests passed ({success_rate:.1f}%)")
    
    if success_rate >= 90:
        print("🎉 Excellent! Authentication logic is working correctly")
    elif success_rate >= 70:
        print("✅ Good! Most authentication features working")
    else:
        print("⚠️  Issues detected in authentication logic")
    
    return success_rate >= 90

if __name__ == "__main__":
    test_results = run_authentication_tests()
    success = generate_test_summary(test_results)
    
    print("\n💡 NEXT STEPS")
    print("-" * 20)
    if success:
        print("• Install dependencies: pip install -r requirements.txt")
        print("• Configure DATABASE_URL and SECRET_KEY environment variables")
        print("• Start server: python start.py")
        print("• Run real endpoint tests with curl commands")
    else:
        print("• Review authentication logic implementation")
        print("• Fix identified issues in the code")
        print("• Re-run tests before proceeding to server testing")