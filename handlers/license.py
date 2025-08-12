import sqlite3
import secrets
from datetime import datetime, timedelta
import csv
from pathlib import Path
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile, ReplyKeyboardMarkup, KeyboardButton
from config import config
from models.pro_users import ProUser, save_pro_user, load_pro_user, load_pro_users

license_router = Router()
EXPORT_FILE = Path("data/pro_users_export.csv")

def get_db_connection():
    return sqlite3.connect(config.DATABASE_NAME)

# License DB functions
def add_license(license_key: str, duration_days: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO licenses (license_key, duration_days) VALUES (?, ?)", (license_key, duration_days))
    conn.commit()
    conn.close()

def get_license(license_key: str) -> tuple | None:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT duration_days FROM licenses WHERE license_key = ?", (license_key,))
    result = cursor.fetchone()
    conn.close()
    return result

def delete_license(license_key: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM licenses WHERE license_key = ?", (license_key,))
    conn.commit()
    conn.close()

# Pro User DB functions
def delete_pro_user(user_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM pro_users WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

@license_router.message(Command("admin_menu"))
async def show_admin_menu(message: Message):
    if message.from_user.id not in config.ADMIN_IDS:
        await message.answer("🚫 Access denied.")
        return

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="/generate_license 30"), KeyboardButton(text="/generate_license 365")],
            [KeyboardButton(text="/stats_pro"), KeyboardButton(text="/list_pro")],
            [KeyboardButton(text="/export_pro"), KeyboardButton(text="/import_pro")],
            [KeyboardButton(text="/renew_pro <id> <days>")],
            [KeyboardButton(text="/revoke_pro <id>")],
        ],
        resize_keyboard=True,
    )
    await message.answer("📋 Admin Control Panel:", reply_markup=keyboard)

@license_router.message(Command("generate_license"))
async def generate_license_key(message: Message):
    if message.from_user.id not in config.ADMIN_IDS:
        await message.answer("🚫 Access denied.")
        return

    parts = message.text.strip().split()
    if len(parts) != 2 or not parts[1].isdigit():
        await message.answer("❌ Usage: /generate_license <days>")
        return

    days = int(parts[1])
    new_key = secrets.token_hex(4).upper()
    add_license(new_key, days)
    await message.answer(f"🆕 License key generated: `{new_key}`\nValid for {days} days", parse_mode="Markdown")

@license_router.message(Command("activate_license"))
async def activate_license(message: Message):
    parts = message.text.strip().split()
    if len(parts) != 2:
        await message.answer("❌ Usage: /activate_license YOUR-LICENSE-KEY")
        return

    license_key = parts[1]
    user_id = message.from_user.id

    pro_user = load_pro_user(user_id)
    if pro_user and pro_user.active:
        await message.answer("✅ You already have PRO access.")
        return

    license_data = get_license(license_key)
    if not license_data:
        await message.answer("❌ Invalid or expired license key.")
        return

    days = license_data[0]
    expiry_date = (datetime.utcnow().date() + timedelta(days=days)).strftime("%Y-%m-%d")

    new_pro_user = ProUser(telegram_id=user_id, expires_at=expiry_date)
    save_pro_user(new_pro_user)
    delete_license(license_key)

    await message.answer(f"✅ License activated. PRO access valid until {expiry_date}.")

@license_router.message(Command("is_pro"))
async def check_pro_status(message: Message):
    user_id = message.from_user.id
    pro_user = load_pro_user(user_id)
    today = datetime.utcnow().date()

    if pro_user and datetime.strptime(pro_user.expires_at, "%Y-%m-%d").date() >= today:
        await message.answer(f"✅ You are a PRO user until {pro_user.expires_at}.")
    elif user_id in config.ADMIN_IDS:
        await message.answer("✅ You are an ADMIN (PRO by default).")
    else:
        await message.answer("🔒 You are not a PRO user.")

@license_router.message(Command("revoke_pro"))
async def revoke_pro_user(message: Message):
    if message.from_user.id not in config.ADMIN_IDS:
        await message.answer("🚫 Access denied.")
        return

    parts = message.text.strip().split()
    if len(parts) != 2 or not parts[1].isdigit():
        await message.answer("❌ Usage: /revoke_pro TELEGRAM_ID")
        return

    target_id = int(parts[1])
    pro_user = load_pro_user(target_id)
    if pro_user:
        delete_pro_user(target_id)
        await message.answer(f"🗑️ PRO access revoked for user ID: {target_id}")
    else:
        await message.answer("ℹ️ This user is not a PRO user.")

