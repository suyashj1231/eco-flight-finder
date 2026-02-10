import json
from pathlib import Path
from typing import Optional, Dict
from user_model import UserProfile


class UserManager:
    """Manages user profile CRUD operations with JSON persistence"""

    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(__file__).parent / data_dir
        self.data_dir.mkdir(exist_ok=True)
        self.users_file = self.data_dir / "users.json"
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        """Ensure users.json file exists"""
        if not self.users_file.exists():
            self.users_file.write_text(json.dumps({}))

    def create_or_update_user(
        self,
        google_id: str,
        email: str,
        first_name: str,
        last_name: str,
        age: int,
        height_cm: float,
        weight_kg: float,
        preferences: Optional[dict] = None,
    ) -> UserProfile:
        """Create or update a user profile"""
        user = UserProfile(
            google_id=google_id,
            email=email,
            first_name=first_name,
            last_name=last_name,
            age=age,
            height_cm=height_cm,
            weight_kg=weight_kg,
            preferences=preferences or {},
        )

        users = self._load_users()
        users[google_id] = user.to_dict()
        self._save_users(users)

        return user

    def get_user(self, google_id: str) -> Optional[UserProfile]:
        """Retrieve a user by Google ID"""
        users = self._load_users()
        user_data = users.get(google_id)
        if user_data:
            return UserProfile.from_dict(user_data)
        return None

    def update_preferences(self, google_id: str, preferences: dict) -> Optional[UserProfile]:
        """Update user preferences"""
        user = self.get_user(google_id)
        if user:
            user.preferences = preferences
            users = self._load_users()
            users[google_id] = user.to_dict()
            self._save_users(users)
            return user
        return None

    def _load_users(self) -> Dict:
        """Load all users from file"""
        try:
            content = self.users_file.read_text()
            return json.loads(content) if content else {}
        except Exception as e:
            print(f"Error loading users: {e}")
            return {}

    def _save_users(self, users: Dict):
        """Save all users to file"""
        try:
            self.users_file.write_text(json.dumps(users, indent=2))
        except Exception as e:
            print(f"Error saving users: {e}")


# Singleton instance
user_manager = UserManager()
