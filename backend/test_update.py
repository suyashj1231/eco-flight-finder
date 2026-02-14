import requests

BASE_URL = "http://127.0.0.1:8000"

def test_update_profile():
    # 1. Login to get token
    login_data = {
        "username": "debug_user_99",
        "password": "password123"
    }
    
    print("Logging in...")
    try:
        resp = requests.post(f"{BASE_URL}/token", data=login_data)
        if resp.status_code != 200:
            print(f"Login failed: {resp.status_code} - {resp.text}")
            return
            
        token = resp.json()["access_token"]
        print("Login success, token received.")
        
        # 2. Update profile
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        update_data = {
            "first_name": "UpdatedName",
            "age": 30
        }
        
        print(f"Updating profile with: {update_data}")
        resp = requests.put(f"{BASE_URL}/users/me", json=update_data, headers=headers)
        
        if resp.status_code == 200:
            print("Update success:", resp.json())
        else:
            print(f"Update failed: {resp.status_code} - {resp.text}")

    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_update_profile()
