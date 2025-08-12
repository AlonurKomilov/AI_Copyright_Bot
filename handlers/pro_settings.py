from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from models.pro_users import load_pro_user, save_pro_user
from keyboards import model_selection_keyboard, pro_user_menu_keyboard, cancel_keyboard
from config import config
from datetime import datetime

pro_router = Router()

class ProStates(StatesGroup):
    set_target = State()
    add_source = State()
    remove_source = State()
    set_filters = State()
    set_media_types = State()
    set_ai_model = State()

def is_pro_user(user_id: int) -> bool:
    pro_user = load_pro_user(user_id)
    if not pro_user:
        return False
    # Also check if the subscription is active
    return pro_user.active and datetime.strptime(pro_user.expires_at, "%Y-%m-%d").date() >= datetime.utcnow().date()

@pro_router.message(F.text == "◀️ Cancel", ProStates)
async def cancel_pro_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ Action cancelled.", reply_markup=pro_user_menu_keyboard())

@pro_router.message(Command("pro"))
async def pro_menu(message: Message):
    if not is_pro_user(message.from_user.id):
        await message.answer("❌ You are not a PRO user. Use /activate_license or /buy_pro.")
        return
    await message.answer("💎 *PRO Menu*", reply_markup=pro_user_menu_keyboard())

@pro_router.message(Command("set_target"))
async def start_set_target(message: Message, state: FSMContext):
    if not is_pro_user(message.from_user.id):
        return
    await state.set_state(ProStates.set_target)
    await message.answer("📥 Send your target channel username (e.g. @mychannel):", reply_markup=cancel_keyboard())

@pro_router.message(ProStates.set_target)
async def save_target_channel(message: Message, state: FSMContext):
    user_id = message.from_user.id
    pro_user = load_pro_user(user_id)
    if not pro_user:
        return
    pro_user.target_channel = message.text.strip()
    save_pro_user(pro_user)
    await state.clear()
    await message.answer(f"✅ Target channel set to: {pro_user.target_channel}", reply_markup=pro_user_menu_keyboard())

# You can add other handlers for add_source, set_filters etc. in a similar fashion.
# Example for a setting: AI Status
@pro_router.message(Command("ai_status"))
async def ai_status(message: Message):
    if not is_pro_user(message.from_user.id):
        return
    pro_user = load_pro_user(message.from_user.id)
    if not pro_user:
        return

    status = "🟢 Enabled" if pro_user.ai_enabled else "🔴 Disabled"
    model_name = pro_user.ai_model
    await message.answer(f"*Your AI Settings:*\n\n- Status: *{status}*\n- Model: *{model_name}*", reply_markup=pro_user_menu_keyboard())

@pro_router.message(Command("enable_ai"))
async def enable_ai(message: Message):
    if not is_pro_user(message.from_user.id):
        return
    pro_user = load_pro_user(message.from_user.id)
    if not pro_user:
        return
    pro_user.ai_enabled = True
    save_pro_user(pro_user)
    await message.answer("🟢 AI processing enabled.", reply_markup=pro_user_menu_keyboard())

@pro_router.message(Command("disable_ai"))
async def disable_ai(message: Message):
    if not is_pro_user(message.from_user.id):
        return
    pro_user = load_pro_user(message.from_user.id)
    if not pro_user:
        return
    pro_user.ai_enabled = False
    save_pro_user(pro_user)
    await message.answer("🔴 AI processing disabled.", reply_markup=pro_user_menu_keyboard())

@pro_router.message(Command("set_ai_model"))
async def start_set_ai_model(message: Message, state: FSMContext):
    if not is_pro_user(message.from_user.id):
        return
    await state.set_state(ProStates.set_ai_model)
    await message.answer("🤖 Choose your preferred AI model:", reply_markup=model_selection_keyboard())

@pro_router.message(ProStates.set_ai_model)
async def save_ai_model(message: Message, state: FSMContext):
    user_id = message.from_user.id
    pro_user = load_pro_user(user_id)
    if not pro_user:
        return

    model_friendly_name = message.text.strip()
    # Assuming config.AI_MODELS maps friendly names to model IDs
    model_id = config.AI_MODELS.get(model_friendly_name)

    if not model_id:
        await message.answer("❌ Invalid model selected. Please use the keyboard.", reply_markup=pro_user_menu_keyboard())
        await state.clear()
        return

    pro_user.ai_model = model_id
    save_pro_user(pro_user)
    await state.clear()
    await message.answer(f"✅ AI model set to: *{model_friendly_name}*", reply_markup=pro_user_menu_keyboard())
