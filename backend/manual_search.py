import os
import sys
from datetime import datetime

# Add the current directory to sys.path to allow imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv, find_dotenv
from flight_api import search_flights
from flight_recommendation import FlightRecommender
from search_context import SearchContext


# Load environment variables
load_dotenv(find_dotenv())

def get_input(prompt, default=None):
    """Helper to get user input with an optional default."""
    if default:
        user_input = input(f"{prompt} [{default}]: ").strip()
        return user_input if user_input else default
    return input(f"{prompt}: ").strip()

def format_duration(hours):
    """Format duration hours into h m string."""
    h = int(hours)
    m = int((hours - h) * 60)
    return f"{h}h {m}m"

def main():
    print("\n--- Manual Eco Flight Finder ---\n")

    # 1. Collect User Input
    if len(sys.argv) > 1:
        dep_iata = sys.argv[1].upper()
        arr_iata = sys.argv[2].upper()
        date_str = sys.argv[3] if len(sys.argv) > 3 else datetime.now().strftime("%Y-%m-%d")
        passengers = int(sys.argv[4]) if len(sys.argv) > 4 else 1
    else:
        dep_iata = get_input("Departure Airport IATA (e.g., SFO)", "SFO").upper()
        arr_iata = get_input("Arrival Airport IATA (e.g., JFK)", "JFK").upper()
        today = datetime.now().strftime("%Y-%m-%d")
        date_str = get_input("Date (YYYY-MM-DD)", today)
        while True:
            try:
                passengers = int(get_input("Number of Passengers", "1"))
                break
            except ValueError:
                print("Please enter a valid integer.")

    print(f"\nSearching for flights from {dep_iata} to {arr_iata} on {date_str}...")

    # 2. Search Flights
    try:
        flights = search_flights(dep_iata, arr_iata, date_str)
    except Exception as e:
        print(f"Error calling Flight API: {e}")
        return

    if not flights:
        print("No flights found. (Note: Free API tier has limited historical/future coverage)")
        return

    print(f"Found {len(flights)} flights. Processing data...\n")

    # 3. Process and Rank

    context = SearchContext(
        departure_iata=dep_iata, arrival_iata=arr_iata,
        departure_date=date_str, eco_mode=True, seat_class="economy"
    )

    recommender = FlightRecommender()
    ranked_results = recommender.rank_flights(flights, context)

    # 4. Display Cleaned Results
    # Wider format to show Aircraft column
    print(f"{'Flight':<8} | {'Airline':<20} | {'Aircraft':<8} | {'Departs':<6} | {'Arrives':<6} | {'Dur':<6} | {'CO2/pax':<10} | {'Total':<10}")
    print("-" * 105)

    for res in ranked_results:
        flight = res.get("flight", {})
        
        flight_num = flight.get("flight_number", "N/A")
        airline = flight.get("airline", "Unknown")[:20]
        # Get aircraft code (might be UNK if missing)
        aircraft_code = flight.get("aircraft", "UNK")
        
        dep_time = flight.get("departure")
        arr_time = flight.get("arrival")
        # Format HH:MM
        dep_str = datetime.fromisoformat(dep_time).strftime("%H:%M") if dep_time else "N/A"
        arr_str = datetime.fromisoformat(arr_time).strftime("%H:%M") if arr_time else "N/A"
        
        duration = flight.get("duration_hours", 0)
        dur_str = format_duration(duration)
        
        # Retrieve emissions first, then check for None
        emissions = flight.get("emissions_kg", 0)
        
        if emissions is None:
            emissions = 0.0
        else:
            emissions = float(emissions)
            
        total_emissions = emissions * passengers
        
        # Format strings to avoid NoneType format errors
        flight_num_fmt = str(flight_num)
        airline_fmt = str(airline)
        ac_fmt = str(aircraft_code)

        try:
            print(f"{flight_num_fmt:<8} | {airline_fmt:<20} | {ac_fmt:<8} | {dep_str:<6} | {arr_str:<6} | {dur_str:<6} | {emissions:6.1f}kg | {total_emissions:6.1f}kg")
        except Exception as e:
            print(f"Error printing row: {e} | Flight: {flight_num}")

    print(f"\n{'-'*105}")
    print(f"Shown {len(ranked_results)} flight options.")
    if any(r.get("flight", {}).get("emissions_kg", 0) == 0 for r in ranked_results):
        print("\n* Note: 0.0kg CO2 indicates missing distance/aircraft data.")

if __name__ == "__main__":
    main()
