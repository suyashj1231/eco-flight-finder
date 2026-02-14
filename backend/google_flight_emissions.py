import requests

def get_emissions(flights):
    api_key = "AIzaSyC_4JUezL_yx94H_cqyx74mBL7L4BHSunU"
    url = f"https://travelimpactmodel.googleapis.com/v1/flights:computeFlightEmissions?key={api_key}"
    
    payload = {"flights": flights}
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        return response.json().get('flightEmissions', [])
    else:
        print(f"Error: {response.text}")
        return None
"""
def get_emissions(flights):
    api_key = "AIzaSyC_4JUezL_yx94H_cqyx74mBL7L4BHSunU"
    url = f"https://travelimpactmodel.googleapis.com/v1/flights:computeFlightEmissions?key={api_key}"
    
    clean_flights = []
    for f in flights:
        try:
            y, m, d = map(int, f['flight_date'].split('-'))
            
            clean_flights.append({
                "origin": f['departure']['iata'],
                "destination": f['arrival']['iata'],
                "operatingCarrierCode": f['airline']['iata'],
                "flightNumber": int(f['flight']['number']),
                "departureDate": {"year": y, "month": m, "day": d}
            })
        except (KeyError, TypeError, ValueError):
            continue
    
    payload = {"flights": clean_flights}
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        return response.json().get('flightEmissions', [])
    else:
        print(f"Error: {response.text}")
        return []
"""
if __name__ == "__main__":
    my_flights = [
    {
        "origin": "LHR",
        "destination": "JFK",
        "operatingCarrierCode": "BA",
        "flightNumber": 115,
        "departureDate": {"year": 2026, "month": 2, "day": 14}
    },
    {
        "origin": "SFO",
        "destination": "NRT",
        "operatingCarrierCode": "UA",
        "flightNumber": 837,
        "departureDate": {"year": 2026, "month": 2, "day": 16}
    },
    {
        "origin": "LAX",
        "destination": "SYD",
        "operatingCarrierCode": "QF",
        "flightNumber": 12,
        "departureDate": {"year": 2026, "month": 2, "day": 18}
    },
    {
        "origin": "DXB",
        "destination": "CDG",
        "operatingCarrierCode": "EK",
        "flightNumber": 73,
        "departureDate": {"year": 2026, "month": 2, "day": 20}
    },
    {
        "origin": "SIN",
        "destination": "LHR",
        "operatingCarrierCode": "SQ",
        "flightNumber": 308,
        "departureDate": {"year": 2026, "month": 2, "day": 22}
    },
    {
        "origin": "JFK",
        "destination": "FRA",
        "operatingCarrierCode": "LH",
        "flightNumber": 401,
        "departureDate": {"year": 2026, "month": 2, "day": 24}
    },
    {
        "origin": "AMS",
        "destination": "ATL",
        "operatingCarrierCode": "KL",
        "flightNumber": 641,
        "departureDate": {"year": 2026, "month": 2, "day": 26}
    }
    ]

    emissions_results = get_emissions(my_flights)

    if emissions_results:
        for flight in emissions_results:
            economy_co2 = flight.get('emissionsGramsPerPax', {}).get('economy', 'N/A')
            print(f"Flight: {flight['flight']['operatingCarrierCode']}{flight['flight']['flightNumber']}")
            print(f"Emissions (Economy): {economy_co2} grams CO2\n")
            # debugging
            #print(f"Full Response for this flight: {flight}")