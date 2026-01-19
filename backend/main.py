import json
import os
import math
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="Eco Flight Finder API")

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For dev only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load Data
def load_json(filename):
    filepath = os.path.join(os.path.dirname(__file__), 'data', filename)
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: {filename} not found at {filepath}")
        return []

AIRPORTS = load_json('airports.json')
AIRCRAFT_EMISSIONS = load_json('aircraft_emissions.json')

# Key Helpers
def get_airport_coords(iata: str):
    iata = iata.upper()
    for airport in AIRPORTS:
        if airport['iata'] == iata:
            return {'lat': airport['lat'], 'lon': airport['lon']}
    return None

def haversine_distance_nm(lat1, lon1, lat2, lon2):
    R = 3440.065 # Radius of earth in NM
    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)
    a = math.sin(dLat/2) * math.sin(dLat/2) + \
        math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * \
        math.sin(dLon/2) * math.sin(dLon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

def get_emission_factor(aircraft_iata: Optional[str]) -> float:
    if not aircraft_iata:
        return 20.0 # Default fallback
    
    # Try exact match
    if aircraft_iata in AIRCRAFT_EMISSIONS:
        return AIRCRAFT_EMISSIONS[aircraft_iata]
    
    # Try partial match (e.g. A320 for A320-200)
    for key, val in AIRCRAFT_EMISSIONS.items():
        if key in aircraft_iata:
            return val
            
    return 20.0 # Default if unknown

def fetch_flights_mock(origin: str, destination: str, date: str):
    return [
        {
            "flight_date": date or "2023-10-25",
            "flight_status": "scheduled",
            "departure": {"airport": "Origin Airport", "iata": origin},
            "arrival": {"airport": "Dest Airport", "iata": destination},
            "airline": {"name": "British Airways", "iata": "BA"},
            "flight": {"number": "BA117", "iata": "BA117"},
            "aircraft": {"iata": "B777"}
        },
        {
            "flight_date": date or "2023-10-25",
            "flight_status": "scheduled",
            "departure": {"airport": "Origin Airport", "iata": origin},
            "arrival": {"airport": "Dest Airport", "iata": destination},
            "airline": {"name": "Virgin Atlantic", "iata": "VS"},
            "flight": {"number": "VS003", "iata": "VS003"},
            "aircraft": {"iata": "A350"}
        },
         {
            "flight_date": date or "2023-10-25",
            "flight_status": "scheduled",
            "departure": {"airport": "Origin Airport", "iata": origin},
            "arrival": {"airport": "Dest Airport", "iata": destination},
            "airline": {"name": "Eco Airways", "iata": "EA"},
            "flight": {"number": "EA999", "iata": "EA999"},
            "aircraft": {"iata": "A320"}
        }
    ]

def fetch_flights_api(origin: str, destination: str, date: Optional[str]):
    api_key = os.getenv("AVIATIONSTACK_API_KEY")
    if not api_key:
        print("No API Key, using mock data")
        return fetch_flights_mock(origin, destination, date)

    url = "http://api.aviationstack.com/v1/flights"
    params = {
        "access_key": api_key,
        "dep_iata": origin,
        "arr_iata": destination
    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        if "data" in data:
            return data["data"]
        return []
    except Exception as e:
        print(f"API Error: {e}")
        return []

@app.get("/")
def read_root():
    return {"message": "Eco Flight Finder API is running"}

@app.get("/api/search")
def search_flights(from_iata: str, to_iata: str, date: Optional[str] = None):
    # 1. Get Coordinates
    origin_coords = get_airport_coords(from_iata)
    dest_coords = get_airport_coords(to_iata)
    
    distance_nm = 0
    if origin_coords and dest_coords:
        distance_nm = haversine_distance_nm(
            origin_coords['lat'], origin_coords['lon'], 
            dest_coords['lat'], dest_coords['lon']
        )
        
    # 2. Fetch Flights
    flights = fetch_flights_api(from_iata, to_iata, date)
    
    # 3. Process Emissions
    results = []
    for flight in flights:
        aircraft_type = flight.get('aircraft', {}).get('iata')
        emission_factor = get_emission_factor(aircraft_type)
        total_emissions = distance_nm * emission_factor
        
        flight_data = {
            **flight,
            "eco": {
                "distanceNM": round(distance_nm),
                "co2EmissionKg": round(total_emissions),
                "aircraftModel": aircraft_type or "Unknown",
                "emissionFactorPerNM": emission_factor
            }
        }
        results.append(flight_data)
        
    # 4. Sort by Emissions
    results.sort(key=lambda x: x["eco"]["co2EmissionKg"])
    
    return {
        "route": {
            "origin": from_iata,
            "destination": to_iata,
            "distanceNM": round(distance_nm)
        },
        "results": results
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
