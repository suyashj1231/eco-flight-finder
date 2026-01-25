from flight_api import search_flights

dep = 'SFO'
arr = 'JFK'
flights = search_flights(dep, arr)

count = 0
found = 0
if flights:
    for f in flights:
        count += 1
        ac = f.get('aircraft')
        if ac:
            found += 1
            print(f"Found aircraft data: {ac}")

print(f"Total flights: {count}")
print(f"Flights with aircraft data: {found}")
