#!/usr/bin/env python3
"""
Simple API test script for Event Management API.
"""
import requests
import json
from datetime import datetime, timedelta

# API base URL
BASE_URL = "http://127.0.0.1:8000/api/v1"

def test_api():
    """Test the Event Management API."""
    print("🚀 Testing Event Management API")
    print("=" * 50)
    
    # Test 1: List events (should be empty)
    print("\n1. Testing list events...")
    response = requests.get(f"{BASE_URL}/events/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Test 2: Get API schema
    print("\n2. Testing API schema...")
    response = requests.get(f"{BASE_URL}/../schema/")
    print(f"Status: {response.status_code}")
    print(f"Schema available: {response.status_code == 200}")
    
    # Test 3: Try to create event without authentication (should fail)
    print("\n3. Testing create event without auth...")
    event_data = {
        "title": "Test Event",
        "description": "A test event with **markdown**"
    }
    response = requests.post(f"{BASE_URL}/events/", json=event_data)
    print(f"Status: {response.status_code}")
    print(f"Expected 401 Unauthorized: {response.status_code == 401}")
    
    # Test 4: Test authentication endpoints
    print("\n4. Testing authentication...")
    
    # First, try to register a user (if endpoint exists)
    user_data = {
        "email": "testapi3@example.com",
        "username": "testapi3",
        "name": "Test API User 3",
        "password": "testpass123",
        "password_confirm": "testpass123"
    }
    
    # Try registration
    response = requests.post(f"{BASE_URL}/auth/register/", json=user_data)
    print(f"Registration status: {response.status_code}")
    
    if response.status_code == 201:
        print("✅ User registered successfully")
        
        # Try login with JWT token endpoint
        login_data = {
            "email": "testapi3@example.com",
            "password": "testpass123"
        }
        response = requests.post(f"{BASE_URL}/auth/token/", json=login_data)
        print(f"Login status: {response.status_code}")
        
        if response.status_code == 200:
            token = response.json().get('access')
            print("✅ Login successful")
            
            # Test 5: Create event with authentication
            print("\n5. Testing create event with auth...")
            headers = {"Authorization": f"Bearer {token}"}
            
            future_datetime = (datetime.now() + timedelta(days=1)).isoformat()
            event_data = {
                "title": "Authenticated Test Event",
                "description": "A test event created with **authentication**",
                "timeslots": [
                    {"datetime": future_datetime}
                ]
            }
            
            response = requests.post(f"{BASE_URL}/events/", json=event_data, headers=headers)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 201:
                event = response.json()
                print("✅ Event created successfully")
                print(f"Event slug: {event.get('slug')}")
                
                # Test 6: Get event details
                print("\n6. Testing get event details...")
                response = requests.get(f"{BASE_URL}/events/{event['slug']}/")
                print(f"Status: {response.status_code}")
                
                if response.status_code == 200:
                    event_detail = response.json()
                    print("✅ Event details retrieved")
                    print(f"Title: {event_detail.get('title')}")
                    print(f"Markdown HTML: {event_detail.get('description_html', '')[:50]}...")
                    print(f"Timeslots: {len(event_detail.get('timeslots', []))}")
                    
                    # Test 7: Update event
                    print("\n7. Testing update event...")
                    update_data = {
                        "title": "Updated Test Event",
                        "description": "Updated description with *new* content"
                    }
                    response = requests.patch(f"{BASE_URL}/events/{event['slug']}/", json=update_data, headers=headers)
                    print(f"Status: {response.status_code}")
                    
                    if response.status_code == 200:
                        print("✅ Event updated successfully")
                        
                        # Test 8: Lock event
                        print("\n8. Testing lock event...")
                        response = requests.post(f"{BASE_URL}/events/{event['slug']}/lock/", headers=headers)
                        print(f"Status: {response.status_code}")
                        
                        if response.status_code == 200:
                            print("✅ Event locked successfully")
                            
                            # Test 9: Try to update locked event (should fail)
                            print("\n9. Testing update locked event...")
                            response = requests.patch(f"{BASE_URL}/events/{event['slug']}/", json=update_data, headers=headers)
                            print(f"Status: {response.status_code}")
                            print(f"Expected 403 Forbidden: {response.status_code == 403}")
            
            # Test 10: List events again (should have our created event)
            print("\n10. Testing list events again...")
            response = requests.get(f"{BASE_URL}/events/")
            if response.status_code == 200:
                events = response.json()
                print(f"Total events: {events.get('count', 0)}")
                
        else:
            print("❌ Login failed")
            print(f"Response: {response.text}")
    else:
        print("❌ Registration failed")
        print(f"Response: {response.text}")
    
    print("\n" + "=" * 50)
    print("🎉 API Test Complete!")

if __name__ == "__main__":
    test_api()
