#!/usr/bin/env python3

"""
PWA Features Testing Script
Tests Progressive Web App functionality for Smart Rice Mill ERP
"""

import requests
import json
import time
import subprocess
import os
from pathlib import Path

def test_pwa_files():
    """Test if PWA files are accessible"""
    print("🔍 Testing PWA Files Accessibility")
    print("=" * 50)
    
    base_url = "http://localhost:3000"
    pwa_files = [
        "/manifest.json",
        "/sw.js", 
        "/offline.html",
        "/logo192.png",
        "/logo512.png"
    ]
    
    results = {}
    
    for file_path in pwa_files:
        try:
            response = requests.get(f"{base_url}{file_path}", timeout=5)
            if response.status_code == 200:
                print(f"✅ {file_path} - Accessible (Status: {response.status_code})")
                results[file_path] = "✅ Accessible"
            else:
                print(f"❌ {file_path} - Error (Status: {response.status_code})")
                results[file_path] = f"❌ Error {response.status_code}"
        except requests.exceptions.RequestException as e:
            print(f"❌ {file_path} - Connection Error: {e}")
            results[file_path] = f"❌ Connection Error"
    
    return results

def test_manifest_content():
    """Test manifest.json content"""
    print("\n📱 Testing Manifest Content")
    print("=" * 50)
    
    try:
        response = requests.get("http://localhost:3000/manifest.json", timeout=5)
        if response.status_code == 200:
            manifest = response.json()
            
            required_fields = [
                "name", "short_name", "start_url", "display", 
                "theme_color", "background_color", "icons"
            ]
            
            print("Manifest Content:")
            for field in required_fields:
                if field in manifest:
                    print(f"✅ {field}: {manifest[field]}")
                else:
                    print(f"❌ Missing: {field}")
            
            # Check icons
            if "icons" in manifest and len(manifest["icons"]) > 0:
                print(f"✅ Icons: {len(manifest['icons'])} icon(s) defined")
                for icon in manifest["icons"]:
                    print(f"   📱 {icon.get('sizes', 'unknown')} - {icon.get('src', 'no src')}")
            else:
                print("❌ No icons defined")
                
            return True
        else:
            print(f"❌ Failed to fetch manifest: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing manifest: {e}")
        return False

def test_service_worker():
    """Test service worker registration"""
    print("\n🔄 Testing Service Worker")
    print("=" * 50)
    
    try:
        response = requests.get("http://localhost:3000/sw.js", timeout=5)
        if response.status_code == 200:
            sw_content = response.text
            
            # Check for key service worker features
            features = {
                "install event": "addEventListener('install'",
                "activate event": "addEventListener('activate'",
                "fetch event": "addEventListener('fetch'",
                "caching": "caches.open",
                "background sync": "addEventListener('sync'",
                "push notifications": "addEventListener('push'"
            }
            
            print("Service Worker Features:")
            for feature, check in features.items():
                if check in sw_content:
                    print(f"✅ {feature}")
                else:
                    print(f"❌ {feature} - Not found")
            
            print(f"\n📊 Service Worker Size: {len(sw_content)} characters")
            return True
        else:
            print(f"❌ Service Worker not accessible: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing service worker: {e}")
        return False

def test_offline_page():
    """Test offline page"""
    print("\n📡 Testing Offline Page")
    print("=" * 50)
    
    try:
        response = requests.get("http://localhost:3000/offline.html", timeout=5)
        if response.status_code == 200:
            content = response.text
            
            # Check for key offline page elements
            elements = {
                "HTML structure": "<html",
                "Title": "<title",
                "Offline message": "offline",
                "Retry functionality": "checkConnection",
                "Styling": "<style",
                "JavaScript": "<script"
            }
            
            print("Offline Page Elements:")
            for element, check in elements.items():
                if check.lower() in content.lower():
                    print(f"✅ {element}")
                else:
                    print(f"❌ {element} - Not found")
            
            return True
        else:
            print(f"❌ Offline page not accessible: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing offline page: {e}")
        return False

def test_pwa_meta_tags():
    """Test PWA meta tags in main page"""
    print("\n🏷️ Testing PWA Meta Tags")
    print("=" * 50)
    
    try:
        response = requests.get("http://localhost:3000", timeout=5)
        if response.status_code == 200:
            content = response.text
            
            # Check for PWA meta tags
            meta_tags = {
                "Manifest link": 'rel="manifest"',
                "Theme color": 'name="theme-color"',
                "Apple mobile capable": 'name="apple-mobile-web-app-capable"',
                "Apple touch icon": 'rel="apple-touch-icon"',
                "Viewport": 'name="viewport"'
            }
            
            print("PWA Meta Tags:")
            for tag, check in meta_tags.items():
                if check in content:
                    print(f"✅ {tag}")
                else:
                    print(f"❌ {tag} - Not found")
            
            return True
        else:
            print(f"❌ Main page not accessible: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing meta tags: {e}")
        return False

def check_frontend_server():
    """Check if frontend server is running"""
    print("🚀 Checking Frontend Server")
    print("=" * 50)
    
    try:
        response = requests.get("http://localhost:3000", timeout=5)
        if response.status_code == 200:
            print("✅ Frontend server is running on http://localhost:3000")
            return True
        else:
            print(f"❌ Frontend server responded with status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Frontend server is not running")
        print("💡 Please start the frontend server with: cd frontend && npm start")
        return False
    except Exception as e:
        print(f"❌ Error checking server: {e}")
        return False

def generate_test_report(results):
    """Generate comprehensive test report"""
    print("\n📊 PWA Test Report")
    print("=" * 50)
    
    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if "✅" in str(result))
    
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    print("\nDetailed Results:")
    for test, result in results.items():
        print(f"  {test}: {result}")
    
    if passed_tests == total_tests:
        print("\n🎉 ALL PWA TESTS PASSED!")
        print("Your Progressive Web App is ready for testing!")
    else:
        print(f"\n⚠️ {total_tests - passed_tests} tests failed")
        print("Please check the issues above and retry")

def main():
    """Main testing function"""
    print("🧪 Smart Rice Mill ERP - PWA Features Testing")
    print("=" * 60)
    print("Testing Progressive Web App functionality...")
    print()
    
    # Check if server is running
    if not check_frontend_server():
        return
    
    # Run all tests
    results = {}
    
    # Test PWA files
    file_results = test_pwa_files()
    results.update(file_results)
    
    # Test manifest
    results["Manifest Content"] = "✅ Valid" if test_manifest_content() else "❌ Invalid"
    
    # Test service worker
    results["Service Worker"] = "✅ Valid" if test_service_worker() else "❌ Invalid"
    
    # Test offline page
    results["Offline Page"] = "✅ Valid" if test_offline_page() else "❌ Invalid"
    
    # Test meta tags
    results["PWA Meta Tags"] = "✅ Valid" if test_pwa_meta_tags() else "❌ Invalid"
    
    # Generate report
    generate_test_report(results)
    
    print("\n🔗 Next Steps:")
    print("1. Open Chrome/Edge and go to http://localhost:3000")
    print("2. Open DevTools (F12) → Application → Manifest")
    print("3. Check for install prompt in address bar")
    print("4. Test offline mode: DevTools → Network → Offline checkbox")
    print("5. Try installing the app on mobile device")

if __name__ == "__main__":
    main()
