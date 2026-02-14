import requests

BASE_URL = "http://127.0.0.1:8000"

def test_register_login():
    username = "debug_user_99"
    password = "password123"
    
    # diverse data payload
    reg_data = {
        "username": username,
        "password": password,
        "first_name": "Debug",
        "last_name": "User",
        "age": 25
    }
    
    print(f"Registering user: {username}")
    try:
        resp = requests.post(f"{BASE_URL}/register", json=reg_data)
        if resp.status_code == 200:
            print("Registration success:", resp.json())
        else:
            print(f"Registration failed: {resp.status_code} - {resp.text}")
            # If 400 user exists, try to login anyway
    except Exception as e:
        print(f"Registration exception: {e}")

    print(" attempting login...")
    login_data = {
        "username": username,
        "password": password
    }
    
    try:
        # requests.post sends data as form-urlencoded by default for data=dict
        # OAuth2PasswordRequestForm expects form-urlencoded or multipart/form-data
        # Let's try form-urlencoded first which is standard
        resp = requests.post(f"{BASE_URL}/token", data=login_data)
        
        if resp.status_code == 200:
            print("Login success:", resp.json())
        else:
            print(f"Login failed: {resp.status_code} - {resp.text}")
            
    except Exception as e:
        print(f"Login exception: {e}")

if __name__ == "__main__":
    test_register_login()
