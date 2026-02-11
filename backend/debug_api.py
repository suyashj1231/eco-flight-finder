import os
import requests
import json
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

API_KEY = os.getenv("API_KEY")
BASE_URL = "https://api.aviationstack.com/v1/flights"

def debug_search():
    if not API_KEY:
        print("Error: API_KEY not found.")
        return

    params = {
        'access_key': API_KEY,
        'dep_iata': 'SNA',
        'arr_iata': 'SFO',
        'limit': 10
    }
    
    print(f"Searching flights with key: {API_KEY[:5]}...")
    try:
        response = requests.get(BASE_URL, params=params)
        data = response.json()
        
        with open('raw_api_response.json', 'w') as f:
            json.dump(data, f, indent=2)
            
        print("Saved raw response to raw_api_response.json")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_search()
