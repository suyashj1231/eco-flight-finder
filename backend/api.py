from typing import Optional
import sys
import os
from pathlib import Path

# Load environment variables first
from dotenv import load_dotenv, find_dotenv
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Add backend directory to Python path
sys.path.insert(0, os.path.dirname(__file__))


from search_context import SearchContext, SortBy
from flight_api import search_flights
from flight_recommendation import FlightRecommender

app = FastAPI(title="Eco Flight Finder API")

# CORS setup - allow local frontend development origins by default
from fastapi.middleware.cors import CORSMiddleware
_origins = os.getenv("FRONTEND_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




class SearchRequest(BaseModel):
    # google_id removed as user management is deleted

    departure_iata: str
    arrival_iata: str
    departure_date: str
    return_date: Optional[str] = None
    eco_mode: bool = False
    sort_by: Optional[str] = None
    max_price: Optional[float] = None
    max_emissions: Optional[float] = None
    max_duration_hours: Optional[float] = None


@app.get("/health")
def health():
    return {"status": "ok"}





@app.post("/search")
def search_and_recommend(req: SearchRequest):
    # Retrieve user logic removed


    # Build search context
    sort_by = None
    if req.sort_by:
        try:
            sort_by = SortBy(req.sort_by)
        except ValueError:
            # allow string names like "price" etc.
            sort_by = None

    context = SearchContext(
        departure_iata=req.departure_iata,
        arrival_iata=req.arrival_iata,
        departure_date=req.departure_date,
        return_date=req.return_date,
        eco_mode=req.eco_mode,
        seat_class="economy",
        max_price=req.max_price,
        max_emissions=req.max_emissions,
        max_duration_hours=req.max_duration_hours,
    )

    # Override sort_by if provided
    if sort_by:
        context.sort_by = sort_by

    # Call the flight search for outbound (and inbound if roundtrip)
    outbound = search_flights(req.departure_iata, req.arrival_iata, req.departure_date)
    if outbound is None:
        raise HTTPException(status_code=500, detail="Flight API error (outbound)")

    inbound = []
    if req.return_date:
        inbound = search_flights(req.arrival_iata, req.departure_iata, req.return_date)
        if inbound is None:
            raise HTTPException(status_code=500, detail="Flight API error (inbound)")

    # Build composite roundtrip options: pair each outbound with each inbound
    composites = []
    if req.return_date and inbound:
        for out in outbound:
            for inn in inbound:
                composites.append({
                    'outbound': out,
                    'inbound': inn
                })
    else:
        # Treat each outbound as a single-leg composite (roundtrip assumed same leg)
        for out in outbound:
            composites.append(out)

    recommender = FlightRecommender()
    ranked = recommender.rank_flights(composites, context)

    # Convert to serializable structure
    output = []
    for item in ranked:
        entry = {
            "filtered_out": item.get("filtered_out", False),
            "filter_reason": item.get("filter_reason"),
            "rank_score": item.get("rank_score"),
            "explanation": item.get("explanation", []),
            "flight": item.get("flight") or item.get("flight")
        }
        output.append(entry)

    return {"results": output}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True)
