#!/usr/bin/env python
"""Test script to check if analyses module can be imported."""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_analyses_import():
    try:
        print("Testing analyses module import...")
        
        # Test individual components first
        print("1. Testing schemas...")
        from app.schemas.analysis import AnalysisSummary, AnalysisWithResults
        print("   ✅ Schemas imported successfully")
        
        print("2. Testing database models...")
        from app.database.models.analysis import Analysis, AnalysisResult
        print("   ✅ Database models imported successfully")
        
        print("3. Testing dependencies...")
        from app.dependencies import get_current_user
        print("   ✅ Dependencies imported successfully")
        
        print("4. Testing database base...")
        from app.database.base import get_db
        print("   ✅ Database base imported successfully")
        
        print("5. Testing analyses router...")
        from app.api.analyses import router
        print("   ✅ Analyses router imported successfully")
        
        # Check router configuration
        print(f"   Router prefix: {router.prefix}")
        print(f"   Router tags: {router.tags}")
        print(f"   Number of routes: {len(router.routes)}")
        
        for route in router.routes:
            print(f"   - {route.methods} {route.path}")
        
        print("\n✅ All imports successful!")
        return True
        
    except Exception as e:
        print(f"\n❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_analyses_import()
    sys.exit(0 if success else 1)