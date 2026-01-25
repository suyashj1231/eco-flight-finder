import pandas as pd
import re

DATA_FILE = "data/Fuel Calculation 50 Aircrafts_final.xlsx"
SHEET_NAME = "Hurtecant"

class FuelUtils:
    def __init__(self):
        self.data = pd.DataFrame()
        self.load_data()
        
    def load_data(self):
        try:
            # Header is at row 3 (0-indexed -> 3 means row 4 in Excel?) 
            # In Step 264 output, header=3 worked to give 'Aircraft Type'.
            self.data = pd.read_excel(DATA_FILE, sheet_name=SHEET_NAME, header=3)
            # Rename columns to be easier to access
            self.data.rename(columns={
                'Aircraft Type': 'aircraft_type',
                'Maximum Number of Pax Single Class (-)': 'max_pax',
                'Fuel Consumption (kg/km)': 'fuel_kg_km'
            }, inplace=True)
            
            # Clean up nan rows
            self.data.dropna(subset=['aircraft_type'], inplace=True)
            
            # Create normalized column for matching
            self.data['normalized_name'] = self.data['aircraft_type'].astype(str).str.lower().str.replace(r'[^a-z0-9]', '', regex=True)
            
        except Exception as e:
            print(f"Error loading fuel data: {e}")

    def get_aircraft_data(self, iata_code):
        """
        Attempts to find fuel data for a given IATA code (e.g. 'A320', 'B738').
        Returns dict or None.
        """
        if not iata_code:
            return None
            
        code = iata_code.lower().strip()
        
        # 1. Direct match might be hard because Excel has full names ("Airbus A320").
        # API has codes ("A320", "B738").
        
        # Heuristic 1: If code starts with 'a' (Airbus) or 'b' (Boeing), try to match the number part.
        # e.g. 'A320' -> '320'. 'B738' -> '737' (usually).
        
        search_term = code
        
        # Common IATA to Model mappings (Simple version)
        if code.startswith('b73'): search_term = '737'
        elif code.startswith('b74'): search_term = '747'
        elif code.startswith('b77'): search_term = '777'
        elif code.startswith('b78'): search_term = '787'
        elif code == 'a20n': search_term = 'a320neo'
        elif code == 'a21n': search_term = 'a321neo'
        
        # Try to find 'search_term' inside the normalized names in DB
        # e.g. '320' in 'airbusa320' -> True.
        
        matches = self.data[self.data['normalized_name'].str.contains(search_term, na=False)]
        
        if not matches.empty:
            # Return the first match (simplest)
            row = matches.iloc[0]
            return {
                'name': row['aircraft_type'],
                'max_pax': row['max_pax'],
                'fuel_kg_km': row['fuel_kg_km']
            }
            
        return None

# Singleton instance
fuel_db = FuelUtils()
