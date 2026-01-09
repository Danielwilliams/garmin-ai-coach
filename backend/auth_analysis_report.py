#!/usr/bin/env python3
"""
Comprehensive Authentication System Analysis Report
for Garmin AI Coach Backend
"""

import os
import sys
import json
from datetime import datetime

def analyze_file_structure():
    """Analyze the backend file structure."""
    print("📁 BACKEND FILE STRUCTURE ANALYSIS")
    print("=" * 50)
    
    backend_path = "/mnt/d/Garmin AI Coach Web App/garmin-ai-coach/backend"
    
    key_files = {
        "main.py": "FastAPI app entry point",
        "start.py": "Railway startup script",
        "requirements.txt": "Python dependencies",
        "app/api/auth.py": "Authentication endpoints",
        "app/core/security.py": "Security utilities",
        "app/database/base.py": "Database configuration",
        "app/database/models/user.py": "User model",
        "app/database/models/training_config.py": "Training config model",
        "app/database/models/analysis.py": "Analysis model"
    }
    
    missing_files = []
    existing_files = []
    
    for file_path, description in key_files.items():
        full_path = os.path.join(backend_path, file_path)
        if os.path.exists(full_path):
            size = os.path.getsize(full_path)
            existing_files.append((file_path, description, size))
            print(f"✅ {file_path:<35} - {description} ({size} bytes)")
        else:
            missing_files.append((file_path, description))
            print(f"❌ {file_path:<35} - {description} (MISSING)")
    
    return len(missing_files) == 0, existing_files, missing_files

def analyze_dependencies():
    """Analyze dependencies in requirements.txt."""
    print("\n📦 DEPENDENCIES ANALYSIS")
    print("=" * 50)
    
    req_path = "/mnt/d/Garmin AI Coach Web App/garmin-ai-coach/backend/requirements.txt"
    
    if not os.path.exists(req_path):
        print("❌ requirements.txt not found")
        return False, []
    
    dependencies = []
    
    try:
        with open(req_path, 'r') as f:
            lines = f.readlines()
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):
                dependencies.append(line)
                print(f"📋 {line}")
        
        # Check critical dependencies
        critical_deps = [
            'fastapi', 'uvicorn', 'sqlalchemy', 'asyncpg', 'alembic',
            'python-jose', 'passlib', 'pydantic', 'python-multipart',
            'email-validator'
        ]
        
        found_deps = [dep.split('==')[0].split('[')[0] for dep in dependencies]
        missing_critical = [dep for dep in critical_deps if dep not in found_deps]
        
        if missing_critical:
            print(f"\n❌ Missing critical dependencies: {missing_critical}")
            return False, dependencies
        else:
            print(f"\n✅ All critical dependencies present")
            return True, dependencies
            
    except Exception as e:
        print(f"❌ Error reading requirements.txt: {e}")
        return False, []

def analyze_authentication_endpoints():
    """Analyze authentication API endpoints."""
    print("\n🔐 AUTHENTICATION ENDPOINTS ANALYSIS")
    print("=" * 50)
    
    auth_path = "/mnt/d/Garmin AI Coach Web App/garmin-ai-coach/backend/app/api/auth.py"
    
    if not os.path.exists(auth_path):
        print("❌ auth.py not found")
        return False, []
    
    endpoints = []
    issues = []
    
    try:
        with open(auth_path, 'r') as f:
            content = f.read()
        
        # Check for required endpoints
        required_endpoints = {
            '@router.post("/register"': 'User registration',
            '@router.post("/login"': 'User login',
            '@router.post("/refresh"': 'Token refresh',
            '@router.get("/me"': 'Get current user'
        }
        
        for endpoint, description in required_endpoints.items():
            if endpoint in content:
                endpoints.append((endpoint, description, True))
                print(f"✅ {description:<20} - {endpoint}")
            else:
                endpoints.append((endpoint, description, False))
                issues.append(f"Missing endpoint: {description}")
                print(f"❌ {description:<20} - {endpoint} (MISSING)")
        
        # Check for security measures
        security_checks = {
            'HTTPBearer': 'Bearer token authentication',
            'verify_password': 'Password verification',
            'get_password_hash': 'Password hashing',
            'create_access_token': 'Access token creation',
            'create_refresh_token': 'Refresh token creation',
            'HTTPException': 'Error handling'
        }
        
        print(f"\n🛡️  Security Features:")
        for feature, description in security_checks.items():
            if feature in content:
                print(f"✅ {description}")
            else:
                issues.append(f"Missing security feature: {description}")
                print(f"❌ {description} (MISSING)")
        
        return len(issues) == 0, endpoints
        
    except Exception as e:
        print(f"❌ Error reading auth.py: {e}")
        return False, []

