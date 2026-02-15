import requests
import json

def test_registration():
    url = "http://127.0.0.1:8000/register"
    payload = {
        "username": "testuser_debug_" + str(json.dumps(True)), # Just a dummy unique-ish name
        "first_name": "Test",
        "last_name": "User",
        "age": 25,
        "password": "a" * 73
    }
    
    # Try a few times to get a unique username
    import time
    timestamp = int(time.time())
    payload["username"] = f"user_{timestamp}"
    
    print(f"Testing registration with username: {payload['username']}")
    try:
        response = requests.post(url, json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.text}")
    except Exception as e:
        print(f"Error connecting to backend: {e}")

if __name__ == "__main__":
    test_registration()
