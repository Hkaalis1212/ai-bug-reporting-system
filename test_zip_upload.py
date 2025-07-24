#!/usr/bin/env python3
"""
Test script for zip file upload functionality
Demonstrates various ways to upload zip files to the Flask app
"""

import requests
import json
import os
import zipfile
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5000"
UPLOAD_ENDPOINT = f"{BASE_URL}/upload"

def create_test_zip():
    """Create a small test zip file for demonstration"""
    zip_filename = "test_upload.zip"
    
    # Create some test files
    test_files = {
        "readme.txt": "This is a test README file\nCreated for zip upload demonstration",
        "config.py": "# Test configuration file\nDEBUG = True\nAPP_NAME = 'Zip Upload Test'",
        "data.json": json.dumps({"name": "test", "version": "1.0", "files": 3}, indent=2)
    }
    
    with zipfile.ZipFile(zip_filename, 'w') as zip_file:
        for filename, content in test_files.items():
            zip_file.writestr(filename, content)
    
    print(f"✅ Created test zip file: {zip_filename}")
    return zip_filename

def test_web_upload(zip_filename):
    """Test uploading via web form (POST request)"""
    print(f"\n🔄 Testing web upload with {zip_filename}...")
    
    try:
        with open(zip_filename, 'rb') as f:
            files = {'file': (zip_filename, f, 'application/zip')}
            response = requests.post(UPLOAD_ENDPOINT, files=files)
        
        if response.status_code == 200:
            try:
                result = response.json()
                print("✅ Upload successful!")
                print(f"   Filename: {result.get('filename', 'N/A')}")
                print(f"   Files extracted: {len(result.get('extracted_files', []))}")
                print(f"   Extract path: {result.get('extract_path', 'N/A')}")
                return True
            except json.JSONDecodeError:
                print("✅ Upload successful (HTML response)")
                return True
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to Flask app. Make sure it's running on localhost:5000")
        return False
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        return False

def test_curl_command(zip_filename):
    """Generate curl command for testing"""
    print(f"\n📋 Equivalent curl command:")
    print(f"curl -X POST -F \"file=@{zip_filename}\" {UPLOAD_ENDPOINT}")

def test_get_upload_page():
    """Test getting the upload page"""
    print(f"\n🔄 Testing upload page access...")
    
    try:
        response = requests.get(UPLOAD_ENDPOINT)
        if response.status_code == 200 and "Upload Zip File" in response.text:
            print("✅ Upload page accessible")
            return True
        else:
            print(f"❌ Upload page error: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to Flask app")
        return False

def main():
    """Main test function"""
    print("🚀 Zip Upload Test Script")
    print("=" * 40)
    
    # Test 1: Check if upload page is accessible
    page_ok = test_get_upload_page()
    
    # Test 2: Create a test zip file
    zip_filename = create_test_zip()
    
    # Test 3: Test web upload
    if page_ok:
        upload_ok = test_web_upload(zip_filename)
    else:
        upload_ok = False
    
    # Test 4: Show curl command
    test_curl_command(zip_filename)
    
    # Cleanup
    if os.path.exists(zip_filename):
        os.remove(zip_filename)
        print(f"\n🧹 Cleaned up test file: {zip_filename}")
    
    # Summary
    print("\n" + "=" * 40)
    print("📊 Test Summary:")
    print(f"   Upload page: {'✅ OK' if page_ok else '❌ Failed'}")
    print(f"   File upload: {'✅ OK' if upload_ok else '❌ Failed'}")
    
    if page_ok and upload_ok:
        print("\n🎉 All tests passed! Zip upload functionality is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Check that the Flask app is running.")

if __name__ == "__main__":
    main()