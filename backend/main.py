import sys
from flight_api import search_flights, format_flight_data

def print_flights(flights, label="Flights"):
    """Pretty print a list of flights"""
    print(f"\n--- {label} ---")
    if not flights:
        print("No flights found.")
        return

    for flight in flights:
        f = format_flight_data(flight)
        print(f"[{f['date']}] {f['airline']} {f['flight_number']} | {f['dep_airport']} ({f['dep_time']}) -> {f['arr_airport']} ({f['arr_time']}) | Status: {f['status']}")

def get_input(prompt):
    """Helper to get user input consistently"""
    try:
        return input(prompt).strip()
    except EOFError:
        return ""

def main():
    print("Welcome to Eco Flight Finder CLI")
    print("--------------------------------")
    
    while True:
        print("\nNew Search (Ctrl+C to exit):")
        dep = get_input("Departure Airport (IATA, e.g. SFO): ").upper()
        if not dep: break
        
        arr = get_input("Arrival Airport (IATA, e.g. JFK): ").upper()
        if not arr: break
        
        date = get_input("Date (YYYY-MM-DD): ")
        if not date: break
        
        round_trip = get_input("Round Trip? (y/n): ").lower()
        
        # Outbound Search
        print(f"\nSearching for flights from {dep} to {arr} on {date}...")
        outbound = search_flights(dep, arr, date)
        print_flights(outbound, "Outbound Flights")
        
        # Inbound Search
        if round_trip == 'y':
            return_date = get_input("Return Date (YYYY-MM-DD): ")
            if return_date:
                print(f"\nSearching for return flights from {arr} to {dep} on {return_date}...")
                inbound = search_flights(arr, dep, return_date)
                print_flights(inbound, "Return Flights")
        
        cont = get_input("\nSearch again? (y/n): ").lower()
        if cont != 'y':
            break

    print("Goodbye!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)