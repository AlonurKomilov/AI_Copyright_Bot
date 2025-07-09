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