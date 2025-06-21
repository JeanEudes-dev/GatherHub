#!/usr/bin/env python3
"""
Test JWT token refresh functionality
"""
import requests
import json
import time

BASE_URL = "http://127.0.0.1:8001/api/v1/auth"

def test_token_refresh():
    """Test JWT token refresh functionality"""
    print("=== Testing JWT Token Refresh ===")
    
    # First, register a user to get tokens
    registration_data = {
        "email": "refresh_test@example.com",
        "name": "Refresh Test User",
        "password": "testpass123",
        "password_confirm": "testpass123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/register/", json=registration_data)
        if response.status_code == 201:
            tokens = response.json()['tokens']
            refresh_token = tokens['refresh']
            access_token = tokens['access']
            
            print(f"✅ Registration successful")
            print(f"Access Token: {access_token[:50]}...")
            print(f"Refresh Token: {refresh_token[:50]}...")
            
            # Test using the access token
            print("\n--- Testing with initial access token ---")
            headers = {"Authorization": f"Bearer {access_token}"}
            profile_response = requests.get(f"{BASE_URL}/profile/", headers=headers)
            print(f"Profile access status: {profile_response.status_code}")
            
            # Test refreshing the token
            print("\n--- Testing token refresh ---")
            refresh_data = {"refresh": refresh_token}
            refresh_response = requests.post(f"{BASE_URL}/token/refresh/", json=refresh_data)
            
            if refresh_response.status_code == 200:
                new_tokens = refresh_response.json()
                new_access_token = new_tokens['access']
                
                print(f"✅ Token refresh successful")
                print(f"New Access Token: {new_access_token[:50]}...")
                
                # Test using the new access token
                print("\n--- Testing with new access token ---")
                new_headers = {"Authorization": f"Bearer {new_access_token}"}
                new_profile_response = requests.get(f"{BASE_URL}/profile/", headers=new_headers)
                print(f"Profile access with new token status: {new_profile_response.status_code}")
                
                if new_profile_response.status_code == 200:
                    print("✅ New access token works correctly")
                    user_data = new_profile_response.json()
                    print(f"User: {user_data['name']} ({user_data['email']})")
                
            else:
                print(f"❌ Token refresh failed: {refresh_response.status_code}")
                print(f"Response: {refresh_response.json()}")
                
        else:
            print(f"❌ Registration failed: {response.status_code}")
            if response.status_code == 400:
                print("User might already exist, trying login instead...")
                
                # Try login
                login_data = {
                    "email": "refresh_test@example.com",
                    "password": "testpass123"
                }
                
                login_response = requests.post(f"{BASE_URL}/token/", json=login_data)
                if login_response.status_code == 200:
                    tokens = login_response.json()
                    refresh_token = tokens['refresh']
                    print(f"✅ Login successful, testing refresh...")
                    
                    refresh_data = {"refresh": refresh_token}
                    refresh_response = requests.post(f"{BASE_URL}/token/refresh/", json=refresh_data)
                    print(f"Refresh status: {refresh_response.status_code}")
                    
                    if refresh_response.status_code == 200:
                        print("✅ Token refresh working with existing user")
                    else:
                        print(f"❌ Token refresh failed: {refresh_response.json()}")
    
    except Exception as e:
        print(f"Error: {e}")

def test_invalid_tokens():
    """Test behavior with invalid tokens"""
    print("\n=== Testing Invalid Tokens ===")
    
    # Test with invalid access token
    print("--- Testing invalid access token ---")
    invalid_headers = {"Authorization": "Bearer invalid_token_here"}
    try:
        response = requests.get(f"{BASE_URL}/profile/", headers=invalid_headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test with invalid refresh token
    print("\n--- Testing invalid refresh token ---")
    try:
        refresh_data = {"refresh": "invalid_refresh_token"}
        response = requests.post(f"{BASE_URL}/token/refresh/", json=refresh_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")

def main():
    """Run token tests"""
    print("🔐 Testing JWT Token Functionality")
    print("=" * 50)
    
    test_token_refresh()
    test_invalid_tokens()
    
    print("\n" + "=" * 50)
    print("✅ Token tests completed!")

if __name__ == "__main__":
    main()
