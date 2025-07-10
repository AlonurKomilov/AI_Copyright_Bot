# handlers/license.py

from aiogram import Router
from aiogram.types import Message
import json
from pathlib import Path
from config import config

license_router = Router()

LICENSE_FILE = Path("data/licenses.json")
ACTIVE_USERS_FILE = Path("data/pro_users.json")

# Load license keys
if LICENSE_FILE.exists():
    with open(LICENSE_FILE, "r") as f:
        license_keys = set(json.load(f))
else:
    license_keys = set()

# Load active PRO users
if ACTIVE_USERS_FILE.exists():
    with open(ACTIVE_USERS_FILE, "r") as f:
        pro_users = set(json.load(f))
else:
    pro_users = set()

@license_router.message(commands=["activate_license"])
async def activate_license(message: Message):
    try:
        parts = message.text.strip().split()
        if len(parts) != 2:
            await message.answer("❌ Usage: /activate_license YOUR-LICENSE-KEY")
            return

        license_key = parts[1]
        telegram_id = message.from_user.id

        if telegram_id in pro_users:
            await message.answer("✅ You already have PRO access.")
            return

        if license_key not in license_keys:
            await message.answer("❌ Invalid or expired license key.")
            return

        # Activate user and remove key
        pro_users.add(telegram_id)
        license_keys.remove(license_key)

        # Save updates
        LICENSE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(LICENSE_FILE, "w") as f:
            json.dump(list(license_keys), f)
        with open(ACTIVE_USERS_FILE, "w") as f:
            json.dump(list(pro_users), f)

        await message.answer("✅ License activated. You now have PRO access!")

    except Exception as e:
        await message.answer("❌ Failed to activate license.")
        print("License activation error:", e)

@license_router.message(commands=["is_pro"])
async def check_pro_status(message: Message):
    telegram_id = message.from_user.id
    if telegram_id in pro_users or telegram_id in config.ADMIN_IDS:
        await message.answer("✅ You are a PRO user.")
    else:
        await message.answer("🔒 You are not a PRO user.")
