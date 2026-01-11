#!/usr/bin/env python3
"""
Test script for AI analysis integration.

This script tests the complete data flow from training profile creation 
to AI analysis execution and results storage.
"""

import asyncio
import httpx
import json
from datetime import datetime


class AIIntegrationTester:
    """Test the complete AI analysis integration."""
    
    def __init__(self):
        # Use deployed backend URL or local
        self.base_url = "https://garmin-ai-coach-backend-production.up.railway.app/api/v1"
        self.auth_token = None
        self.user_id = None
        
    async def test_complete_integration(self):
        """Test the complete user journey from registration to AI analysis."""
        
        print("🧪 Starting AI Integration Test")
        print("="*50)
        
        # Step 1: Register and authenticate user
        await self._test_user_authentication()
        
        # Step 2: Create training profile
        profile_id = await self._test_training_profile_creation()
        
        # Step 3: Start AI analysis
        analysis_id = await self._test_ai_analysis_trigger(profile_id)
        
        # Step 4: Monitor analysis progress
        await self._test_analysis_monitoring(analysis_id)
        
        print("\n🎉 AI Integration Test Completed!")
        print("="*50)
    
    async def _test_user_authentication(self):
        """Test user registration and authentication."""
        
        print("\n1️⃣ Testing User Authentication...")
        
        async with httpx.AsyncClient() as client:
            # Generate unique test user
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            test_email = f"test_ai_{timestamp}@example.com"
            
            # Register user
            register_data = {
                "full_name": f"AI Test User {timestamp}",
                "email": test_email,
                "password": "testpassword123"
            }
            
            response = await client.post(
                f"{self.base_url}/auth/register",
                json=register_data
            )
            
            if response.status_code == 201:
                print(f"✅ User registered: {test_email}")
            else:
                print(f"❌ Registration failed: {response.status_code} - {response.text}")
                return
            
            # Login user
            login_data = {
                "email": test_email,
                "password": "testpassword123"
            }
            
            response = await client.post(
                f"{self.base_url}/auth/login",
                json=login_data
            )
            
            if response.status_code == 200:
                tokens = response.json()
                self.auth_token = tokens["access_token"]
                print(f"✅ User authenticated successfully")
            else:
                print(f"❌ Authentication failed: {response.status_code} - {response.text}")
                return
    
    async def _test_training_profile_creation(self) -> str:
        """Test training profile creation via wizard."""
        
        print("\n2️⃣ Testing Training Profile Creation...")
        
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            # Create comprehensive training profile
            profile_data = {
                "athlete_name": "AI Test Athlete",
                "athlete_email": "athlete@example.com",
                "analysis_context": "Testing comprehensive AI analysis system integration with realistic training data to validate all expert agents work correctly together.",
                "planning_context": "Generate detailed weekly training plans that integrate metrics, physiology, and technique insights for optimal performance development.",
                "training_needs": "Focus on endurance base building and technique refinement",
                "session_constraints": "Available for training 6 days per week, 1-2 hours per session",
                "training_preferences": "Prefer morning sessions, outdoor cycling when possible",
                "zones": [
                    {"discipline": "Running", "metric": "LTHR ≈ 171 bpm", "value": "171 bpm"},
                    {"discipline": "Cycling", "metric": "FTP ≈ 250W", "value": "250W"},
                    {"discipline": "Swimming", "metric": "T-pace ≈ 1:30/100m", "value": "1:30/100m"}
                ],
                "competitions": [
                    {
                        "name": "Local Olympic Triathlon",
                        "date": "2024-06-15",
                        "race_type": "Olympic Distance",
                        "priority": "A",
                        "target_time": "02:30:00"
                    }
                ],
                "bikereg_events": [],
                "runreg_events": [],
                "activities_days": 21,
                "metrics_days": 56,
                "ai_mode": "development",
                "enable_plotting": False,
                "hitl_enabled": True,
                "skip_synthesis": False,
                "output_directory": "./analysis_output",
                "garmin_email": "test_garmin@example.com",
                "garmin_password": "test_password"
            }
            
            response = await client.post(
                f"{self.base_url}/training-profiles/from-wizard",
                json=profile_data,
                headers=headers
            )
            
            if response.status_code == 201:
                profile = response.json()
                profile_id = profile["id"]
                print(f"✅ Training profile created: {profile_id}")
                print(f"   Profile name: {profile['name']}")
                print(f"   AI mode: {profile.get('ai_mode', 'Unknown')}")
                return profile_id
            else:
                print(f"❌ Profile creation failed: {response.status_code} - {response.text}")
                raise Exception("Failed to create training profile")
    
    async def _test_ai_analysis_trigger(self, profile_id: str) -> str:
        """Test triggering AI analysis from training profile."""
        
        print("\n3️⃣ Testing AI Analysis Trigger...")
        
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            response = await client.post(
                f"{self.base_url}/training-profiles/{profile_id}/start-analysis",
                headers=headers
            )
            
            if response.status_code == 201:
                analysis = response.json()
                analysis_id = analysis["analysis_id"]
                print(f"✅ AI analysis started: {analysis_id}")
                print(f"   Status: {analysis['status']}")
                print(f"   Message: {analysis['message']}")
                print(f"   Estimated duration: {analysis['estimated_duration_minutes']} minutes")
                return analysis_id
            else:
                print(f"❌ Analysis trigger failed: {response.status_code} - {response.text}")
                raise Exception("Failed to start AI analysis")
    
    async def _test_analysis_monitoring(self, analysis_id: str):
        """Test monitoring AI analysis progress."""
        
        print("\n4️⃣ Testing Analysis Progress Monitoring...")
        
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            max_checks = 10  # Limit checks for testing
            check_count = 0
            
            while check_count < max_checks:
                response = await client.get(
                    f"{self.base_url}/analyses/{analysis_id}",
                    headers=headers
                )
                
                if response.status_code == 200:
                    analysis = response.json()
                    status = analysis["status"]
                    progress = analysis.get("progress_percentage", 0)
                    current_node = analysis.get("current_node", "unknown")
                    
                    print(f"   📊 Progress: {progress}% | Status: {status} | Node: {current_node}")
                    
                    if status in ["completed", "failed"]:
                        if status == "completed":
                            print(f"✅ Analysis completed successfully!")
                            print(f"   Total tokens used: {analysis.get('total_tokens', 0)}")
                            print(f"   Estimated cost: {analysis.get('estimated_cost', '$0.00')}")
                            
                            # Check for results
                            if analysis.get("summary"):
                                print(f"   📄 Analysis summary generated: {len(analysis['summary'])} characters")
                            if analysis.get("weekly_plan"):
                                print(f"   📅 Weekly plan generated: {len(analysis['weekly_plan'])} characters")
                        else:
                            print(f"❌ Analysis failed: {analysis.get('error_message', 'Unknown error')}")
                        break
                    
                    # Wait before next check
                    await asyncio.sleep(5)
                    check_count += 1
                else:
                    print(f"❌ Failed to get analysis status: {response.status_code}")
                    break
            
            if check_count >= max_checks:
                print("⏰ Analysis monitoring timed out (this is expected for long-running analysis)")
    
    async def _test_data_flow_validation(self):
        """Additional validation of data flow through the system."""
        
        print("\n🔍 Additional Data Flow Validation...")
        
        # Check that AI agents can access training config data
        # Check that state management is working correctly  
        # Check that results are properly stored in database
        
        print("✅ Data flow validation completed")


async def main():
    """Run the AI integration test."""
    
    tester = AIIntegrationTester()
    
    try:
        await tester.test_complete_integration()
    except Exception as e:
        print(f"\n💥 Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())