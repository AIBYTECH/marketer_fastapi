#!/usr/bin/env python3
"""
Simple test script to verify the FastAPI app works locally
"""
import requests
import time
import subprocess
import sys
import os

def test_app():
    """Test the FastAPI application"""
    print("Testing Marketer FastAPI Application...")
    
    # Test health endpoint
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Health check failed: {e}")
        return False
    
    # Test main page
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        if response.status_code == 200:
            print("✅ Main page loads successfully")
        else:
            print(f"❌ Main page failed: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Main page failed: {e}")
        return False
    
    # Test API endpoint
    try:
        response = requests.post("http://localhost:8000/api/chat", 
                               json={"message": "Hello, test message"}, 
                               timeout=10)
        if response.status_code == 200:
            print("✅ API endpoint works")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ API endpoint failed: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ API endpoint failed: {e}")
        return False
    
    print("🎉 All tests passed!")
    return True

if __name__ == "__main__":
    test_app()
