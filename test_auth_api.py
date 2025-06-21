#!/usr/bin/env python3
"""
Test script for GatherHub Authentication API
"""
import requests
import json
import os

BASE_URL = "http://127.0.0.1:8001/api/v1/auth"

def test_user_registration():
    """Test user registration endpoint"""
    print("=== Testing User Registration ===")
    
    registration_data = {
        "email": "test@example.com",
        "name": "Test User",
        "password": "testpass123",
        "password_confirm": "testpass123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/register/", json=registration_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 201:
            data = response.json()
            return data.get('tokens', {}).get('access')
        else:
            print("Registration failed!")
            return None
            
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_login():
    """Test JWT token login endpoint"""
    print("\n=== Testing User Login ===")
    
    login_data = {
        "email": "test@example.com",
        "password": "testpass123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/token/", json=login_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            data = response.json()
            return data.get('access')
        else:
            print("Login failed!")
            return None
            
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_get_profile(access_token):
    """Test getting user profile"""
    print("\n=== Testing Get User Profile ===")
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(f"{BASE_URL}/profile/", headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
    except Exception as e:
        print(f"Error: {e}")

def test_update_profile(access_token):
    """Test updating user profile"""
    print("\n=== Testing Update User Profile ===")
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    update_data = {
        "name": "Updated Test User"
    }
    
    try:
        response = requests.put(f"{BASE_URL}/profile/", json=update_data, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
    except Exception as e:
        print(f"Error: {e}")

def test_change_password(access_token):
    """Test changing user password"""
    print("\n=== Testing Change Password ===")
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    password_data = {
        "current_password": "testpass123",
        "new_password": "newpass123",
        "new_password_confirm": "newpass123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/change-password/", json=password_data, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
    except Exception as e:
        print(f"Error: {e}")

def test_validation_errors():
    """Test validation errors"""
    print("\n=== Testing Validation Errors ===")
    
    # Test duplicate email registration
    print("\n--- Testing Duplicate Email Registration ---")
    registration_data = {
        "email": "test@example.com",  # Same email as before
        "name": "Another User",
        "password": "testpass123",
        "password_confirm": "testpass123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/register/", json=registration_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test weak password
    print("\n--- Testing Weak Password ---")
    registration_data = {
        "email": "test2@example.com",
        "name": "Test User 2",
        "password": "123",  # Weak password
        "password_confirm": "123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/register/", json=registration_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test password mismatch
    print("\n--- Testing Password Mismatch ---")
    registration_data = {
        "email": "test3@example.com",
        "name": "Test User 3",
        "password": "testpass123",
        "password_confirm": "differentpass123"  # Different confirmation
    }
    
    try:
        response = requests.post(f"{BASE_URL}/register/", json=registration_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")

def main():
    """Run all tests"""
    print("🚀 Starting GatherHub Authentication API Tests")
    print("=" * 50)
    
    # Test 1: Registration
    access_token = test_user_registration()
    
    if not access_token:
        # If registration failed, try login instead
        access_token = test_login()
    
    if access_token:
        # Test 2: Get Profile
        test_get_profile(access_token)
        
        # Test 3: Update Profile
        test_update_profile(access_token)
        
        # Test 4: Change Password
        test_change_password(access_token)
    
    # Test 5: Validation Errors
    test_validation_errors()
    
    print("\n" + "=" * 50)
    print("✅ Tests completed!")

if __name__ == "__main__":
    main()
