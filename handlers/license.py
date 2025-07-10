# handlers/license.py

from aiogram import Router
from aiogram.types import Message, FSInputFile
import json
from pathlib import Path
from config import config
import secrets
from datetime import datetime, timedelta
import csv

license_router = Router()

LICENSE_FILE = Path("data/licenses.json")
ACTIVE_USERS_FILE = Path("data/pro_users.json")
EXPORT_FILE = Path("data/pro_users_export.csv")

# Load license keys
if LICENSE_FILE.exists():
    with open(LICENSE_FILE, "r") as f:
        license_keys = json.load(f)  # Now expects dict: {"KEY123": 30}
else:
    license_keys = {}  # key: duration_in_days

# Load active PRO users with expiry
if ACTIVE_USERS_FILE.exists():
    with open(ACTIVE_USERS_FILE, "r") as f:
        pro_users = json.load(f)
else:
    pro_users = {}

# Save helpers
def save_licenses():
    LICENSE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LICENSE_FILE, "w") as f:
        json.dump(license_keys, f)

def save_pro_users():
    with open(ACTIVE_USERS_FILE, "w") as f:
        json.dump(pro_users, f)

@license_router.message(commands=["activate_license"])
async def activate_license(message: Message):
    parts = message.text.strip().split()
    if len(parts) != 2:
        await message.answer("❌ Usage: /activate_license YOUR-LICENSE-KEY")
        return

    license_key = parts[1]
    telegram_id = str(message.from_user.id)

    if telegram_id in pro_users:
        await message.answer("✅ You already have PRO access.")
        return

    if license_key not in license_keys:
        await message.answer("❌ Invalid or expired license key.")
        return

    # Set expiry based on license duration
    days = license_keys[license_key]
    expiry_date = (datetime.utcnow().date() + timedelta(days=days - 1)).strftime("%Y-%m-%d")
    pro_users[telegram_id] = expiry_date
    del license_keys[license_key]
    save_licenses()
    save_pro_users()

    await message.answer(f"✅ License activated. PRO access valid until {expiry_date}.")

@license_router.message(commands=["is_pro"])
async def check_pro_status(message: Message):
    telegram_id = str(message.from_user.id)
    today = datetime.utcnow().date()

    if telegram_id in pro_users:
        expiry = datetime.strptime(pro_users[telegram_id], "%Y-%m-%d").date()
        if expiry >= today:
            await message.answer(f"✅ You are a PRO user until {expiry}.")
            return
        else:
            del pro_users[telegram_id]
            save_pro_users()

    if message.from_user.id in config.ADMIN_IDS:
        await message.answer("✅ You are an ADMIN (PRO by default).")
    else:
        await message.answer("🔒 You are not a PRO user.")

@license_router.message(commands=["generate_license"])
async def generate_license_key(message: Message):
    if message.from_user.id not in config.ADMIN_IDS:
        await message.answer("🚫 Access denied.")
        return

    parts = message.text.strip().split()
    if len(parts) != 2 or parts[1] not in ["30", "365"]:
        await message.answer("❌ Usage: /generate_license [30|365]  (days of validity)")
        return

    days = int(parts[1])
    new_key = secrets.token_hex(4).upper()  # example: 7F8A9C2E
    license_keys[new_key] = days
    save_licenses()
    await message.answer(f"🆕 License key generated: `{new_key}`\nValid for {days} days", parse_mode="Markdown")

@license_router.message(commands=["revoke_pro"])
async def revoke_pro_user(message: Message):
    if message.from_user.id not in config.ADMIN_IDS:
        await message.answer("🚫 Access denied.")
        return

    parts = message.text.strip().split()
    if len(parts) != 2 or not parts[1].isdigit():
        await message.answer("❌ Usage: /revoke_pro TELEGRAM_ID")
        return

    target_id = parts[1]
    if target_id in pro_users:
        del pro_users[target_id]
        save_pro_users()
        await message.answer(f"🗑️ PRO access revoked for user ID: {target_id}")
    else:
        await message.answer("ℹ️ This user is not a PRO user.")

@license_router.message(commands=["list_pro"])
async def list_pro_users(message: Message):
    if message.from_user.id not in config.ADMIN_IDS:
        await message.answer("🚫 Access denied.")
        return

    today = datetime.utcnow().date()
    if not pro_users:
        await message.answer("ℹ️ No active PRO users found.")
        return

    result_lines = ["🧑‍💻 Active PRO Users:"]
    for user_id, expiry_str in pro_users.items():
        expiry = datetime.strptime(expiry_str, "%Y-%m-%d").date()
        status = "✅ active" if expiry >= today else "❌ expired"
        result_lines.append(f"👤 {user_id} — until {expiry_str} ({status})")

    await message.answer("\n".join(result_lines))

@license_router.message(commands=["export_pro"])
async def export_pro_users(message: Message):
    if message.from_user.id not in config.ADMIN_IDS:
        await message.answer("🚫 Access denied.")
        return

    EXPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(EXPORT_FILE, mode="w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Telegram ID", "Expiry Date"])
        for user_id, expiry_str in pro_users.items():
            writer.writerow([user_id, expiry_str])

    file = FSInputFile(EXPORT_FILE)
    await message.answer_document(file, caption="📤 Exported PRO user list")

@license_router.message(commands=["import_pro"])
async def import_pro_users(message: Message):
    if message.from_user.id not in config.ADMIN_IDS:
        await message.answer("🚫 Access denied.")
        return

    if not message.document:
        await message.answer("📎 Please attach a CSV file.")
        return

    try:
        file = await message.bot.get_file(message.document.file_id)
        file_path = file.file_path
        content = await message.bot.download_file(file_path)

        # Read CSV from file content
        lines = content.read().decode("utf-8").splitlines()
        reader = csv.DictReader(lines)

        imported = 0
        for row in reader:
            telegram_id = str(row.get("Telegram ID", "").strip())
            expiry_str = row.get("Expiry Date", "").strip()
            if telegram_id and expiry_str:
                try:
                    datetime.strptime(expiry_str, "%Y-%m-%d")  # validate date format
                    pro_users[telegram_id] = expiry_str
                    imported += 1
                except ValueError:
                    continue

        save_pro_users()
        await message.answer(f"✅ Imported {imported} PRO users from file.")

    except Exception as e:
        await message.answer("❌ Failed to import file.")
        print("Import error:", e)
