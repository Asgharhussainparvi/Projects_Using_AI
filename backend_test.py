#!/usr/bin/env python3
"""
Backend API Testing for Mood Tracker App
Tests all 5 backend endpoints with comprehensive scenarios
"""

import requests
import json
import csv
import io
from datetime import datetime
import uuid

# Get backend URL from frontend .env
BACKEND_URL = "https://054bbaf7-94dc-4624-8c0a-9bb7c673ec5a.preview.emergentagent.com/api"

# Valid mood emojis from backend
VALID_EMOJIS = ["😄", "😊", "🙂", "😐", "😞", "😢", "😡", "😰", "🤗", "😴"]
INVALID_EMOJI = "🤔"  # Not in the valid list

def test_mood_options_endpoint():
    """Test GET /api/moods/options endpoint"""
    print("\n=== Testing GET /api/moods/options ===")
    
    try:
        response = requests.get(f"{BACKEND_URL}/moods/options")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {data}")
            
            # Verify we get exactly 10 mood options
            if len(data) == 10:
                print("✅ Correct number of mood options (10)")
            else:
                print(f"❌ Expected 10 mood options, got {len(data)}")
                return False
                
            # Verify all expected emojis are present
            for emoji in VALID_EMOJIS:
                if emoji in data:
                    print(f"✅ Found emoji {emoji}: {data[emoji]}")
                else:
                    print(f"❌ Missing emoji {emoji}")
                    return False
                    
            return True
        else:
            print(f"❌ Failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_create_mood_entry():
    """Test POST /api/moods endpoint"""
    print("\n=== Testing POST /api/moods ===")
    
    # Test 1: Valid mood entry with notes
    print("\n--- Test 1: Valid mood with notes ---")
    mood_data = {
        "mood_emoji": "😄",
        "mood_name": "Very Happy",
        "notes": "Had a great day at work!"
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/moods", json=mood_data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Created mood entry: {data}")
            
            # Verify response structure
            required_fields = ["id", "mood_emoji", "mood_name", "notes", "timestamp"]
            for field in required_fields:
                if field in data:
                    print(f"✅ Field '{field}' present: {data[field]}")
                else:
                    print(f"❌ Missing field '{field}'")
                    return False, None
                    
            # Verify UUID format
            try:
                uuid.UUID(data["id"])
                print("✅ Valid UUID format for ID")
            except ValueError:
                print("❌ Invalid UUID format for ID")
                return False, None
                
            return True, data["id"]
        else:
            print(f"❌ Failed with status {response.status_code}: {response.text}")
            return False, None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False, None

def test_create_mood_without_notes():
    """Test POST /api/moods without notes"""
    print("\n--- Test 2: Valid mood without notes ---")
    mood_data = {
        "mood_emoji": "😊",
        "mood_name": "Happy"
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/moods", json=mood_data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Created mood entry: {data}")
            print("✅ Successfully created mood without notes")
            return True, data["id"]
        else:
            print(f"❌ Failed with status {response.status_code}: {response.text}")
            return False, None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False, None

def test_create_invalid_mood():
    """Test POST /api/moods with invalid emoji"""
    print("\n--- Test 3: Invalid mood emoji ---")
    mood_data = {
        "mood_emoji": INVALID_EMOJI,
        "mood_name": "Thinking",
        "notes": "This should fail"
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/moods", json=mood_data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 400:
            print("✅ Correctly rejected invalid emoji with 400 status")
            print(f"Error message: {response.text}")
            return True
        else:
            print(f"❌ Expected 400 status, got {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_get_mood_entries():
    """Test GET /api/moods endpoint"""
    print("\n=== Testing GET /api/moods ===")
    
    try:
        response = requests.get(f"{BACKEND_URL}/moods")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Retrieved {len(data)} mood entries")
            
            if len(data) > 0:
                # Check first entry structure
                entry = data[0]
                required_fields = ["id", "mood_emoji", "mood_name", "timestamp"]
                for field in required_fields:
                    if field in entry:
                        print(f"✅ Field '{field}' present in entry")
                    else:
                        print(f"❌ Missing field '{field}' in entry")
                        return False
                        
                # Verify sorting (newest first)
                if len(data) > 1:
                    first_time = datetime.fromisoformat(data[0]["timestamp"].replace('Z', '+00:00'))
                    second_time = datetime.fromisoformat(data[1]["timestamp"].replace('Z', '+00:00'))
                    if first_time >= second_time:
                        print("✅ Entries are sorted by timestamp (newest first)")
                    else:
                        print("❌ Entries are not properly sorted")
                        return False
                        
                print("✅ Successfully retrieved mood entries")
                return True, data
            else:
                print("✅ No mood entries found (empty database)")
                return True, []
        else:
            print(f"❌ Failed with status {response.status_code}")
            return False, []
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False, []

def test_delete_mood_entry(mood_id):
    """Test DELETE /api/moods/{mood_id} endpoint"""
    print(f"\n=== Testing DELETE /api/moods/{mood_id} ===")
    
    try:
        response = requests.delete(f"{BACKEND_URL}/moods/{mood_id}")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Delete response: {data}")
            print("✅ Successfully deleted mood entry")
            return True
        else:
            print(f"❌ Failed with status {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_delete_nonexistent_mood():
    """Test DELETE with non-existent mood ID"""
    print("\n--- Test: Delete non-existent mood ---")
    fake_id = str(uuid.uuid4())
    
    try:
        response = requests.delete(f"{BACKEND_URL}/moods/{fake_id}")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 404:
            print("✅ Correctly returned 404 for non-existent mood")
            return True
        else:
            print(f"❌ Expected 404 status, got {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_csv_export():
    """Test GET /api/moods/export endpoint"""
    print("\n=== Testing GET /api/moods/export ===")
    
    try:
        response = requests.get(f"{BACKEND_URL}/moods/export")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            # Check content type
            content_type = response.headers.get('content-type', '')
            if 'text/csv' in content_type:
                print("✅ Correct content type (text/csv)")
            else:
                print(f"❌ Expected text/csv, got {content_type}")
                return False
                
            # Check content disposition header
            disposition = response.headers.get('content-disposition', '')
            if 'attachment' in disposition and 'mood_history.csv' in disposition:
                print("✅ Correct content disposition header")
            else:
                print(f"❌ Incorrect content disposition: {disposition}")
                return False
                
            # Parse CSV content
            csv_content = response.text
            print(f"CSV content length: {len(csv_content)} characters")
            
            # Parse CSV to verify structure
            csv_reader = csv.reader(io.StringIO(csv_content))
            rows = list(csv_reader)
            
            if len(rows) > 0:
                header = rows[0]
                expected_header = ['Date', 'Time', 'Mood', 'Emoji', 'Notes']
                if header == expected_header:
                    print("✅ Correct CSV header format")
                    print(f"Header: {header}")
                else:
                    print(f"❌ Incorrect header. Expected: {expected_header}, Got: {header}")
                    return False
                    
                # Show sample data if available
                if len(rows) > 1:
                    print(f"Sample data row: {rows[1]}")
                    print("✅ CSV export working correctly")
                else:
                    print("✅ CSV export working (no data entries)")
            else:
                print("❌ Empty CSV response")
                return False
                
            return True
        else:
            print(f"❌ Failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def create_test_data():
    """Create multiple mood entries for comprehensive testing"""
    print("\n=== Creating Test Data ===")
    
    test_moods = [
        {"mood_emoji": "😄", "mood_name": "Very Happy", "notes": "Great morning workout!"},
        {"mood_emoji": "😊", "mood_name": "Happy", "notes": "Nice lunch with friends"},
        {"mood_emoji": "😐", "mood_name": "Neutral", "notes": "Regular afternoon"},
        {"mood_emoji": "😞", "mood_name": "Sad", "notes": "Missed the bus"},
        {"mood_emoji": "😴", "mood_name": "Tired", "notes": "Long day at work"}
    ]
    
    created_ids = []
    for mood in test_moods:
        try:
            response = requests.post(f"{BACKEND_URL}/moods", json=mood)
            if response.status_code == 200:
                data = response.json()
                created_ids.append(data["id"])
                print(f"✅ Created mood: {mood['mood_emoji']} {mood['mood_name']}")
            else:
                print(f"❌ Failed to create mood: {mood['mood_emoji']}")
        except Exception as e:
            print(f"❌ Error creating mood {mood['mood_emoji']}: {e}")
    
    return created_ids

def run_all_tests():
    """Run all backend API tests"""
    print("🚀 Starting Mood Tracker Backend API Tests")
    print("=" * 50)
    
    test_results = {}
    
    # Test 1: Mood options endpoint
    test_results["mood_options"] = test_mood_options_endpoint()
    
    # Test 2: Create mood entries
    success, mood_id1 = test_create_mood_entry()
    test_results["create_mood_with_notes"] = success
    
    success, mood_id2 = test_create_mood_without_notes()
    test_results["create_mood_without_notes"] = success
    
    # Test 3: Invalid mood creation
    test_results["invalid_mood_creation"] = test_create_invalid_mood()
    
    # Test 4: Create additional test data
    created_ids = create_test_data()
    all_ids = [id for id in [mood_id1, mood_id2] + created_ids if id]
    
    # Test 5: Get mood entries
    success, entries = test_get_mood_entries()
    test_results["get_mood_entries"] = success
    
    # Test 6: CSV export
    test_results["csv_export"] = test_csv_export()
    
    # Test 7: Delete mood entries
    if all_ids:
        # Test deleting existing mood
        test_results["delete_existing_mood"] = test_delete_mood_entry(all_ids[0])
        
        # Clean up remaining test data
        print("\n=== Cleaning up test data ===")
        for mood_id in all_ids[1:]:
            try:
                requests.delete(f"{BACKEND_URL}/moods/{mood_id}")
                print(f"✅ Cleaned up mood {mood_id}")
            except:
                print(f"❌ Failed to clean up mood {mood_id}")
    
    # Test 8: Delete non-existent mood
    test_results["delete_nonexistent_mood"] = test_delete_nonexistent_mood()
    
    # Print summary
    print("\n" + "=" * 50)
    print("🏁 TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All backend API tests PASSED!")
        return True
    else:
        print("⚠️  Some backend API tests FAILED!")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)