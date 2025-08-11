# models/pro_users.py (updated with AI fields)

from datetime import datetime
from typing import Optional, List, Dict
import json
from pathlib import Path

# Path to PRO user settings file
PRO_USERS_FILE = Path("data/pro_users.json")

# Default structure for each PRO user
class ProUser:
    def __init__(self, telegram_id: int, expires_at: str):
        self.telegram_id = telegram_id  # numeric user ID
        self.expires_at = expires_at    # ISO date string: YYYY-MM-DD
        self.target_channel: Optional[str] = None
        self.source_channels: List[str] = []
        self.filters: List[str] = []
        self.media_types: List[str] = []
        self.active: bool = True
        self.ai_enabled: bool = True
        self.ai_model: str = "GPT-3.5 Turbo"

    def to_dict(self):
        return {
            "expires_at": self.expires_at,
            "target_channel": self.target_channel,
            "source_channels": self.source_channels,
            "filters": self.filters,
            "media_types": self.media_types,
            "active": self.active,
            "ai_enabled": self.ai_enabled,
            "ai_model": self.ai_model,
        }

    @staticmethod
    def from_dict(telegram_id: int, data: Dict):
        user = ProUser(telegram_id, data.get("expires_at", "1970-01-01"))
        user.target_channel = data.get("target_channel")
        user.source_channels = data.get("source_channels", [])
        user.filters = data.get("filters", [])
        user.media_types = data.get("media_types", [])
        user.active = data.get("active", True)
        user.ai_enabled = data.get("ai_enabled", True)
        user.ai_model = data.get("ai_model", "GPT-3.5 Turbo")
        return user


# Load all PRO users
def load_pro_users() -> Dict[str, ProUser]:
    if not PRO_USERS_FILE.exists():
        return {}
    with open(PRO_USERS_FILE, "r") as f:
        raw = json.load(f)
    return {
        uid: ProUser.from_dict(int(uid), data)
        for uid, data in raw.items()
    }

# Save all PRO users
def save_pro_users(users: Dict[str, ProUser]):
    # Ensure the parent directory exists
    PRO_USERS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(PRO_USERS_FILE, "w") as f:
        json.dump({uid: user.to_dict() for uid, user in users.items()}, f, indent=2)
