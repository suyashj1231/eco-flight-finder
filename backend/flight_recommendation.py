from typing import List, Dict, Optional, Union
from datetime import datetime

from search_context import SearchContext, SortBy
from airport_utils import airport_db
from google_flight_emissions import get_emissions

class FlightRecommender:
    """Scores and ranks flights based on emissions, duration, and user preferences"""

    def __init__(self):
        pass

    def rank_flights(self, flights: Union[List, List[Dict]], context: SearchContext) -> List[Dict]:
        """
        Rank and filter flights based on search context and user profile
        
        Args:
            flights: List of flight dicts or composite roundtrip dicts {outbound, inbound}
            context: SearchContext with parameters and ranking mode
            
        Returns:
            List of ranked flight dicts with scores and explanations
        """
        # 1. Collect unique flight segments to verify
        unique_segments = {}
        for item in flights:
            if isinstance(item, dict) and "outbound" in item and "inbound" in item:
                unique_segments[id(item["outbound"])] = item["outbound"]
                unique_segments[id(item["inbound"])] = item["inbound"]
            else:
                unique_segments[id(item)] = item

        # 2. Build payload for Google API
        segment_list = list(unique_segments.values())
        payload_inputs = []
        id_to_index = {}

        for i, flight in enumerate(segment_list):
            try:
                # Extract clean data for API
                dep_iata = flight.get('departure', {}).get('iata')
                arr_iata = flight.get('arrival', {}).get('iata')
                carrier = flight.get('airline', {}).get('iata')
                f_num = flight.get('flight', {}).get('number')
                iso_date = flight.get('departure', {}).get('scheduled')
                
                # Check for validity
                if dep_iata and arr_iata and carrier and f_num and iso_date:
                    # Parse date components
                    dt = datetime.fromisoformat(iso_date.replace("Z", "+00:00"))
                    
                    payload_inputs.append({
                        "origin": dep_iata,
                        "destination": arr_iata,
                        "operatingCarrierCode": carrier,
                        "flightNumber": int(f_num) if str(f_num).isdigit() else 0,
                        "departureDate": {"year": dt.year, "month": dt.month, "day": dt.day}
                    })
                    # Map flight object ID to the index in the payload list
                    id_to_index[id(flight)] = len(payload_inputs) - 1
            except Exception as e:
                print(f"Skipping extraction for flight {i}: {e}")

        # 3. Batch Call to Google API (Chunked)
        emissions_cache = {} # id -> emissions_kg
        
        if payload_inputs:
            chunk_size = 50 # Google limit is 100 usually, playing safe
            all_emissions_results = []
            
            for i in range(0, len(payload_inputs), chunk_size):
                chunk = payload_inputs[i:i+chunk_size]
                try:
                    results = get_emissions(chunk)
                    if results:
                        all_emissions_results.extend(results)
                    else:
                        # If API fails, append Nones
                        all_emissions_results.extend([None] * len(chunk))
                except Exception as e:
                    print(f"Batch emissions error: {e}")
                    all_emissions_results.extend([None] * len(chunk))

            # 4. Map results back to flight IDs
            for flight_id, idx in id_to_index.items():
                if idx < len(all_emissions_results):
                    res = all_emissions_results[idx]
                    if res and "emissionsGramsPerPax" in res:
                        kg = res.get('emissionsGramsPerPax', {}).get('economy', 0) / 1000.0
                        emissions_cache[flight_id] = kg

        # 5. Score and Rank
        scored = []
        for flight in flights:
            score_result = self.calculate_flight_score(flight, context, emissions_cache)
            scored.append(score_result)

        # 6. Sort based on user preference
        def get_sort_key(item):
            if item.get("filtered_out"):
                return (1, float('inf'))
            
            flight = item.get("flight", {})
            sb = context.sort_by
            
            if sb == SortBy.DURATION:
                return (0, flight.get("duration_hours", 0))
            elif sb == SortBy.DEPARTURE_TIME:
                return (0, flight.get("departure", ""))
            elif sb == SortBy.EMISSIONS:
                return (0, flight.get("emissions_kg", 0))
            else:
                # Default to rank_score (can be balanced)
                return (0, item.get("rank_score", 0))

        ranked = sorted(scored, key=get_sort_key)

        return ranked

    def calculate_flight_score(self, flight: Union[Dict, List], context: SearchContext, emissions_cache: Dict = None) -> Dict:
        """
        Calculate emissions, duration, and ranking score for a flight or roundtrip composite
        
        Args:
            flight: Single flight dict or composite {outbound, inbound}
            context: SearchContext with filters
            emissions_cache: Dict mapping flight object ID to emissions in kg
            
        Returns:
            Dict with formatted flight, score, filters applied, and explanation
        """
        formatted = self._format_flight(flight, emissions_cache)

        # Apply filters
        filter_reason = None
        if context.max_emissions and formatted.get("emissions_kg") and formatted["emissions_kg"] > context.max_emissions:
            filter_reason = f"Emissions {formatted['emissions_kg']:.1f}kg exceeds limit {context.max_emissions}kg"

        if context.max_duration_hours and formatted.get("duration_hours") and formatted["duration_hours"] > context.max_duration_hours:
            filter_reason = f"Duration {formatted['duration_hours']:.1f}h exceeds limit {context.max_duration_hours}h"

        if filter_reason:
            return {
                "flight": formatted,
                "filtered_out": True,
                "filter_reason": filter_reason,
                "rank_score": float('inf'),
                "explanation": [filter_reason],
            }

        # Calculate normalized rank score
        rank_score, explanation = self._normalize_and_rank(formatted, context)

        return {
            "flight": formatted,
            "filtered_out": False,
            "filter_reason": None,
            "rank_score": rank_score,
            "explanation": explanation,
        }

    def _format_flight(self, flight: Union[Dict, List], emissions_cache: Dict = None) -> Dict:
        """
        Format flight data from API response or composite roundtrip
        
        Handles both single-leg and roundtrip composite structures
        """
        # Handle composite roundtrip: {outbound, inbound}
        if isinstance(flight, dict) and "outbound" in flight and "inbound" in flight:
            return self._format_composite_roundtrip(flight, emissions_cache)
        
        # Handle single flight
        return self._format_single_flight(flight, emissions_cache)

    def _format_composite_roundtrip(self, composite: Dict, emissions_cache: Dict = None) -> Dict:
        """Format a roundtrip composite with outbound and inbound flights"""
        outbound = composite.get("outbound", {})
        inbound = composite.get("inbound", {})

        out_fmt = self._format_single_flight(outbound, emissions_cache)
        in_fmt = self._format_single_flight(inbound, emissions_cache)

        # Sum emissions and duration
        total_emissions = (out_fmt.get("emissions_kg", 0) or 0) + (in_fmt.get("emissions_kg", 0) or 0)
        total_duration = (out_fmt.get("duration_hours", 0) or 0) + (in_fmt.get("duration_hours", 0) or 0)

        return {
            "flight_number": f"{out_fmt.get('flight_number', 'N/A')} + {in_fmt.get('flight_number', 'N/A')}",
            "airline": out_fmt.get("airline", "Unknown"),
            "aircraft": out_fmt.get("aircraft", "Unknown"),
            "distance_km": (out_fmt.get("distance_km", 0) or 0) + (in_fmt.get("distance_km", 0) or 0),
            "duration_hours": total_duration,
            "emissions_kg": total_emissions,
            "num_legs": 2,
            "outbound": out_fmt,
            "inbound": in_fmt,
        }

    def _format_single_flight(self, flight: Dict, emissions_cache: Dict = None) -> Dict:
        """Parse a single flight from AviationStack API response"""
        if not flight:
            return {}

        # Parse distance
        distance_km = 0
        # Helper to get nested or flat
        def get_val(obj, key, nested_key=None):
            if nested_key and key in obj and isinstance(obj[key], dict):
                return obj[key].get(nested_key)
            return obj.get(key)

        # Parse distance
        distance_km = 0
        if "distance" in flight and isinstance(flight["distance"], dict):
            distance_km = flight["distance"].get("km", 0) or 0
        elif "distance" in flight:
            distance_km = float(flight["distance"]) if flight["distance"] else 0

        # If API returns 0 distance, calculate it manually using airport coords
        if not distance_km:
            try:
                # Need dep_iata and arr_iata
                dep_iata = get_val(flight, "departure", "iata")
                arr_iata = get_val(flight, "arrival", "iata")
                
                if dep_iata and arr_iata:
                    dep_coords = airport_db.get_coordinates(dep_iata)
                    arr_coords = airport_db.get_coordinates(arr_iata)
                    
                    if dep_coords and arr_coords:
                        distance_km = airport_db.calculate_distance(
                            dep_coords[0], dep_coords[1],
                            arr_coords[0], arr_coords[1]
                        )
            except Exception as e:
                print(f"Error calculating distance manually: {e}")

        sched_dep = get_val(flight, "scheduled_departure") or get_val(flight, "departure", "scheduled")
        sched_arr = get_val(flight, "scheduled_arrival") or get_val(flight, "arrival", "scheduled")

        try:
            if sched_dep and sched_arr:
                # Handle timezones if present, else assume UTC if Z or isoformat
                # AviationStack sends: "2026-02-10T22:55:00+00:00"
                dep_time = datetime.fromisoformat(sched_dep.replace("Z", "+00:00"))
                arr_time = datetime.fromisoformat(sched_arr.replace("Z", "+00:00"))
                duration_hours = (arr_time - dep_time).total_seconds() / 3600
        except Exception as e:
            print(f"Error calculating duration: {e}")
            duration_hours = 0

        # Get aircraft and calculate emissions
        aircraft_obj = flight.get("aircraft") or {}
        aircraft_iata = aircraft_obj.get("iata", "UNK")
        
        # Retrieve from cache if available
        emissions_kg = 0
        if emissions_cache and id(flight) in emissions_cache:
            emissions_kg = emissions_cache.get(id(flight), 0)
        # Fallback Estimation if API returns 0 or failed
        if not emissions_kg and distance_km > 0:
            # Average avg CO2 per km per passenger for economy (approx 115g/km)
            # This is a rough industry average for short/medium haul
            AVERAGE_CO2_PER_KM = 0.115 
            emissions_kg = distance_km * AVERAGE_CO2_PER_KM
            # We could flag this as estimated if we wanted to show UI hint
            # flight['is_estimated'] = True 
        elif not emissions_kg:
             # Last resort if no distance either
             emissions_kg = 0
    

        flight_obj = flight.get("flight") or {}
        airline_obj = flight.get("airline") or {}

        return {
            "flight_number": flight_obj.get("iata", "N/A"),
            "airline": airline_obj.get("name", "Unknown"),
            "aircraft": aircraft_iata,
            "distance_km": distance_km,
            "duration_hours": duration_hours,
            "emissions_kg": emissions_kg,
            "departure": sched_dep,
            "arrival": sched_arr,
            "dep_iata": get_val(flight, "departure", "iata"),
            "arr_iata": get_val(flight, "arrival", "iata"),
        }

    def _normalize_and_rank(self, flight: Dict, context: SearchContext) -> tuple:
        """
        Normalize emissions and duration scores, then rank based on context
        
        Primary: 90% emissions (lower is better)
        Secondary: 10% duration (shorter is better)
        
        Returns: (rank_score, explanation_list)
        """
        explanations = []

        # Reference values for normalization
        ref_emissions = 500  # kg CO2 for 1000km flight
        ref_duration = 10    # hours

        emissions = flight.get("emissions_kg", 0) or 0
        duration = flight.get("duration_hours", 0) or 0

        # Normalize (0-1 scale, lower is better)
        norm_emissions = min(1.0, emissions / ref_emissions) if ref_emissions else 0
        norm_duration = min(1.0, duration / ref_duration) if ref_duration else 0

        # Default Rank score: 70% emissions, 30% duration
        # (A good balance for an eco-focused app until filters are added)
        rank_score = 0.7 * norm_emissions + 0.3 * norm_duration

        # Build explanation
        if emissions > 0:
            explanations.append(f"CO2: {emissions:.1f}kg")
        if duration > 0:
            explanations.append(f"Duration: {duration:.1f}h")
        if flight.get("distance_km"):
            explanations.append(f"Distance: {flight['distance_km']:.0f}km")

        return rank_score, explanations
