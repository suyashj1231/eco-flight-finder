import os
import sys

# Add backend dir to path so we can import airport_utils
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

from airport_utils import airport_db

def test_sfo():
    print("Testing SFO lookup...")
    coords = airport_db.get_coordinates("SFO")
    if coords:
        print(f"Success! SFO coords: {coords}")
        return True
    else:
        print("Failed to get SFO coords.")
        return False

def test_sna():
    # John Wayne Airport
    print("\nTesting SNA lookup...")
    coords = airport_db.get_coordinates("SNA")
    if coords:
        print(f"Success! SNA coords: {coords}")
        return True
    else:
        print("Failed to get SNA coords.")
        return False

if __name__ == "__main__":
    s1 = test_sfo()
    s2 = test_sna()
    
    if s1 and s2:
        print("\nCalculate distance SFO -> SNA:")
        dist = airport_db.calculate_distance(37.6, -122.4, 33.6, -117.8)
        print(f"Approx distance: {dist:.2f} km")
