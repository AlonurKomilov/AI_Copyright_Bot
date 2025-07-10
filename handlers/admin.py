from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from config import config
import database
from keyboards import main_menu, cancel_keyboard
from handlers.state_groups import StateGroups
from models.pro_users import load_pro_users

admin_router = Router()
pro_users = load_pro_users()

def admin_only(handler):
    async def wrapper(message: Message, *args, **kwargs):
        if message.from_user.id not in config.ADMIN_IDS:
            await message.answer("🚫 Access denied.")
            return
        return await handler(message, *args, **kwargs)
    return wrapper

# === Start ===
@admin_router.message(F.text == "/start")
@admin_only
async def start_command(message: Message):
    await message.answer("👋 Welcome to AI Bot Control Panel", reply_markup=main_menu())

@admin_router.message(F.text == "◀️ Cancel")
@admin_only
async def cancel_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ Cancelled", reply_markup=main_menu())

# === Info ===
@admin_router.message(F.text == "ℹ️ Bot Info")
@admin_only
async def bot_info(message: Message):
    try:
        ai = database.get_ai_status()
        msg = [
            f"📡 Sources: {', '.join(database.get_all_sources())}",
            f"🎯 Target: {database.get_target_chat() or 'Not set'}",
            f"🧾 Keywords: {', '.join(database.get_all_spam_keywords())}",
            f"🧱 Types: {', '.join(database.get_all_spam_types())}",
            f"🤖 Model: {ai['model']}",
            "🟢 AI is ON" if ai['enabled'] else "🔴 AI is OFF"
        ]
        await message.answer("\n".join(msg))
    except Exception as e:
        await message.answer("❌ Failed to load bot info.")

# === Manage PRO user ===
@admin_router.message(F.text.startswith("/manage_pro"))
@admin_only
async def manage_pro_user(message: Message):
    parts = message.text.strip().split()
    if len(parts) != 2 or not parts[1].isdigit():
        await message.answer("❌ Usage: /manage_pro TELEGRAM_ID")
        return

    target_id = parts[1]
    user = pro_users.get(target_id)

    if not user:
        await message.answer("❌ No PRO user found with this ID.")
        return

    text = (
        f"👤 User ID: {target_id}\n"
        f"📅 Expires: {user.expires_at}\n"
        f"📡 Target: {user.target_channel or '—'}\n"
        f"📥 Sources: {', '.join(user.source_channels) or '—'}\n"
        f"🔤 Filters: {', '.join(user.filters) or '—'}\n"
        f"📁 Media Types: {', '.join(user.media_types) or '—'}\n"
        f"🤖 AI: {user.ai_model} ({'🟢 Enabled' if user.ai_enabled else '🔴 Disabled'})\n"
        f"{'🟢 Active' if user.active else '🔴 Inactive'}"
    )

    await message.answer(text)

# === Sources ===
@admin_router.message(F.text == "➕ Add Source")
@admin_only
async def add_source(message: Message, state: FSMContext):
    await state.set_state(StateGroups.AddSource.username)
    await message.answer("Enter @source username:", reply_markup=cancel_keyboard())

@admin_router.message(StateGroups.AddSource.username)
@admin_only
async def save_source(message: Message, state: FSMContext):
    database.add_source(message.text.strip())
    await state.clear()
    await message.answer("✅ Source added", reply_markup=main_menu())

@admin_router.message(F.text == "❌ Remove Source")
@admin_only
async def del_source(message: Message, state: FSMContext):
    await state.set_state(StateGroups.RemoveSource.username)
    await message.answer("Enter @source to remove:", reply_markup=cancel_keyboard())

@admin_router.message(StateGroups.RemoveSource.username)
@admin_only
async def confirm_del_source(message: Message, state: FSMContext):
    database.del_source(message.text.strip())
    await state.clear()
    await message.answer("✅ Source removed", reply_markup=main_menu())

# === Target Chat ===
@admin_router.message(F.text == "🎯 Set Target")
@admin_only
async def set_target(message: Message, state: FSMContext):
    await state.set_state(StateGroups.SetTarget.username)
    await message.answer("Enter @target chat:", reply_markup=cancel_keyboard())

@admin_router.message(StateGroups.SetTarget.username)
@admin_only
async def save_target(message: Message, state: FSMContext):
    database.set_target_chat(message.text.strip())
    await state.clear()
    await message.answer("✅ Target set", reply_markup=main_menu())

# === Spam Keywords ===
@admin_router.message(F.text == "➕ Add Keyword")
@admin_only
async def add_keyword(message: Message, state: FSMContext):
    await state.set_state(StateGroups.AddSpamKeyword.keyword)
    await message.answer("Enter spam keyword:", reply_markup=cancel_keyboard())

@admin_router.message(StateGroups.AddSpamKeyword.keyword)
@admin_only
async def save_keyword(message: Message, state: FSMContext):
    database.add_spam_keyword(message.text.strip())
    await state.clear()
    await message.answer("✅ Keyword added", reply_markup=main_menu())

@admin_router.message(F.text == "❌ Remove Keyword")
@admin_only
async def remove_keyword(message: Message, state: FSMContext):
    await state.set_state(StateGroups.RemoveSpamKeyword.keyword)
    await message.answer("Enter keyword to remove:", reply_markup=cancel_keyboard())

@admin_router.message(StateGroups.RemoveSpamKeyword.keyword)
@admin_only
async def confirm_remove_keyword(message: Message, state: FSMContext):
    database.del_spam_keyword(message.text.strip())
    await state.clear()
    await message.answer("✅ Keyword removed", reply_markup=main_menu())

# === Spam Types ===
@admin_router.message(F.text == "➕ Add Type")
@admin_only
async def add_type(message: Message, state: FSMContext):
    await state.set_state(StateGroups.AddSpamType.type)
    await message.answer("Enter type (text/photo/video...):", reply_markup=cancel_keyboard())

@admin_router.message(StateGroups.AddSpamType.type)
@admin_only
async def save_type(message: Message, state: FSMContext):
    database.add_spam_type(message.text.strip().lower())
    await state.clear()
    await message.answer("✅ Type added", reply_markup=main_menu())

@admin_router.message(F.text == "❌ Remove Type")
@admin_only
async def remove_type(message: Message, state: FSMContext):
    await state.set_state(StateGroups.RemoveSpamType.type)
    await message.answer("Enter type to remove:", reply_markup=cancel_keyboard())

@admin_router.message(StateGroups.RemoveSpamType.type)
@admin_only
async def confirm_remove_type(message: Message, state: FSMContext):
    database.del_spam_type(message.text.strip().lower())
    await state.clear()
    await message.answer("✅ Type removed", reply_markup=main_menu())
