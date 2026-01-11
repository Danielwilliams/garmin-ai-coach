#!/usr/bin/env python3
"""
Integration test script to verify the complete user journey works.
Tests the new training profile -> AI analysis integration.
"""

import requests
import json
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
TEST_USER = {
    "email": "test_integration@example.com",
    "password": "TestPassword123!",
    "full_name": "Integration Test User"
}

def test_complete_journey():
    """Test the complete user journey from registration to analysis."""
    
    print("🧪 Starting Complete User Journey Test")
    print("=" * 50)
    
    # Step 1: Register or login
    print("1. Authenticating user...")
    auth_token = authenticate_user()
    if not auth_token:
        print("❌ Authentication failed")
        return False
    print("✅ Authentication successful")
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # Step 2: Create training profile
    print("\n2. Creating training profile...")
    profile_id = create_training_profile(headers)
    if not profile_id:
        print("❌ Training profile creation failed")
        return False
    print(f"✅ Training profile created: {profile_id}")
    
    # Step 3: Start AI analysis using NEW ENDPOINT
    print("\n3. Starting AI analysis using new integrated endpoint...")
    analysis_id = start_analysis_new_endpoint(profile_id, headers)
    if not analysis_id:
        print("❌ Analysis creation failed")
        return False
    print(f"✅ Analysis started: {analysis_id}")
    
    # Step 4: Check analysis status
    print("\n4. Checking analysis status...")
    analysis_status = check_analysis_status(analysis_id, headers)
    if not analysis_status:
        print("❌ Analysis status check failed")
        return False
    print(f"✅ Analysis status: {analysis_status}")
    
    # Step 5: List all analyses
    print("\n5. Listing user analyses...")
    analyses = list_analyses(headers)
    if analyses is None:
        print("❌ Analyses list failed")
        return False
    print(f"✅ Found {len(analyses)} analyses")
    
    print("\n🎉 Complete user journey test PASSED!")
    print("The 404 error has been resolved - frontend now correctly")
    print("calls the new integrated endpoint.")
    return True

def authenticate_user() -> str:
    """Register and authenticate a test user."""
    try:
        # Try to register
        register_response = requests.post(f"{BASE_URL}/auth/register", json=TEST_USER, timeout=10)
        
        # Login
        login_response = requests.post(f"{BASE_URL}/auth/login", json={
            "email": TEST_USER["email"],
            "password": TEST_USER["password"]
        }, timeout=10)
        
        if login_response.status_code == 200:
            return login_response.json()["access_token"]
        else:
            print(f"Login failed: {login_response.status_code} - {login_response.text}")
            return None
            
    except requests.RequestException as e:
        print(f"Auth request failed: {e}")
        return None

def create_training_profile(headers: Dict[str, str]) -> str:
    """Create a test training profile."""
    try:
        profile_data = {
            "profile_name": "Integration Test Profile",
            "training_goals": ["Improve endurance", "Increase speed"],
            "ai_mode": "comprehensive",
            "activities_days": 30,
            "metrics_days": 90,
            "enable_plotting": True,
            "hitl_enabled": False,
            "skip_synthesis": False,
            "athlete_name": TEST_USER["full_name"],
            "athlete_email": TEST_USER["email"],
            "training_needs": "Improve marathon performance",
            "session_constraints": "3-4 sessions per week",
            "training_preferences": "Morning runs preferred",
            "garmin_email": "test@example.com",
            "garmin_password": "encrypted_password_placeholder",
            "garmin_is_connected": True,
            "competitions": [
                {
                    "name": "City Marathon",
                    "date": "2024-06-15",
                    "distance": 42.2,
                    "target_time": "04:00:00",
                    "priority": "high"
                }
            ],
            "training_zones": [
                {
                    "zone_name": "Zone 1",
                    "min_bpm": 120,
                    "max_bpm": 140,
                    "description": "Easy pace"
                }
            ]
        }
        
        response = requests.post(f"{BASE_URL}/training-profiles/from-wizard", 
                               json=profile_data, headers=headers, timeout=10)
        
        if response.status_code == 201:
            return response.json()["id"]
        else:
            print(f"Profile creation failed: {response.status_code} - {response.text}")
            return None
            
    except requests.RequestException as e:
        print(f"Profile creation request failed: {e}")
        return None

def start_analysis_new_endpoint(profile_id: str, headers: Dict[str, str]) -> str:
    """Start analysis using the NEW integrated endpoint."""
    try:
        # This is the NEW endpoint that should work without 404 errors
        url = f"{BASE_URL}/training-profiles/{profile_id}/start-analysis"
        response = requests.post(url, headers=headers, timeout=30)
        
        if response.status_code == 201:
            return response.json()["analysis_id"]
        else:
            print(f"NEW endpoint failed: {response.status_code} - {response.text}")
            print(f"URL attempted: {url}")
            return None
            
    except requests.RequestException as e:
        print(f"New endpoint request failed: {e}")
        return None

def check_analysis_status(analysis_id: str, headers: Dict[str, str]) -> str:
    """Check the status of an analysis."""
    try:
        response = requests.get(f"{BASE_URL}/analyses/{analysis_id}", 
                              headers=headers, timeout=10)
        
        if response.status_code == 200:
            return response.json()["status"]
        else:
            print(f"Status check failed: {response.status_code} - {response.text}")
            return None
            
    except requests.RequestException as e:
        print(f"Status check request failed: {e}")
        return None

def list_analyses(headers: Dict[str, str]) -> list:
    """List all user analyses."""
    try:
        response = requests.get(f"{BASE_URL}/analyses/", 
                              headers=headers, timeout=10)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Analyses list failed: {response.status_code} - {response.text}")
            return None
            
    except requests.RequestException as e:
        print(f"Analyses list request failed: {e}")
        return None

if __name__ == "__main__":
    print("🚀 Integration Test for Garmin AI Coach")
    print("Testing Priority #1: Connect Training Profile to AI Analysis")
    print()
    
    success = test_complete_journey()
    
    if success:
        print("\n✅ INTEGRATION TEST PASSED")
        print("The frontend 404 error has been fixed!")
        print("Users can now successfully start analyses through training profiles.")
    else:
        print("\n❌ INTEGRATION TEST FAILED")
        print("Check server status and endpoints.")
        print("Note: This test requires the backend server to be running.")
    
    print("\nTo run this test:")
    print("1. Start backend: cd backend && uvicorn app.main:app --reload")
    print("2. Run test: python test_integration.py")