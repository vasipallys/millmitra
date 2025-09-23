"""
Simple System Validation Script
Tests core system components without Unicode issues
"""

import os
import sys
import requests
import json
import time
from pathlib import Path
from datetime import datetime

def test_environment():
    """Test environment configuration"""
    print("Testing Environment Configuration...")
    
    backend_path = Path(__file__).parent
    
    # Check .env files
    env_file = backend_path / ".env"
    prod_env_file = backend_path / ".env.production"
    
    results = []
    
    if env_file.exists():
        results.append("PASS: Development environment file exists")
    else:
        results.append("FAIL: Development environment file missing")
    
    if prod_env_file.exists():
        results.append("PASS: Production environment file exists")
    else:
        results.append("WARN: Production environment file missing")
    
    return results

def test_backend():
    """Test backend API"""
    print("Testing Backend API...")
    
    results = []
    
    try:
        response = requests.get("http://127.0.0.1:5000/api/health", timeout=5)
        if response.status_code == 200:
            results.append("PASS: Backend health endpoint responding")
            
            health_data = response.json()
            if 'status' in health_data:
                results.append(f"PASS: Backend status: {health_data['status']}")
            
        else:
            results.append(f"FAIL: Backend returned status {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        results.append("FAIL: Cannot connect to backend - not running")
    except Exception as e:
        results.append(f"FAIL: Backend test error: {str(e)}")
    
    return results

def test_ai_services():
    """Test AI services"""
    print("Testing AI Services...")
    
    results = []
    
    try:
        response = requests.get("http://127.0.0.1:8000/health", timeout=5)
        if response.status_code == 200:
            results.append("PASS: AI services responding")
        else:
            results.append(f"FAIL: AI services returned status {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        results.append("FAIL: Cannot connect to AI services - not running")
    except Exception as e:
        results.append(f"FAIL: AI services test error: {str(e)}")
    
    return results

def test_database():
    """Test database"""
    print("Testing Database...")
    
    results = []
    
    try:
        sys.path.append(str(Path(__file__).parent))
        from app import create_app
        
        # Create app and test database connection within app context
        app = create_app()
        with app.app_context():
            from extensions import db
            from sqlalchemy import text
            # Test database connection
            result = db.session.execute(text('SELECT 1')).scalar()
            if result == 1:
                results.append("PASS: Database connection working")
            else:
                results.append("FAIL: Database connection test failed")
            
    except ImportError as e:
        results.append(f"FAIL: Cannot import app or database: {str(e)}")
    except Exception as e:
        results.append(f"FAIL: Database test error: {str(e)}")
    
    return results

def main():
    """Main validation function"""
    print("=" * 50)
    print("Rice Mill System Validation")
    print("=" * 50)
    
    all_results = []
    
    # Run all tests
    test_functions = [
        ("Environment", test_environment),
        ("Backend", test_backend),
        ("AI Services", test_ai_services),
        ("Database", test_database)
    ]
    
    for test_name, test_func in test_functions:
        print(f"\n{test_name} Tests:")
        try:
            results = test_func()
            for result in results:
                print(f"  {result}")
                all_results.append(result)
        except Exception as e:
            error_msg = f"FAIL: {test_name} test crashed: {str(e)}"
            print(f"  {error_msg}")
            all_results.append(error_msg)
    
    # Summary
    print("\n" + "=" * 50)
    print("VALIDATION SUMMARY")
    print("=" * 50)
    
    pass_count = len([r for r in all_results if r.startswith("PASS")])
    fail_count = len([r for r in all_results if r.startswith("FAIL")])
    warn_count = len([r for r in all_results if r.startswith("WARN")])
    total_count = len(all_results)
    
    print(f"Total Tests: {total_count}")
    print(f"Passed: {pass_count}")
    print(f"Failed: {fail_count}")
    print(f"Warnings: {warn_count}")
    
    if fail_count == 0:
        print("\nSTATUS: SYSTEM VALIDATION SUCCESSFUL!")
        print("System is ready for operation")
        return True
    else:
        print(f"\nSTATUS: SYSTEM NEEDS ATTENTION")
        print(f"{fail_count} critical issues found")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
