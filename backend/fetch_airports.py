import requests
import json
import os

url = "https://raw.githubusercontent.com/algolia/datasets/master/airports/airports.json"
output_file = "airports.json"

def download_airports():
    print(f"Downloading airports from {url}...")
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        # Filter for only necessary fields to save space/time
        # The dataset has: name, city, country, iata_code, _geoloc, links_count, objectID
        print(f"Downloaded {len(data)} airports. Filtering...")
        
        filtered = []
        for airport in data:
            if not airport.get('iata_code'):
                continue
                
            filtered.append({
                "name": airport.get('name'),
                "city": airport.get('city'),
                "country": airport.get('country'),
                "iata": airport.get('iata_code'),
                "lat": airport.get('_geoloc', {}).get('lat'),
                "lon": airport.get('_geoloc', {}).get('lng')
            })
            
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(filtered, f)
            
        print(f"Saved {len(filtered)} airports to {output_file}")
        
    except Exception as e:
        print(f"Failed to download airports: {e}")

if __name__ == "__main__":
    download_airports()
