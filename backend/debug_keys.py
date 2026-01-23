import os
import requests
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
api_key = os.getenv("API_KEY")

params = {
  'access_key': api_key
}

api_result = requests.get('https://api.aviationstack.com/v1/flights', params)
resp = api_result.json()
print("Keys in response:", resp.keys())
