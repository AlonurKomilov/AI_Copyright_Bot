# handlers/pro_settings.py

from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from models.pro_users import load_pro_users, save_pro_users
from keyboards import model_selection_keyboard, pro_user_menu_keyboard, cancel_keyboard
from config import config

pro_router = Router()

class ProStates(StatesGroup):
    set_target = State()
    add_source = State()
    set_filters = State()
    set_media_types = State()
    set_ai_model = State()

# Helper to check for PRO status
def is_pro_user(user_id: int) -> bool:
    pro_users = load_pro_users()
    return str(user_id) in pro_users and pro_users[str(user_id)].active

# General cancel handler for all PRO states
@pro_router.message(F.text == "◀️ Cancel", ProStates)
async def cancel_pro_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ Action cancelled.", reply_markup=pro_user_menu_keyboard())

@pro_router.message(F.text == "/pro")
async def pro_menu(message: Message):
    if not is_pro_user(message.from_user.id):
        await message.answer("❌ You are not a PRO user.")
        return
    await message.answer("💎 *PRO Menu*", reply_markup=pro_user_menu_keyboard())

@pro_router.message(F.text == "/set_target")
async def start_set_target(message: Message, state: FSMContext):
    if not is_pro_user(message.from_user.id):
        await message.answer("❌ You are not a PRO user.")
        return
    await state.set_state(ProStates.set_target)
    await message.answer("📥 Send your target channel username (e.g. @mychannel):", reply_markup=cancel_keyboard())

@pro_router.message(ProStates.set_target)
async def save_target_channel(message: Message, state: FSMContext):
    uid = str(message.from_user.id)
    pro_users = load_pro_users()
    if uid not in pro_users:
        await message.answer("❌ You are not a PRO user.")
        return
    pro_users[uid].target_channel = message.text.strip()
    save_pro_users(pro_users)
    await state.clear()
    await message.answer(f"✅ Target channel set!", reply_markup=pro_user_menu_keyboard())

# ... (other handlers like add_source, set_filters, etc. would be updated similarly) ...
# For brevity, I will only focus on the AI-related handlers from now on.

@pro_router.message(F.text == "/ai_status")
async def ai_status(message: Message):
    if not is_pro_user(message.from_user.id):
        await message.answer("❌ You are not a PRO user.")
        return
    pro_users = load_pro_users()
    user = pro_users[str(message.from_user.id)]
    status = "🟢 Enabled" if user.ai_enabled else "🔴 Disabled"
    model_friendly_name = next((name for name, mid in config.AI_MODELS.items() if mid == user.ai_model), "Default")
    await message.answer(f"*Your AI Settings:*\n\n- Status: *{status}*\n- Model: *{model_friendly_name}*", reply_markup=pro_user_menu_keyboard())

@pro_router.message(F.text == "/set_ai_model")
async def choose_ai_model(message: Message, state: FSMContext):
    if not is_pro_user(message.from_user.id):
        await message.answer("❌ You are not a PRO user.")
        return
    await state.set_state(ProStates.set_ai_model)
    await message.answer("🤖 Choose your preferred AI model:", reply_markup=model_selection_keyboard())

@pro_router.message(ProStates.set_ai_model)
async def save_ai_model(message: Message, state: FSMContext):
    uid = str(message.from_user.id)
    model_name = message.text.strip()
    pro_users = load_pro_users()

    if uid not in pro_users:
        await message.answer("❌ You are not a PRO user.")
        return

    if model_name not in config.AI_MODELS:
        await message.answer("❌ Invalid model. Please use the buttons.", reply_markup=pro_user_menu_keyboard())
        await state.clear()
        return

    pro_users[uid].ai_model = config.AI_MODELS[model_name]
    save_pro_users(pro_users)
    await state.clear()
    await message.answer(f"✅ AI model set to: *{model_name}*", reply_markup=pro_user_menu_keyboard())

@pro_router.message(F.text == "/enable_ai")
async def enable_ai_for_pro(message: Message):
    if not is_pro_user(message.from_user.id):
        await message.answer("❌ You are not a PRO user.")
        return
    uid = str(message.from_user.id)
    pro_users = load_pro_users()
    pro_users[uid].ai_enabled = True
    save_pro_users(pro_users)
    await message.answer("🟢 AI access enabled.", reply_markup=pro_user_menu_keyboard())

@pro_router.message(F.text == "/disable_ai")
async def disable_ai_for_pro(message: Message):
    if not is_pro_user(message.from_user.id):
        await message.answer("❌ You are not a PRO user.")
        return
    uid = str(message.from_user.id)
    pro_users = load_pro_users()
    pro_users[uid].ai_enabled = False
    save_pro_users(pro_users)
    await message.answer("🔴 AI access disabled.", reply_markup=pro_user_menu_keyboard())

# Note: I have omitted the other PRO setting handlers for brevity.
# They would need to be updated to use the new ProStates and return the pro_user_menu_keyboard.
# The provided code focuses on the AI model selection feature.
