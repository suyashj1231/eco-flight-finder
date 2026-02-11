import math
import requests
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

API_KEY = os.getenv("API_KEY")
BASE_URL = "http://api.aviationstack.com/v1/airports"

class AirportUtils:
    def __init__(self):
        self.cache = {}

    def get_coordinates(self, iata_code):
        """
        Get (lat, lon) for an airport IATA code from AviationStack API.
        Returns a tuple (lat, lon) or None.
        """
        if not iata_code:
            return None
        
        iata = iata_code.upper()
        if iata in self.cache:
            return self.cache[iata]

        params = {
            'access_key': API_KEY,
            'iata_code': iata
        }
        
        try:
            response = requests.get(BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()
            
            if 'data' in data and len(data['data']) > 0:
                airport = data['data'][0]
                # Sometimes lat/lon are strings "37.618972"
                lat = float(airport['latitude'])
                lon = float(airport['longitude'])
                self.cache[iata] = (lat, lon)
                return lat, lon
            
        except Exception as e:
            print(f"Error fetching airport data for {iata}: {e}")
            
        return None

    def calculate_distance(self, lat1, lon1, lat2, lon2):
        """
        Calculate Great Circle Distance between two points in km.
        """
        R = 6371.0  # Earth radius in km

        d_lat = math.radians(lat2 - lat1)
        d_lon = math.radians(lon2 - lon1)
        
        a = (math.sin(d_lat / 2) * math.sin(d_lat / 2) +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(d_lon / 2) * math.sin(d_lon / 2))
        
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        distance = R * c
        return distance

airport_db = AirportUtils()