def analyze_security_configuration():
    """Analyze security configuration."""
    print("\n🔒 SECURITY CONFIGURATION ANALYSIS")
    print("=" * 50)
    
    security_path = "/mnt/d/Garmin AI Coach Web App/garmin-ai-coach/backend/app/core/security.py"
    
    if not os.path.exists(security_path):
        print("❌ security.py not found")
        return False, []
    
    security_features = []
    issues = []
    
    try:
        with open(security_path, 'r') as f:
            content = f.read()
        
        # Check security configurations
        security_checks = {
            'SECRET_KEY = os.getenv': 'Environment-based secret key',
            'ALGORITHM = "HS256"': 'JWT algorithm specification',
            'ACCESS_TOKEN_EXPIRE_MINUTES': 'Token expiration configuration',
            'bcrypt': 'bcrypt password hashing',
            'CryptContext': 'Password context configuration',
            'jwt.encode': 'JWT token creation',
            'jwt.decode': 'JWT token verification',
            'HTTPException': 'Security error handling'
        }
        
        for check, description in security_checks.items():
            if check in content:
                security_features.append((description, True))
                print(f"✅ {description}")
            else:
                security_features.append((description, False))
                issues.append(f"Missing: {description}")
                print(f"❌ {description} (MISSING)")
        
        # Check for potential security issues
        potential_issues = []
        
        if 'SECRET_KEY = "your-secret-key-here"' in content:
            potential_issues.append("Default secret key detected")
        
        if 'bcrypt__rounds=12' not in content:
            potential_issues.append("bcrypt rounds not explicitly set")
        
        if potential_issues:
            print(f"\n⚠️  Potential Security Issues:")
            for issue in potential_issues:
                print(f"⚠️  {issue}")
                issues.append(issue)
        
        return len(issues) == 0, security_features
        
    except Exception as e:
        print(f"❌ Error reading security.py: {e}")
        return False, []

def analyze_database_models():
    """Analyze database models."""
    print("\n🗄️  DATABASE MODELS ANALYSIS")
    print("=" * 50)
    
    models_path = "/mnt/d/Garmin AI Coach Web App/garmin-ai-coach/backend/app/database/models"
    
    model_files = {
        "user.py": "User and authentication models",
        "training_config.py": "Training configuration models", 
        "analysis.py": "Analysis and result models"
    }
    
    models_status = []
    issues = []
    
    for file_name, description in model_files.items():
        file_path = os.path.join(models_path, file_name)
        
        if not os.path.exists(file_path):
            models_status.append((file_name, description, False))
            issues.append(f"Missing model file: {file_name}")
            print(f"❌ {file_name:<20} - {description} (MISSING)")
            continue
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            models_status.append((file_name, description, True))
            print(f"✅ {file_name:<20} - {description}")
            
            # Check User model specifically
            if file_name == "user.py":
                user_fields = [
                    'email', 'full_name', 'hashed_password', 
                    'is_active', 'is_verified'
                ]
                
                print(f"   User model fields:")
                for field in user_fields:
                    if field in content:
                        print(f"   ✅ {field}")
                    else:
                        print(f"   ❌ {field} (MISSING)")
                        issues.append(f"Missing User field: {field}")
        
        except Exception as e:
            models_status.append((file_name, description, False))
            issues.append(f"Error reading {file_name}: {e}")
            print(f"❌ {file_name:<20} - Error: {e}")
    
    return len(issues) == 0, models_status

