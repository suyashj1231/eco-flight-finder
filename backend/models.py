from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True) # Used for login (email or username)
    first_name = Column(String)
    last_name = Column(String)
    age = Column(Integer)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

    searches = relationship("SearchHistory", back_populates="owner")

class SearchHistory(Base):
    __tablename__ = "search_history"

    id = Column(Integer, primary_key=True, index=True)
    departure_iata = Column(String, index=True)
    arrival_iata = Column(String, index=True)
    departure_date = Column(String)
    return_date = Column(String, nullable=True)
    search_timestamp = Column(DateTime, default=datetime.utcnow)
    
    user_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="searches")
