import sqlite3
import json
from typing import Optional, List, Dict
from config import Config

class ProUser:
    def __init__(self, telegram_id: int, expires_at: str, target_channel: Optional[str] = None,
                 source_channels: Optional[List[str]] = None, filters: Optional[List[str]] = None,
                 media_types: Optional[List[str]] = None, active: bool = True,
                 ai_enabled: bool = True, ai_model: str = "GPT-3.5 Turbo"):
        self.telegram_id = telegram_id
        self.expires_at = expires_at
        self.target_channel = target_channel
        self.source_channels = source_channels or []
        self.filters = filters or []
        self.media_types = media_types or []
        self.active = active
        self.ai_enabled = ai_enabled
        self.ai_model = ai_model

def get_db_connection():
    return sqlite3.connect(Config.DATABASE_NAME)

def load_pro_users() -> Dict[str, ProUser]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pro_users")
    users = {}
    for row in cursor.fetchall():
        user_id, expires_at, target_channel, source_channels, filters, media_types, active, ai_enabled, ai_model = row
        users[str(user_id)] = ProUser(
            telegram_id=user_id,
            expires_at=expires_at,
            target_channel=target_channel,
            source_channels=json.loads(source_channels) if source_channels else [],
            filters=json.loads(filters) if filters else [],
            media_types=json.loads(media_types) if media_types else [],
            active=bool(active),
            ai_enabled=bool(ai_enabled),
            ai_model=ai_model
        )
    conn.close()
    return users

def save_pro_user(user: ProUser):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO pro_users (
            user_id, expires_at, target_channel, source_channels,
            filters, media_types, active, ai_enabled, ai_model
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user.telegram_id,
        user.expires_at,
        user.target_channel,
        json.dumps(user.source_channels),
        json.dumps(user.filters),
        json.dumps(user.media_types),
        user.active,
        user.ai_enabled,
        user.ai_model
    ))
    conn.commit()
    conn.close()

def load_pro_user(user_id: int) -> Optional[ProUser]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pro_users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        user_id, expires_at, target_channel, source_channels, filters, media_types, active, ai_enabled, ai_model = row
        return ProUser(
            telegram_id=user_id,
            expires_at=expires_at,
            target_channel=target_channel,
            source_channels=json.loads(source_channels) if source_channels else [],
            filters=json.loads(filters) if filters else [],
            media_types=json.loads(media_types) if media_types else [],
            active=bool(active),
            ai_enabled=bool(ai_enabled),
            ai_model=ai_model
        )
    return None