def analyze_database_configuration():
    """Analyze database configuration."""
    print("\n💾 DATABASE CONFIGURATION ANALYSIS")
    print("=" * 50)
    
    db_path = "/mnt/d/Garmin AI Coach Web App/garmin-ai-coach/backend/app/database/base.py"
    
    if not os.path.exists(db_path):
        print("❌ database/base.py not found")
        return False, []
    
    db_features = []
    issues = []
    
    try:
        with open(db_path, 'r') as f:
            content = f.read()
        
        # Check database configurations
        db_checks = {
            'create_async_engine': 'Async database engine',
            'AsyncSession': 'Async session support',
            'DeclarativeBase': 'SQLAlchemy base model',
            'get_db': 'Database dependency injection',
            'init_database': 'Database initialization',
            'UUID': 'UUID primary key support',
            'postgresql+asyncpg': 'AsyncPG PostgreSQL driver'
        }
        
        for check, description in db_checks.items():
            if check in content:
                db_features.append((description, True))
                print(f"✅ {description}")
            else:
                db_features.append((description, False))
                issues.append(f"Missing: {description}")
                print(f"❌ {description} (MISSING)")
        
        # Check environment variable usage
        if 'DATABASE_URL' in content or 'DATABASE_PUBLIC_URL' in content:
            print(f"✅ Environment-based database URL")
        else:
            issues.append("No environment-based database URL")
            print(f"❌ No environment-based database URL")
        
        return len(issues) == 0, db_features
        
    except Exception as e:
        print(f"❌ Error reading database/base.py: {e}")
        return False, []

def analyze_main_application():
    """Analyze main application configuration."""
    print("\n🚀 MAIN APPLICATION ANALYSIS")
    print("=" * 50)
    
    main_path = "/mnt/d/Garmin AI Coach Web App/garmin-ai-coach/backend/main.py"
    
    if not os.path.exists(main_path):
        print("❌ main.py not found")
        return False, []
    
    app_features = []
    issues = []
    
    try:
        with open(main_path, 'r') as f:
            content = f.read()
        
        # Check FastAPI configurations
        app_checks = {
            'FastAPI(': 'FastAPI application',
            'CORSMiddleware': 'CORS support',
            'lifespan': 'Application lifespan events',
            'init_database': 'Database initialization on startup',
            'auth_router': 'Authentication router',
            'app.include_router': 'Router inclusion',
            '@app.get("/health")': 'Health check endpoint',
            '@app.get("/")': 'Root endpoint'
        }
        
        for check, description in app_checks.items():
            if check in content:
                app_features.append((description, True))
                print(f"✅ {description}")
            else:
                app_features.append((description, False))
                issues.append(f"Missing: {description}")
                print(f"❌ {description} (MISSING)")
        
        # Check for potential issues
        if 'allow_origins=["*"]' in content:
            issues.append("CORS allows all origins - security risk in production")
            print(f"⚠️  CORS allows all origins - security risk in production")
        
        return len(issues) == 0, app_features
        
    except Exception as e:
        print(f"❌ Error reading main.py: {e}")
        return False, []

