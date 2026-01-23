import os
import requests
from dotenv import load_dotenv, find_dotenv

# Load environment variables from .env file
load_dotenv(find_dotenv())

# Get API key from environment variable
api_key = os.getenv("API_KEY")

params = {
  'access_key': api_key
}

api_result = requests.get('https://api.aviationstack.com/v1/flights', params)

api_response = api_result.json()

print(f"API Status Code: {api_result.status_code}")
print(f"Full API Response: {api_response}")

# for flight in api_response['results']:
#     if (flight['live']['is_ground'] is False):
#         print(u'%s flight %s from %s (%s) to %s (%s) is in the air.' % (
#             flight['airline']['name'],
#             flight['flight']['iata'],
#             flight['departure']['airport'],
#             flight['departure']['iata'],
#             flight['arrival']['airport'],
#             flight['arrival']['iata']))

# print(api_response)