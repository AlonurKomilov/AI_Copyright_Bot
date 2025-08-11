import sqlite3
from config import Config

def migrate():
    print("Running database migration...")
    conn = sqlite3.connect(Config.DATABASE_NAME)
    cursor = conn.cursor()

    # Create users table for tracking usage
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            requests_count INTEGER DEFAULT 0,
            last_request_date TEXT
        )
    """)

    conn.commit()
    conn.close()
    print("Migration completed successfully.")

if __name__ == "__main__":
    migrate()