def create_test_scenarios():
    """Create manual test scenarios for authentication endpoints."""
    print("\n🧪 AUTHENTICATION TEST SCENARIOS")
    print("=" * 50)
    
    scenarios = [
        {
            "name": "Health Check",
            "endpoint": "GET /health",
            "description": "Basic server health check",
            "expected": "200 OK with status message",
            "curl": 'curl -X GET "http://localhost:8000/health"'
        },
        {
            "name": "User Registration",
            "endpoint": "POST /api/v1/auth/register",
            "description": "Register a new user account",
            "expected": "200 OK with user data",
            "curl": 'curl -X POST "http://localhost:8000/api/v1/auth/register" -H "Content-Type: application/json" -d \'{"email": "test@example.com", "full_name": "Test User", "password": "testpassword123"}\''
        },
        {
            "name": "User Login",
            "endpoint": "POST /api/v1/auth/login",
            "description": "Authenticate user and get tokens",
            "expected": "200 OK with access and refresh tokens",
            "curl": 'curl -X POST "http://localhost:8000/api/v1/auth/login" -H "Content-Type: application/json" -d \'{"email": "test@example.com", "password": "testpassword123"}\''
        },
        {
            "name": "Get Current User",
            "endpoint": "GET /api/v1/auth/me",
            "description": "Get authenticated user information",
            "expected": "200 OK with user data",
            "curl": 'curl -X GET "http://localhost:8000/api/v1/auth/me" -H "Authorization: Bearer YOUR_ACCESS_TOKEN"'
        },
        {
            "name": "Token Refresh",
            "endpoint": "POST /api/v1/auth/refresh",
            "description": "Refresh access token using refresh token",
            "expected": "200 OK with new tokens",
            "curl": 'curl -X POST "http://localhost:8000/api/v1/auth/refresh" -H "Content-Type: application/json" -d \'{"refresh_token": "YOUR_REFRESH_TOKEN"}\''
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"{i}. {scenario['name']}")
        print(f"   Endpoint: {scenario['endpoint']}")
        print(f"   Description: {scenario['description']}")
        print(f"   Expected: {scenario['expected']}")
        print(f"   Test: {scenario['curl']}")
        print()
    
    return scenarios

def generate_comprehensive_report():
    """Generate comprehensive authentication system analysis report."""
    print("🔍 GARMIN AI COACH BACKEND AUTHENTICATION ANALYSIS")
    print("=" * 70)
    print(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Backend Path: /mnt/d/Garmin AI Coach Web App/garmin-ai-coach/backend/")
    print("=" * 70)
    
    # Run all analyses
    analyses = [
        ("File Structure", analyze_file_structure),
        ("Dependencies", analyze_dependencies),
        ("Authentication Endpoints", analyze_authentication_endpoints),
        ("Security Configuration", analyze_security_configuration),
        ("Database Models", analyze_database_models),
        ("Database Configuration", analyze_database_configuration),
        ("Main Application", analyze_main_application)
    ]
    
    results = {}
    overall_score = 0
    total_analyses = len(analyses)
    
    for name, analysis_func in analyses:
        try:
            success, details = analysis_func()
            results[name] = {"success": success, "details": details}
            if success:
                overall_score += 1
        except Exception as e:
            print(f"❌ Error in {name} analysis: {e}")
            results[name] = {"success": False, "details": f"Error: {e}"}
    
    # Create test scenarios
    test_scenarios = create_test_scenarios()
    
    # Generate summary report
    print("\n" + "=" * 70)
    print("📊 ANALYSIS SUMMARY")
    print("=" * 70)
    
    for name, result in results.items():
        status = "✅ PASS" if result["success"] else "❌ FAIL"
        print(f"{name:<25}: {status}")
    
    score_percentage = (overall_score / total_analyses) * 100
    print(f"\nOverall Score: {overall_score}/{total_analyses} ({score_percentage:.1f}%)")
    
    # Issues and recommendations
    print("\n🚨 IDENTIFIED ISSUES")
    print("-" * 30)
    
    issues_found = []
    
    # Dependencies issue
    if not results["Dependencies"]["success"]:
        issues_found.append("Missing Python dependencies - run: pip install -r requirements.txt")
    
    # Environment configuration
    database_url = os.getenv("DATABASE_URL") or os.getenv("DATABASE_PUBLIC_URL")
    secret_key = os.getenv("SECRET_KEY")
    
    if not database_url:
        issues_found.append("DATABASE_URL not configured - needed for production deployment")
    
    if not secret_key or secret_key == "your-secret-key-here":
        issues_found.append("SECRET_KEY not properly configured - security risk")
    
    # Authentication endpoint issues
    if not results["Authentication Endpoints"]["success"]:
        issues_found.append("Authentication endpoints missing or incomplete")
    
    if issues_found:
        for issue in issues_found:
            print(f"• {issue}")
    else:
        print("No major issues identified!")
    
    # Recommendations
    print("\n💡 RECOMMENDATIONS")
    print("-" * 30)
    
    recommendations = [
        "Install dependencies: pip install -r requirements.txt",
        "Set DATABASE_URL environment variable for database connection",
        "Set SECRET_KEY environment variable with a secure random string",
        "Test server startup: python start.py or uvicorn main:app --reload",
        "Run authentication endpoint tests using the provided curl commands",
        "Verify database connectivity and table creation",
        "Test user registration, login, and token refresh flows",
        "Configure CORS origins for production deployment"
    ]
    
    for rec in recommendations:
        print(f"• {rec}")
    
    # Next steps
    print("\n🎯 NEXT STEPS FOR TESTING")
    print("-" * 30)
    
    if overall_score >= total_analyses * 0.7:  # 70% or better
        print("✅ Authentication system structure looks good!")
        print("1. Install missing dependencies")
        print("2. Configure environment variables")
        print("3. Start the server")
        print("4. Run endpoint tests")
        print("5. Verify database operations")
    else:
        print("⚠️  Authentication system needs fixes before testing")
        print("1. Fix structural issues identified above")
        print("2. Ensure all required files are present")
        print("3. Review authentication logic")
        print("4. Test individual components")
        
    return overall_score >= total_analyses * 0.7

if __name__ == "__main__":
    success = generate_comprehensive_report()
    sys.exit(0 if success else 1)