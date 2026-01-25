import sys
from flight_api import search_flights, format_flight_data
from fuel_utils import fuel_db

CO2_PER_KG_FUEL = 3.16

def print_flights(flights, label="Flights"):
    """Pretty print a list of flights"""
    print(f"\n--- {label} ---")
    if not flights:
        print("No flights found.")
        return

    for i, flight in enumerate(flights):
        if i == 0: print(f"DEBUG RAW AIRCRAFT: {flight.get('aircraft')}")
        f = format_flight_data(flight)
        
        # CO2 Calculation
        fuel_info = fuel_db.get_aircraft_data(f['aircraft'])
        emissions_str = "Emissions: N/A"
        
        if fuel_info:
            fuel_kg_km = fuel_info['fuel_kg_km']
            max_pax = fuel_info['max_pax']
            
            # Total CO2 per km for the whole plane
            co2_kg_km = fuel_kg_km * CO2_PER_KG_FUEL
            
            # CO2 per pax per km (assuming full flight)
            co2_per_pax_km = co2_kg_km / max_pax if max_pax else 0
            
            emissions_str = (f"Est. CO2: {co2_kg_km:.2f} kg/km (Total) | "
                             f"{co2_per_pax_km:.3f} kg/km/pax | "
                             f"Plane: {fuel_info['name']} (Max Pax: {max_pax})")
        
        print(f"[{f['date']}] {f['airline']} {f['flight_number']} ({f['aircraft']}) | "
              f"{f['dep_airport']} ({f['dep_time']}) -> {f['arr_airport']} ({f['arr_time']}) | "
              f"Status: {f['status']}\n\t{emissions_str}")

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