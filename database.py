import sqlite3
from config import Config

DATABASE_NAME = Config.DATABASE_NAME

def add_spam_keyword(keyword: str):
    conn = sqlite3.connect(DATABASE_NAME)
    conn.execute("INSERT OR REPLACE INTO spam_keywords VALUES (?)", (keyword,));
    conn.commit()
    conn.close()

def del_spam_keyword(keyword: str):
    conn = sqlite3.connect(DATABASE_NAME)
    conn.execute("DELETE FROM spam_keywords WHERE keyword = ?", (keyword,))
    conn.commit()
    conn.close()

def get_all_spam_keywords():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT keyword FROM spam_keywords")
    spam_keywords = [row[0] for row in cursor.fetchall()]
    conn.close()
    return spam_keywords

def add_spam_type(spam_type: str):
    conn = sqlite3.connect(DATABASE_NAME)
    conn.execute("INSERT OR REPLACE INTO spam_types VALUES (?)", (spam_type,));
    conn.commit()
    conn.close()

def del_spam_type(spam_type: str):
    conn = sqlite3.connect(DATABASE_NAME)
    conn.execute("DELETE FROM spam_types WHERE type = ?", (spam_type,))
    conn.commit()
    conn.close()

def get_all_spam_types():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT type FROM spam_types")
    spam_types = [row[0] for row in cursor.fetchall()]
    conn.close()
    return spam_types

def add_source(username: str):
    conn = sqlite3.connect(DATABASE_NAME)
    conn.execute("INSERT OR REPLACE INTO sources VALUES (?, CURRENT_TIMESTAMP)", (username,))
    conn.commit()
    conn.close()

def get_all_sources():
    """Get all source channels/groups"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM sources ORDER BY added_at DESC")
    sources = [row[0] for row in cursor.fetchall()]
    conn.close()
    return sources

def del_source(username: str):
    """Remove a source channel/group"""
    conn = sqlite3.connect(DATABASE_NAME)
    conn.execute("DELETE FROM sources WHERE username = ?", (username,))
    conn.commit()
    conn.close()

def set_target_chat(username: str):
    conn = sqlite3.connect(DATABASE_NAME)
    conn.execute("DELETE FROM target_chat")  # Clear previous
    conn.execute("INSERT INTO target_chat VALUES (?)", (username,))
    conn.commit()
    conn.close()

def get_target_chat():
    """Get current target channel"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM target_chat LIMIT 1")
    target = cursor.fetchone()
    conn.close()
    return target[0] if target else None

def enable_ai():
    """Enable AI message processing"""
    conn = sqlite3.connect(DATABASE_NAME)
    conn.execute("UPDATE ai_settings SET is_enabled = 1 WHERE id = 1")
    conn.commit()
    conn.close()

def disable_ai():
    """Disable AI message processing"""
    conn = sqlite3.connect(DATABASE_NAME)
    conn.execute("UPDATE ai_settings SET is_enabled = 0 WHERE id = 1")
    conn.commit()
    conn.close()

def set_ai_model(model: str):
    """Change active AI model"""
    conn = sqlite3.connect(DATABASE_NAME)
    conn.execute("UPDATE ai_settings SET model = ? WHERE id = 1", (model,))
    conn.commit()
    conn.close()

def get_ai_status():
    """Get current AI settings"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT model, is_enabled FROM ai_settings WHERE id = 1")
    result = cursor.fetchone()
    conn.close()
    return {
        'model': result[0],
        'enabled': bool(result[1])
    } if result else None

# === User Usage Tracking ===
from datetime import date

def check_and_update_user(user_id: int) -> int:
    """
    Checks a user's request count. If the last request was on a previous day,
    resets the count. Creates the user if they don't exist.
    Returns the current request count for today.
    """
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    today = date.today().isoformat()

    # Try to get the user
    cursor.execute("SELECT requests_count, last_request_date FROM users WHERE user_id = ?", (user_id,))
    user_data = cursor.fetchone()

    if user_data:
        requests_count, last_request_date = user_data
        if last_request_date != today:
            # It's a new day, reset the count
            requests_count = 0
            cursor.execute(
                "UPDATE users SET requests_count = 0, last_request_date = ? WHERE user_id = ?",
                (today, user_id)
            )
    else:
        # User does not exist, create them
        requests_count = 0
        cursor.execute(
            "INSERT INTO users (user_id, requests_count, last_request_date) VALUES (?, ?, ?)",
            (user_id, 0, today)
        )

    conn.commit()
    conn.close()
    return requests_count

def increment_request_count(user_id: int):
    """Increments the request count for a user."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET requests_count = requests_count + 1 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()