from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class SortBy(str, Enum):
    """Ranking modes for flight recommendations"""
    PRICE = "price"
    EMISSIONS = "emissions"
    DURATION = "duration"
    ECO_BALANCED = "eco_balanced"


@dataclass
class SearchContext:
    """Encapsulates search parameters and ranking preferences"""
    departure_iata: str
    arrival_iata: str
    departure_date: str  # YYYY-MM-DD
    return_date: Optional[str] = None  # YYYY-MM-DD for roundtrip
    eco_mode: bool = True
    seat_class: str = "economy"
    sort_by: SortBy = SortBy.EMISSIONS
    max_price: Optional[float] = None
    max_emissions: Optional[float] = None
    max_duration_hours: Optional[float] = None
