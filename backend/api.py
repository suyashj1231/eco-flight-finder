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

from user_manager import user_manager
from user_model import UserProfile
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

GOOGLE_TOKENINFO_URL = "https://oauth2.googleapis.com/tokeninfo"


class AuthToken(BaseModel):
    id_token: str


class CreateUserRequest(BaseModel):
    google_id: str
    email: str
    first_name: str
    last_name: str
    age: int
    height_cm: float
    weight_kg: float


class SearchRequest(BaseModel):
    google_id: Optional[str]
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


@app.post("/auth/google")
def auth_google(token: AuthToken):
    """Verify Google ID token using Google's tokeninfo endpoint and return basic profile info.
    Note: For production verify audience (client_id) and use the official Google libraries.
    """
    params = {"id_token": token.id_token}
    try:
        resp = requests.get(GOOGLE_TOKENINFO_URL, params=params)
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Token verification failed: {e}")

    # Expected keys include: sub (user id), email, email_verified, name, given_name, family_name
    google_id = data.get("sub")
    email = data.get("email")
    first_name = data.get("given_name")
    last_name = data.get("family_name")

    if not google_id or not email:
        raise HTTPException(status_code=400, detail="Invalid token: missing user info")

    return {
        "google_id": google_id,
        "email": email,
        "first_name": first_name,
        "last_name": last_name,
        "raw": data,
    }


@app.post("/user")
def create_or_update_user(req: CreateUserRequest):
    user = user_manager.create_or_update_user(
        google_id=req.google_id,
        email=req.email,
        first_name=req.first_name,
        last_name=req.last_name,
        age=req.age,
        height_cm=req.height_cm,
        weight_kg=req.weight_kg,
    )

    return user.to_dict()


@app.get("/user/{google_id}")
def get_user(google_id: str):
    user = user_manager.get_user(google_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user.to_dict()


@app.post("/search")
def search_and_recommend(req: SearchRequest):
    # Retrieve user if provided (optional for guest search)
    user = None
    if req.google_id:
        user = user_manager.get_user(req.google_id)

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

    # Use a lightweight user placeholder if none provided
    if not user:
        user = UserProfile(
            google_id="guest",
            email="",
            first_name="Guest",
            last_name="",
            age=0,
            height_cm=0.0,
            weight_kg=0.0,
        )

    recommender = FlightRecommender(user)
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
