#!/usr/bin/env python3
"""
Extended test script for GatherHub Authentication API with avatar upload
"""
import requests
import json
import os
from io import BytesIO
from PIL import Image

BASE_URL = "http://127.0.0.1:8001/api/v1/auth"

def create_test_image():
    """Create a test JPEG image for avatar upload"""
    img = Image.new('RGB', (100, 100), color='red')
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format='JPEG')
    img_byte_arr.seek(0)
    return img_byte_arr

def test_fresh_user_registration():
    """Test registration with a new user"""
    print("=== Testing Fresh User Registration ===")
    
    registration_data = {
        "email": "newuser@example.com",
        "name": "New Test User",
        "password": "securepass123",
        "password_confirm": "securepass123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/register/", json=registration_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 201:
            data = response.json()
            return data.get('tokens', {}).get('access')
        return None
            
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_avatar_upload(access_token):
    """Test avatar upload functionality"""
    print("\n=== Testing Avatar Upload ===")
    
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    # Create test image
    img_data = create_test_image()
    
    files = {
        'avatar': ('test_avatar.jpg', img_data, 'image/jpeg')
    }
    
    data = {
        'name': 'User with Avatar'
    }
    
    try:
        response = requests.put(f"{BASE_URL}/profile/", headers=headers, files=files, data=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
    except Exception as e:
        print(f"Error: {e}")

def test_avatar_delete(access_token):
    """Test avatar deletion"""
    print("\n=== Testing Avatar Deletion ===")
    
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    try:
        response = requests.delete(f"{BASE_URL}/profile/avatar/", headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
    except Exception as e:
        print(f"Error: {e}")

def test_token_verification(access_token):
    """Test JWT token verification"""
    print("\n=== Testing Token Verification ===")
    
    verification_data = {
        "token": access_token
    }
    
    try:
        response = requests.post(f"{BASE_URL}/token/verify/", json=verification_data)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("✅ Token is valid")
        else:
            print(f"❌ Token verification failed: {response.json()}")
        
    except Exception as e:
        print(f"Error: {e}")

def test_unauthorized_access():
    """Test accessing protected endpoints without authentication"""
    print("\n=== Testing Unauthorized Access ===")
    
    # Try to access profile without token
    try:
        response = requests.get(f"{BASE_URL}/profile/")
        print(f"Profile Access Status Code: {response.status_code}")
        print(f"Profile Access Response: {json.dumps(response.json(), indent=2)}")
        
    except Exception as e:
        print(f"Error: {e}")
    
    # Try to change password without token
    try:
        response = requests.post(f"{BASE_URL}/change-password/", json={
            "current_password": "test",
            "new_password": "newtest",
            "new_password_confirm": "newtest"
        })
        print(f"Password Change Status Code: {response.status_code}")
        print(f"Password Change Response: {json.dumps(response.json(), indent=2)}")
        
    except Exception as e:
        print(f"Error: {e}")

def test_email_validation():
    """Test email validation edge cases"""
    print("\n=== Testing Email Validation ===")
    
    invalid_emails = [
        "notanemail",
        "@invalid.com", 
        "user@",
        "user..user@domain.com",
        "user@domain",
        ""
    ]
    
    for email in invalid_emails:
        print(f"\n--- Testing invalid email: '{email}' ---")
        registration_data = {
            "email": email,
            "name": "Test User",
            "password": "testpass123",
            "password_confirm": "testpass123"
        }
        
        try:
            response = requests.post(f"{BASE_URL}/register/", json=registration_data)
            print(f"Status Code: {response.status_code}")
            if response.status_code != 201:
                errors = response.json()
                if 'email' in errors:
                    print(f"Email Error: {errors['email']}")
                else:
                    print(f"Response: {json.dumps(errors, indent=2)}")
            
        except Exception as e:
            print(f"Error: {e}")

def main():
    """Run extended tests"""
    print("🚀 Starting Extended GatherHub Authentication API Tests")
    print("=" * 60)
    
    # Test 1: Fresh user registration
    access_token = test_fresh_user_registration()
    
    if access_token:
        # Test 2: Token verification
        test_token_verification(access_token)
        
        # Test 3: Avatar upload
        test_avatar_upload(access_token)
        
        # Test 4: Profile after avatar upload
        print("\n=== Profile After Avatar Upload ===")
        headers = {"Authorization": f"Bearer {access_token}"}
        try:
            response = requests.get(f"{BASE_URL}/profile/", headers=headers)
            print(f"Status Code: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        except Exception as e:
            print(f"Error: {e}")
        
        # Test 5: Avatar deletion
        test_avatar_delete(access_token)
    
    # Test 6: Unauthorized access
    test_unauthorized_access()
    
    # Test 7: Email validation
    test_email_validation()
    
    print("\n" + "=" * 60)
    print("✅ Extended tests completed!")

if __name__ == "__main__":
    main()
