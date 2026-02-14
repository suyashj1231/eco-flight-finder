from typing import List, Dict, Optional, Union
from datetime import datetime
from user_model import UserProfile
from search_context import SearchContext, SortBy
from fuel_utils import fuel_db
from airport_utils import airport_db
from google_flight_emissions import get_emissions

class FlightRecommender:
    """Scores and ranks flights based on emissions, duration, and user preferences"""

    def __init__(self, user: UserProfile):
        self.user = user

    def rank_flights(self, flights: Union[List, List[Dict]], context: SearchContext) -> List[Dict]:
        """
        Rank and filter flights based on search context and user profile
        
        Args:
            flights: List of flight dicts or composite roundtrip dicts {outbound, inbound}
            context: SearchContext with parameters and ranking mode
            
        Returns:
            List of ranked flight dicts with scores and explanations
        """
        scored = []

        for flight in flights:
            score_result = self.calculate_flight_score(flight, context)
            scored.append(score_result)

        # Sort by rank_score (lower is better)
        ranked = sorted(scored, key=lambda x: x["rank_score"] if not x.get("filtered_out") else float('inf'))

        return ranked

    def calculate_flight_score(self, flight: Union[Dict, List], context: SearchContext) -> Dict:
        """
        Calculate emissions, duration, and ranking score for a flight or roundtrip composite
        
        Args:
            flight: Single flight dict or composite {outbound, inbound}
            context: SearchContext with filters
            
        Returns:
            Dict with formatted flight, score, filters applied, and explanation
        """
        formatted = self._format_flight(flight)

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

    def _format_flight(self, flight: Union[Dict, List]) -> Dict:
        """
        Format flight data from API response or composite roundtrip
        
        Handles both single-leg and roundtrip composite structures
        """
        # Handle composite roundtrip: {outbound, inbound}
        if isinstance(flight, dict) and "outbound" in flight and "inbound" in flight:
            return self._format_composite_roundtrip(flight)
        
        # Handle single flight
        return self._format_single_flight(flight)

    def _format_composite_roundtrip(self, composite: Dict) -> Dict:
        """Format a roundtrip composite with outbound and inbound flights"""
        outbound = composite.get("outbound", {})
        inbound = composite.get("inbound", {})

        out_fmt = self._format_single_flight(outbound)
        in_fmt = self._format_single_flight(inbound)

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

    def _format_single_flight(self, flight: Dict) -> Dict:
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
        emissions_kg = 0
        # this comment section was the original part calculating emissions before
        # the google API
        """
        if aircraft_iata and aircraft_iata != "UNK" and distance_km > 0:
            aircraft_data = fuel_db.get_aircraft_data(aircraft_iata)
            if aircraft_data:
                fuel_kg_per_km = aircraft_data.get("fuel_kg_km", 0)
                max_pax = aircraft_data.get("max_pax", 0)

                co2_per_kg_fuel = 3.16  # kg CO2 per kg jet fuel
                
                if fuel_kg_per_km and max_pax:
                    emissions_kg = (fuel_kg_per_km * co2_per_kg_fuel / max_pax) * distance_km
        """
        iso = flight["departure"]["scheduled"]
        dt = datetime.fromisoformat(iso)
        departure_date = { "year": dt.year, "month": dt.month, "day": dt.day }
        my_flight = {
            "origin": f"{flight['departure']['iata']}",
            "destination": f"{flight['arrival']['iata']}",
            "operatingCarrierCode": f"{flight['airline']['iata']}",
            "flightNumber": f"{flight['flight']['number']}",
            "departureDate": departure_date
        }
        emission_api_return = get_emissions(my_flight)[0]
        # gets the emissions for economy
        if emission_api_return and "emissionsGramsPerPax" in emission_api_return:
            emissions_kg = emission_api_return.get('emissionsGramsPerPax', {}).get('economy', 'N/A')/1000
        else:
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

        # Rank score: weighted combination
        rank_score = 0.9 * norm_emissions + 0.1 * norm_duration

        # Build explanation
        if emissions > 0:
            explanations.append(f"CO2: {emissions:.1f}kg")
        if duration > 0:
            explanations.append(f"Duration: {duration:.1f}h")
        if flight.get("distance_km"):
            explanations.append(f"Distance: {flight['distance_km']:.0f}km")

        return rank_score, explanations
