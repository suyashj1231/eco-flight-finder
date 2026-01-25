import os
import requests
from dotenv import load_dotenv, find_dotenv

# Load environment variables
load_dotenv(find_dotenv())

API_KEY = os.getenv("API_KEY")
BASE_URL = "https://api.aviationstack.com/v1/flights"

def search_flights(dep_iata, arr_iata, date=None):
    """
    Search for flights between two airports on a specific date.
    
    Args:
        dep_iata (str): Departure IATA code (e.g., 'SFO')
        arr_iata (str): Arrival IATA code (e.g., 'JFK')
        date (str, optional): Date in YYYY-MM-DD format.
        
    Returns:
        list: A list of flight dictionaries or None if error.
    """
    if not API_KEY:
        print("Error: API_KEY not found in environment variables.")
        return None

    params = {
        'access_key': API_KEY,
        'dep_iata': dep_iata,
        'arr_iata': arr_iata,
        'limit': 100  # Max limit for free plan
    }
    
    # AviationStack 'flights' endpoint filters by active/recent. 
    # For historical dates, we might need 'flight_date' if the plan supports it.
    # Note: The free plan is very limited on historical data.
    # We will try passing 'flight_date' param which works for some tiers/endpoints.
    if date:
        # Validates date format could go here
        # AviationStack uses 'flight_date' param for filtering specific days (usually historical or very near future)
        # Note: Future schedules might require a different strategy if 'flights' doesn't return them.
        # But for 'active' flights on a specific day, this is the param.
        # However, for pure future schedules, we might need /flightsFuture, but let's stick to /flights for now
        # params['flight_date'] = date
        print("Note: Date filtering is restricted on the Free Plan. Searching for active/recent flights instead.")

    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()
        
        if 'error' in data:
            print(f"API Error: {data['error']}")
            return None
            
        return data.get('data', [])
        
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None

def format_flight_data(flight):
    """Helper to extract relevant info from a flight object"""
    departure = flight.get('departure') or {}
    arrival = flight.get('arrival') or {}
    airline = flight.get('airline') or {}
    flight_info = flight.get('flight') or {}
    aircraft = flight.get('aircraft') or {}
    
    return {
        'date': flight.get('flight_date'),
        'status': flight.get('flight_status'),
        'airline': airline.get('name'),
        'flight_number': f"{airline.get('iata', '')}{flight_info.get('number', '')}",
        'dep_airport': departure.get('iata'),
        'dep_time': departure.get('scheduled'),
        'arr_airport': arrival.get('iata'),
        'arr_time': arrival.get('scheduled'),
        'aircraft': aircraft.get('iata') # Valuable for CO2
    }
