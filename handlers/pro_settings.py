# handlers/pro_settings.py

from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from models.pro_users import load_pro_users, save_pro_users

pro_router = Router()
pro_users = load_pro_users()

class SetTarget(StatesGroup):
    channel = State()

class AddSource(StatesGroup):
    channel = State()

class SetFilters(StatesGroup):
    filters = State()

class SetMediaTypes(StatesGroup):
    types = State()

class SetAIModel(StatesGroup):
    model = State()

@pro_router.message(F.text == "/set_target")
async def start_set_target(message: Message, state: FSMContext):
    await state.set_state(SetTarget.channel)
    await message.answer("📥 Send your target channel username (e.g. @mychannel):")

@pro_router.message(SetTarget.channel)
async def save_target_channel(message: Message, state: FSMContext):
    uid = str(message.from_user.id)
    channel = message.text.strip()
    if uid not in pro_users:
        await message.answer("❌ You are not a PRO user.")
        return
    pro_users[uid].target_channel = channel
    save_pro_users(pro_users)
    await state.clear()
    await message.answer(f"✅ Target channel set to {channel}")

@pro_router.message(F.text == "/add_source")
async def start_add_source(message: Message, state: FSMContext):
    await state.set_state(AddSource.channel)
    await message.answer("➕ Send the source channel username to add:")

@pro_router.message(AddSource.channel)
async def save_source_channel(message: Message, state: FSMContext):
    uid = str(message.from_user.id)
    channel = message.text.strip()
    if uid not in pro_users:
        await message.answer("❌ You are not a PRO user.")
        return
    if channel not in pro_users[uid].source_channels:
        pro_users[uid].source_channels.append(channel)
        save_pro_users(pro_users)
    await state.clear()
    await message.answer(f"✅ Added {channel} to your source list.")

@pro_router.message(F.text == "/set_filters")
async def set_filters(message: Message, state: FSMContext):
    await state.set_state(SetFilters.filters)
    await message.answer("🔤 Send keywords (comma separated):")

@pro_router.message(SetFilters.filters)
async def save_filters(message: Message, state: FSMContext):
    uid = str(message.from_user.id)
    if uid not in pro_users:
        await message.answer("❌ You are not a PRO user.")
        return
    filters = [x.strip() for x in message.text.split(",") if x.strip()]
    pro_users[uid].filters = filters
    save_pro_users(pro_users)
    await state.clear()
    await message.answer(f"✅ Filters saved: {', '.join(filters)}")

@pro_router.message(F.text == "/set_media_types")
async def set_media_types(message: Message, state: FSMContext):
    await state.set_state(SetMediaTypes.types)
    await message.answer("📁 Send media types (e.g. text, photo, video, file, contact, location) — comma separated:")

@pro_router.message(SetMediaTypes.types)
async def save_media_types(message: Message, state: FSMContext):
    uid = str(message.from_user.id)
    if uid not in pro_users:
        await message.answer("❌ You are not a PRO user.")
        return
    types = [x.strip().lower() for x in message.text.split(",") if x.strip()]
    allowed = ["text", "photo", "video", "file", "location", "contact"]
    if not all(t in allowed for t in types):
        await message.answer("❌ Invalid media types.")
        return
    pro_users[uid].media_types = types
    save_pro_users(pro_users)
    await state.clear()
    await message.answer(f"✅ Media types saved: {', '.join(types)}")

@pro_router.message(F.text == "/ai_status")
async def ai_status(message: Message):
    uid = str(message.from_user.id)
    if uid not in pro_users:
        await message.answer("❌ You are not a PRO user.")
        return
    user = pro_users[uid]
    status = "🟢 Enabled" if user.ai_enabled else "🔴 Disabled"
    await message.answer(f"AI status: {status}\nModel: {user.ai_model}")

@pro_router.message(F.text == "/set_ai_model")
async def choose_ai_model(message: Message, state: FSMContext):
    await state.set_state(SetAIModel.model)
    await message.answer("🤖 Available models: GPT-3.5 Turbo, GPT-4\nSend model name:")

@pro_router.message(SetAIModel.model)
async def save_ai_model(message: Message, state: FSMContext):
    uid = str(message.from_user.id)
    model = message.text.strip()
    if uid not in pro_users:
        await message.answer("❌ You are not a PRO user.")
        return
    if model not in ["GPT-3.5 Turbo", "GPT-4"]:
        await message.answer("❌ Invalid model. Available: GPT-3.5 Turbo, GPT-4")
        return
    pro_users[uid].ai_model = model
    save_pro_users(pro_users)
    await state.clear()
    await message.answer(f"✅ AI model set to: {model}")

@pro_router.message(F.text == "/disable_ai")
async def disable_ai(message: Message):
    uid = str(message.from_user.id)
    if uid not in pro_users:
        await message.answer("❌ You are not a PRO user.")
        return
    pro_users[uid].ai_enabled = False
    save_pro_users(pro_users)
    await message.answer("🔴 AI access disabled.")
