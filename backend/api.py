import sys
from typing import Optional
import os
import json
from pathlib import Path

import logging
import requests
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session

# Configure logging to console
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add backend directory to Python path
sys.path.insert(0, os.path.dirname(__file__))


from search_context import SearchContext, SortBy
from flight_api import search_flights
from flight_recommendation import FlightRecommender
import models, schemas, auth, database
from sqlalchemy.orm import Session
from fastapi import Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta

# Initialize DB tables
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Eco Flight Finder API")

# CORS setup - allow local frontend development origins by default
# CORS setup - allow all origins for development
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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

# --- Airport Suggestion Logic ---
AIRPORT_DATA = []
try:
    with open("airports.json", "r", encoding="utf-8") as f:
        AIRPORT_DATA = json.load(f)
    print(f"Loaded {len(AIRPORT_DATA)} airports.")
except Exception as e:
    print(f"Failed to load airports.json: {e}")

@app.get("/airports/search")
def search_airports(q: str):
    """
    Search airports by city, name, or IATA code.
    Results are limited to top 10 matches.
    """
    if not q or len(q) < 2:
        return []
        
    term = q.lower()
    matches = []
    
    # Simple direct matching first (could be optimized with trie/search engine)
    for airport in AIRPORT_DATA:
        # Check IATA exact match first (priority)
        if airport.get('iata', '').lower() == term:
            matches.insert(0, airport)
            continue
            
        # Check text fields
        text = f"{airport.get('city', '')} {airport.get('name', '')} {airport.get('country', '')} {airport.get('iata', '')}".lower()
        if term in text:
            matches.append(airport)
            
        if len(matches) >= 10:
            break
            
    return matches

# --- Auth Endpoints ---

@app.post("/register", response_model=schemas.User)
def register(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    logger.debug(f"Attempting to register user {user.username}")
    try:
        db_user = db.query(models.User).filter(models.User.username == user.username).first()
        if db_user:
            logger.warning(f"Username {user.username} already registered")
            raise HTTPException(status_code=400, detail="Username already registered")
        
        logger.debug("Hashing password...")
        hashed_password = auth.get_password_hash(user.password)
        logger.debug("Password hashed successfully")
        
        new_user = models.User(
            username=user.username,
            hashed_password=hashed_password,
            first_name=user.first_name,
            last_name=user.last_name,
            age=user.age
        )
        logger.debug("Adding user to DB...")
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        logger.debug("User registered successfully")
        return new_user
    except Exception as e:
        logger.error(f"ERROR inside register: {e}", exc_info=True)
        raise e

@app.post("/token", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=schemas.User)
def read_users_me(current_user: models.User = Depends(auth.get_current_user)):
    return current_user

@app.put("/users/me", response_model=schemas.User)
def update_user_me(user_update: schemas.UserUpdate, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
    if user_update.first_name:
        current_user.first_name = user_update.first_name
    if user_update.last_name:
        current_user.last_name = user_update.last_name
    if user_update.age is not None:
        current_user.age = user_update.age
    if user_update.results_per_page is not None:
        current_user.results_per_page = user_update.results_per_page
        
    if user_update.new_password:
        # Require old password if setting new one
        if not user_update.old_password:
             raise HTTPException(status_code=400, detail="Old password required to change password")
        if not auth.verify_password(user_update.old_password, current_user.hashed_password):
             raise HTTPException(status_code=400, detail="Incorrect old password")
        current_user.hashed_password = auth.get_password_hash(user_update.new_password)
    
    db.commit()
    db.refresh(current_user)
    return current_user

@app.delete("/users/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_me(current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
    # Delete search history first (if not cascading)
    db.query(models.SearchHistory).filter(models.SearchHistory.user_id == current_user.id).delete()
    
    # Delete user
    db.delete(current_user)
    db.commit()
    return None

@app.delete("/users/history", status_code=status.HTTP_204_NO_CONTENT)
def clear_search_history(current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
    db.query(models.SearchHistory).filter(models.SearchHistory.user_id == current_user.id).delete()
    db.commit()
    return None

@app.get("/users/history", response_model=list[schemas.SearchHistory])
def read_search_history(current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
    return current_user.searches





@app.post("/search")
def search_public(req: SearchRequest):
    return search_and_recommend_logic(req)

@app.post("/search_authenticated")
async def search_authenticated(req: SearchRequest, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
    # Save history
    history = models.SearchHistory(
        departure_iata=req.departure_iata,
        arrival_iata=req.arrival_iata,
        departure_date=req.departure_date,
        return_date=req.return_date,
        user_id=current_user.id
    )
    db.add(history)
    db.commit()
    
    return search_and_recommend_logic(req)

def search_and_recommend_logic(req: SearchRequest):
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

    # Rank outbound
    recommender = FlightRecommender()
    ranked_outbound = recommender.rank_flights(outbound, context)
    
    ranked_inbound = []
    if req.return_date and inbound:
        # Rank inbound
        ranked_inbound = recommender.rank_flights(inbound, context)

    # Convert to serializable structure helper
    def serialize_results(ranked_list):
        output = []
        for item in ranked_list:
            entry = {
                "filtered_out": item.get("filtered_out", False),
                "filter_reason": item.get("filter_reason"),
                "rank_score": item.get("rank_score"),
                "explanation": item.get("explanation", []),
                "flight": item.get("flight")
            }
            output.append(entry)
        return output

    return {
        "outbound": serialize_results(ranked_outbound),
        "inbound": serialize_results(ranked_inbound)
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True)
