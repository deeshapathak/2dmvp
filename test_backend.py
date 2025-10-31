#!/usr/bin/env python3
"""
Test script for Rhinovate AI Backend
"""

import requests
import json
import sys
import os

def test_health_endpoint():
    """Test the health endpoint"""
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data['message']}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend. Make sure it's running on http://localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_analyze_endpoint():
    """Test the analyze endpoint with a sample image"""
    # Create a simple test image (1x1 pixel)
    from PIL import Image
    import io
    
    # Create a small test image
    img = Image.new('RGB', (100, 100), color='red')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    
    try:
        files = {'file': ('test.jpg', img_bytes, 'image/jpeg')}
        response = requests.post("http://localhost:8000/analyze", files=files)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Analysis test passed")
            print(f"   - Facial Harmony Score: {data.get('facial_harmony_score', 'N/A')}")
            print(f"   - Recommendations: {len(data.get('recommendations', []))}")
            return True
        else:
            print(f"❌ Analysis test failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Analysis test error: {e}")
        return False

def main():
    print("🧪 Testing Rhinovate AI Backend...")
    print("=" * 50)
    
    # Test health endpoint
    health_ok = test_health_endpoint()
    
    if health_ok:
        # Test analyze endpoint
        analyze_ok = test_analyze_endpoint()
        
        if analyze_ok:
            print("\n🎉 All tests passed! Backend is working correctly.")
            sys.exit(0)
        else:
            print("\n❌ Analysis test failed.")
            sys.exit(1)
    else:
        print("\n❌ Health check failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()
