import json
import sqlite3
from pathlib import Path

# Database and JSON file paths
DB_FILE = "userbot.db"
PRO_USERS_FILE = Path("data/pro_users.json")
LICENSES_FILE = Path("data/licenses.json")

def migrate_data():
    """
    Migrates data from JSON files to the SQLite database.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Migrate pro_users.json
    if PRO_USERS_FILE.exists():
        print(f"Migrating data from {PRO_USERS_FILE}...")
        with open(PRO_USERS_FILE, "r") as f:
            pro_users_data = json.load(f)

        for user_id, data in pro_users_data.items():
            cursor.execute("""
                INSERT OR REPLACE INTO pro_users (
                    user_id, expires_at, target_channel, source_channels,
                    filters, media_types, active, ai_enabled, ai_model
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                int(user_id),
                data.get("expires_at"),
                data.get("target_channel"),
                json.dumps(data.get("source_channels", [])),
                json.dumps(data.get("filters", [])),
                json.dumps(data.get("media_types", [])),
                data.get("active", True),
                data.get("ai_enabled", True),
                data.get("ai_model", "GPT-3.5 Turbo")
            ))
        print(f"Successfully migrated {len(pro_users_data)} users from {PRO_USERS_FILE}.")
    else:
        print(f"{PRO_USERS_FILE} not found. Skipping pro user migration.")

    # Migrate licenses.json
    if LICENSES_FILE.exists():
        print(f"Migrating data from {LICENSES_FILE}...")
        with open(LICENSES_FILE, "r") as f:
            licenses_data = json.load(f)

        for license_key, duration_days in licenses_data.items():
            cursor.execute("""
                INSERT OR REPLACE INTO licenses (license_key, duration_days)
                VALUES (?, ?)
            """, (license_key, duration_days))
        print(f"Successfully migrated {len(licenses_data)} licenses from {LICENSES_FILE}.")
    else:
        print(f"{LICENSES_FILE} not found. Skipping license migration.")

    conn.commit()
    conn.close()
    print("Data migration completed.")

if __name__ == "__main__":
    migrate_data()
