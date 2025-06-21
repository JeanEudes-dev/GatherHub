#!/usr/bin/env python3
"""
Comprehensive demo script for Event Management API.
"""
import requests
import json
from datetime import datetime, timedelta

# API base URL
BASE_URL = "http://127.0.0.1:8000/api/v1"

def demo_api():
    """Demonstrate all Event Management API features."""
    print("🎉 Event Management API Demo")
    print("=" * 60)
    
    # Step 1: Register a new user
    print("\n1. 👤 Registering a new user...")
    user_data = {
        "email": f"demo{datetime.now().microsecond}@example.com",
        "username": f"demo{datetime.now().microsecond}",
        "name": "Demo User",
        "password": "demopass123",
        "password_confirm": "demopass123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register/", json=user_data)
    if response.status_code == 201:
        print("✅ User registered successfully!")
        user_email = user_data["email"]
        
        # Step 2: Login and get JWT token
        print("\n2. 🔐 Logging in...")
        login_data = {
            "email": user_email,
            "password": "demopass123"
        }
        response = requests.post(f"{BASE_URL}/auth/token/", json=login_data)
        
        if response.status_code == 200:
            token = response.json()["access"]
            headers = {"Authorization": f"Bearer {token}"}
            print("✅ Login successful!")
            
            # Step 3: Create an event with timeslots
            print("\n3. 📅 Creating an event with timeslots...")
            future_dt1 = (datetime.now() + timedelta(days=7)).isoformat()
            future_dt2 = (datetime.now() + timedelta(days=8)).isoformat()
            
            event_data = {
                "title": "Team Building Workshop",
                "description": """# Team Building Workshop

This is an **exciting** workshop for team building activities.

## What we'll do:
- *Icebreaker* activities
- Problem-solving challenges  
- Fun group exercises

**Note**: Please bring comfortable clothes!""",
                "timeslots": [
                    {"datetime": future_dt1},
                    {"datetime": future_dt2}
                ]
            }
            
            response = requests.post(f"{BASE_URL}/events/", json=event_data, headers=headers)
            if response.status_code == 201:
                event = response.json()
                event_slug = event["slug"]
                print(f"✅ Event created: {event['title']}")
                print(f"   Slug: {event_slug}")
                
                # Step 4: Get event details
                print("\n4. 📖 Retrieving event details...")
                response = requests.get(f"{BASE_URL}/events/{event_slug}/")
                if response.status_code == 200:
                    event_detail = response.json()
                    print("✅ Event details retrieved!")
                    print(f"   Title: {event_detail['title']}")
                    print(f"   Status: {event_detail['status']}")
                    print(f"   Timeslots: {len(event_detail['timeslots'])}")
                    print(f"   Creator: {event_detail['created_by']['name']}")
                    print(f"   Markdown HTML preview: {event_detail['description_html'][:100]}...")
                    
                    # Step 5: Add more timeslots
                    print("\n5. ⏰ Adding more timeslots...")
                    future_dt3 = (datetime.now() + timedelta(days=9)).isoformat()
                    timeslot_data = {"datetime": future_dt3}
                    
                    response = requests.post(f"{BASE_URL}/events/{event_slug}/timeslots/", 
                                           json=timeslot_data, headers=headers)
                    if response.status_code == 201:
                        print("✅ Additional timeslot added!")
                    
                    # Step 6: Update event details
                    print("\n6. ✏️ Updating event...")
                    update_data = {
                        "title": "Advanced Team Building Workshop",
                        "description": event_detail["description"] + "\n\n**UPDATE**: This workshop is now advanced level!"
                    }
                    response = requests.patch(f"{BASE_URL}/events/{event_slug}/", 
                                            json=update_data, headers=headers)
                    if response.status_code == 200:
                        updated_event = response.json()
                        print(f"✅ Event updated! New title: {updated_event['title']}")
                        new_slug = updated_event.get('slug', event_slug)
                        event_slug = new_slug  # Use new slug if it changed
                    
                    # Step 7: List all events
                    print("\n7. 📋 Listing all events...")
                    response = requests.get(f"{BASE_URL}/events/")
                    if response.status_code == 200:
                        events_list = response.json()
                        print(f"✅ Found {events_list['count']} events")
                        for event_item in events_list['results']:
                            print(f"   - {event_item['title']} ({event_item['timeslot_count']} timeslots)")
                    
                    # Step 8: Search events
                    print("\n8. 🔍 Searching events...")
                    response = requests.get(f"{BASE_URL}/events/?search=team")
                    if response.status_code == 200:
                        search_results = response.json()
                        print(f"✅ Search results: {search_results['count']} events found")
                    
                    # Step 9: Get timeslots for the event
                    print("\n9. ⏱️ Getting event timeslots...")
                    response = requests.get(f"{BASE_URL}/events/{event_slug}/timeslots/")
                    if response.status_code == 200:
                        timeslots = response.json()
                        print(f"✅ Found {len(timeslots['results'])} timeslots")
                        for ts in timeslots['results']:
                            dt = datetime.fromisoformat(ts['datetime'].replace('Z', '+00:00'))
                            print(f"   - {dt.strftime('%Y-%m-%d %H:%M')} (votes: {ts['vote_count']})")
                    
                    # Step 10: Lock the event
                    print("\n10. 🔒 Locking the event...")
                    response = requests.post(f"{BASE_URL}/events/{event_slug}/lock/", 
                                           headers=headers)
                    if response.status_code == 200:
                        locked_event = response.json()
                        print(f"✅ Event locked! Status: {locked_event['status']}")
                        
                        # Step 11: Try to update locked event (should fail)
                        print("\n11. ❌ Trying to update locked event...")
                        response = requests.patch(f"{BASE_URL}/events/{event_slug}/", 
                                                json={"title": "Should Not Work"}, headers=headers)
                        if response.status_code == 403:
                            print("✅ Correctly prevented updating locked event!")
                        else:
                            print(f"❌ Unexpected response: {response.status_code}")
                    
                    # Step 12: Create second event to demonstrate permissions
                    print("\n12. 👥 Creating second event...")
                    event2_data = {
                        "title": "Another Event",
                        "description": "This is another event for testing"
                    }
                    response = requests.post(f"{BASE_URL}/events/", json=event2_data, headers=headers)
                    if response.status_code == 201:
                        print("✅ Second event created!")
                    
                    # Final: Summary
                    print("\n" + "=" * 60)
                    print("📊 DEMO SUMMARY")
                    print("=" * 60)
                    
                    response = requests.get(f"{BASE_URL}/events/")
                    if response.status_code == 200:
                        final_events = response.json()
                        print(f"Total events created: {final_events['count']}")
                        
                        for event_item in final_events['results']:
                            print(f"\n📅 {event_item['title']}")
                            print(f"   Slug: {event_item['slug']}")
                            print(f"   Status: {event_item['status']}")
                            print(f"   Timeslots: {event_item['timeslot_count']}")
                            print(f"   Creator: {event_item['created_by']['name']}")
                    
                    print(f"\n🎯 Demo completed successfully!")
                    print(f"🌐 View the API docs at: http://127.0.0.1:8000/api/docs/")
                    
                else:
                    print(f"❌ Failed to get event details: {response.status_code}")
            else:
                print(f"❌ Failed to create event: {response.status_code}")
                print(f"Response: {response.text}")
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"Response: {response.text}")
    else:
        print(f"❌ Registration failed: {response.status_code}")
        print(f"Response: {response.text}")

if __name__ == "__main__":
    demo_api()
