from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class UserBase(BaseModel):
    username: str
    first_name: str
    last_name: str
    age: int

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    age: Optional[int] = None
    old_password: Optional[str] = None # Required if changing password
    new_password: Optional[str] = None

class User(UserBase):
    id: int
    is_active: bool
    
    class Config:
        from_attributes = True

class SearchHistoryBase(BaseModel):
    departure_iata: str
    arrival_iata: str
    departure_date: str
    return_date: Optional[str] = None
    
class SearchHistoryCreate(SearchHistoryBase):
    pass

class SearchHistory(SearchHistoryBase):
    id: int
    user_id: int
    search_timestamp: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