@license_router.message(Command("list_pro"))
async def list_pro_users(message: Message):
    if message.from_user.id not in config.ADMIN_IDS:
        await message.answer("🚫 Access denied.")
        return

    pro_users = load_pro_users()
    if not pro_users:
        await message.answer("ℹ️ No active PRO users found.")
        return

    today = datetime.utcnow().date()
    result_lines = ["🧑‍💻 Active PRO Users:"]
    for user in pro_users.values():
        expiry_date = datetime.strptime(user.expires_at, "%Y-%m-%d").date()
        status = "✅ active" if expiry_date >= today else "❌ expired"
        result_lines.append(f"👤 {user.telegram_id} — until {user.expires_at} ({status})")

    await message.answer("\n".join(result_lines))

@license_router.message(Command("stats_pro"))
async def stats_pro(message: Message):
    if message.from_user.id not in config.ADMIN_IDS:
        await message.answer("🚫 Access denied.")
        return

    pro_users = load_pro_users()
    today = datetime.utcnow().date()
    total = len(pro_users)
    active = 0
    expired = 0
    expiring_soon = 0

    for user in pro_users.values():
        expiry_date = datetime.strptime(user.expires_at, "%Y-%m-%d").date()
        if expiry_date >= today:
            active += 1
            if (expiry_date - today).days <= 7:
                expiring_soon += 1
        else:
            expired += 1

    msg = (
        f"📊 PRO Subscription Stats:\n"
        f"• Total PRO users: {total}\n"
        f"• ✅ Active: {active}\n"
        f"• ⏳ Expiring in ≤7 days: {expiring_soon}\n"
        f"• ❌ Expired: {expired}"
    )
    await message.answer(msg)

@license_router.message(Command("export_pro"))
async def export_pro_users(message: Message):
    if message.from_user.id not in config.ADMIN_IDS:
        await message.answer("🚫 Access denied.")
        return

    pro_users = load_pro_users()
    EXPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(EXPORT_FILE, mode="w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Telegram ID", "Expiry Date"])
        for user in pro_users.values():
            writer.writerow([user.telegram_id, user.expires_at])

    file = FSInputFile(EXPORT_FILE)
    await message.answer_document(file, caption="📤 Exported PRO user list")

@license_router.message(Command("renew_pro"))
async def renew_pro_user(message: Message):
    if message.from_user.id not in config.ADMIN_IDS:
        await message.answer("🚫 Access denied.")
        return

    parts = message.text.strip().split()
    if len(parts) != 3 or not parts[1].isdigit() or not parts[2].isdigit():
        await message.answer("❌ Usage: /renew_pro TELEGRAM_ID DAYS")
        return

    target_id = int(parts[1])
    days_to_add = int(parts[2])
    today = datetime.utcnow().date()

    pro_user = load_pro_user(target_id)
    if pro_user:
        current_expiry = datetime.strptime(pro_user.expires_at, "%Y-%m-%d").date()
        new_expiry = max(today, current_expiry) + timedelta(days=days_to_add)
        pro_user.expires_at = new_expiry.strftime("%Y-%m-%d")
    else:
        new_expiry = today + timedelta(days=days_to_add)
        pro_user = ProUser(telegram_id=target_id, expires_at=new_expiry.strftime("%Y-%m-%d"))

    save_pro_user(pro_user)
    await message.answer(f"🔁 PRO renewed for user {target_id} until {pro_user.expires_at}.")

@license_router.message(Command("import_pro"))
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

        lines = content.read().decode("utf-8").splitlines()
        reader = csv.DictReader(lines)

        imported_count = 0
        for row in reader:
            telegram_id_str = row.get("Telegram ID", "").strip()
            expiry_str = row.get("Expiry Date", "").strip()
            if telegram_id_str.isdigit() and expiry_str:
                try:
                    user_id = int(telegram_id_str)
                    datetime.strptime(expiry_str, "%Y-%m-%d")
                    pro_user = load_pro_user(user_id) or ProUser(telegram_id=user_id, expires_at=expiry_str)
                    pro_user.expires_at = expiry_str
                    save_pro_user(pro_user)
                    imported_count += 1
                except (ValueError, TypeError):
                    continue

        await message.answer(f"✅ Imported {imported_count} PRO users from file.")

    except Exception as e:
        await message.answer(f"❌ Failed to import file: {e}")
        print("Import error:", e)
