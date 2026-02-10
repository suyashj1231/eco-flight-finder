from dataclasses import dataclass, field, asdict
from typing import Optional
from datetime import datetime


@dataclass
class UserProfile:
    """User profile for personalization and tracking"""
    google_id: str
    email: str
    first_name: str
    last_name: str
    age: int
    height_cm: float
    weight_kg: float
    preferences: Optional[dict] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict):
        """Create from dictionary"""
        return cls(**data)
