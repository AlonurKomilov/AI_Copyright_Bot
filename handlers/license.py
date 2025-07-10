# handlers/license.py

from aiogram import Router
from aiogram.types import Message
import json
from pathlib import Path
from config import config
import secrets
from datetime import datetime, timedelta

license_router = Router()

LICENSE_FILE = Path("data/licenses.json")
ACTIVE_USERS_FILE = Path("data/pro_users.json")

# Load license keys
if LICENSE_FILE.exists():
    with open(LICENSE_FILE, "r") as f:
        license_keys = set(json.load(f))
else:
    license_keys = set()

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
        json.dump(list(license_keys), f)

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

    # Set expiry to 30 days from today
    expiry_date = (datetime.utcnow() + timedelta(days=30)).strftime("%Y-%m-%d")
    pro_users[telegram_id] = expiry_date
    license_keys.remove(license_key)
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

    new_key = secrets.token_hex(4).upper()  # example: 7F8A9C2E
    license_keys.add(new_key)
    save_licenses()
    await message.answer(f"🆕 License key generated: `{new_key}`", parse_mode="Markdown")

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
