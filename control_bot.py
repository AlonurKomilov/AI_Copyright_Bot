import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from config import config
import database
import subprocess
import openai
import httpx
import os
import sys

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("bot")

bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher()

def admin_only(handler):
    async def wrapper(message: Message, *args, **kwargs):
        if message.from_user.id not in config.ADMIN_IDS:
            await message.answer("🚫 Access denied.")
            return
        return await handler(message, *args, **kwargs)
    return wrapper

# States
class StateGroups:
    class AddSource(StatesGroup): username = State()
    class RemoveSource(StatesGroup): username = State()
    class SetTarget(StatesGroup): username = State()
    class AddSpamKeyword(StatesGroup): keyword = State()
    class RemoveSpamKeyword(StatesGroup): keyword = State()
    class AddSpamType(StatesGroup): type = State()
    class RemoveSpamType(StatesGroup): type = State()
    class SetAiModel(StatesGroup): model = State()
    class AiPrompt(StatesGroup): text = State()

# Core commands
@dp.message(F.text == "/start")
@admin_only
async def start_command(message: Message):
    await message.answer("👋 Welcome to AI Bot Control Panel", reply_markup=main_menu())

@dp.message(F.text == "◀️ Cancel")
@admin_only
async def cancel_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ Cancelled", reply_markup=main_menu())

@dp.message(F.text == "ℹ️ Bot Info")
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
        logger.exception("Bot info error")
        await message.answer("❌ Failed to load bot info.")

# === Source Management ===
@dp.message(F.text == "➕ Add Source")
@admin_only
async def add_source(message: Message, state: FSMContext):
    await state.set_state(StateGroups.AddSource.username)
    await message.answer("Enter @source username:", reply_markup=cancel_keyboard())

@dp.message(StateGroups.AddSource.username)
@admin_only
async def save_source(message: Message, state: FSMContext):
    database.add_source(message.text.strip())
    await state.clear()
    await message.answer("✅ Source added", reply_markup=main_menu())

@dp.message(F.text == "❌ Remove Source")
@admin_only
async def del_source(message: Message, state: FSMContext):
    await state.set_state(StateGroups.RemoveSource.username)
    await message.answer("Enter @source to remove:", reply_markup=cancel_keyboard())

@dp.message(StateGroups.RemoveSource.username)
@admin_only
async def confirm_del_source(message: Message, state: FSMContext):
    database.del_source(message.text.strip())
    await state.clear()
    await message.answer("✅ Source removed", reply_markup=main_menu())

# === Target ===
@dp.message(F.text == "🎯 Set Target")
@admin_only
async def set_target(message: Message, state: FSMContext):
    await state.set_state(StateGroups.SetTarget.username)
    await message.answer("Enter @target chat:", reply_markup=cancel_keyboard())

@dp.message(StateGroups.SetTarget.username)
@admin_only
async def save_target(message: Message, state: FSMContext):
    database.set_target_chat(message.text.strip())
    await state.clear()
    await message.answer("✅ Target set", reply_markup=main_menu())

# === Spam Keyword ===
@dp.message(F.text == "➕ Add Keyword")
@admin_only
async def add_keyword(message: Message, state: FSMContext):
    await state.set_state(StateGroups.AddSpamKeyword.keyword)
    await message.answer("Enter spam keyword:", reply_markup=cancel_keyboard())

@dp.message(StateGroups.AddSpamKeyword.keyword)
@admin_only
async def save_keyword(message: Message, state: FSMContext):
    database.add_spam_keyword(message.text.strip())
    await state.clear()
    await message.answer("✅ Keyword added", reply_markup=main_menu())

@dp.message(F.text == "❌ Remove Keyword")
@admin_only
async def remove_keyword(message: Message, state: FSMContext):
    await state.set_state(StateGroups.RemoveSpamKeyword.keyword)
    await message.answer("Enter keyword to remove:", reply_markup=cancel_keyboard())

@dp.message(StateGroups.RemoveSpamKeyword.keyword)
@admin_only
async def confirm_remove_keyword(message: Message, state: FSMContext):
    database.del_spam_keyword(message.text.strip())
    await state.clear()
    await message.answer("✅ Keyword removed", reply_markup=main_menu())

# === Spam Types ===
@dp.message(F.text == "➕ Add Type")
@admin_only
async def add_type(message: Message, state: FSMContext):
    await state.set_state(StateGroups.AddSpamType.type)
    await message.answer("Enter type (text/photo/video...):", reply_markup=cancel_keyboard())

@dp.message(StateGroups.AddSpamType.type)
@admin_only
async def save_type(message: Message, state: FSMContext):
    database.add_spam_type(message.text.strip().lower())
    await state.clear()
    await message.answer("✅ Type added", reply_markup=main_menu())

@dp.message(F.text == "❌ Remove Type")
@admin_only
async def remove_type(message: Message, state: FSMContext):
    await state.set_state(StateGroups.RemoveSpamType.type)
    await message.answer("Enter type to remove:", reply_markup=cancel_keyboard())

@dp.message(StateGroups.RemoveSpamType.type)
@admin_only
async def confirm_remove_type(message: Message, state: FSMContext):
    database.del_spam_type(message.text.strip().lower())
    await state.clear()
    await message.answer("✅ Type removed", reply_markup=main_menu())

# === AI ===
@dp.message(F.text == "🟢 Enable AI")
@admin_only
async def enable_ai(message: Message):
    database.enable_ai()
    await message.answer("✅ AI Enabled")

@dp.message(F.text == "🔴 Disable AI")
@admin_only
async def disable_ai(message: Message):
    database.disable_ai()
    await message.answer("✅ AI Disabled")

@dp.message(F.text == "🤖 Set Model")
@admin_only
async def set_model(message: Message, state: FSMContext):
    await state.set_state(StateGroups.SetAiModel.model)
    models = list(config.AI_MODELS.keys())
    await message.answer("Choose model:\n" + "\n".join(models), reply_markup=cancel_keyboard())

@dp.message(StateGroups.SetAiModel.model)
@admin_only
async def save_model(message: Message, state: FSMContext):
    model = message.text.strip()
    if model in config.AI_MODELS:
        database.set_ai_model(config.AI_MODELS[model])
        await message.answer("✅ Model set", reply_markup=main_menu())
    else:
        await message.answer("❌ Unknown model")
    await state.clear()

# === Prompt + Balance ===
@dp.message(F.text == "💬 Prompt")
@admin_only
async def prompt_start(message: Message, state: FSMContext):
    await state.set_state(StateGroups.AiPrompt.text)
    await message.answer("Send your prompt:", reply_markup=cancel_keyboard())

@dp.message(StateGroups.AiPrompt.text)
@admin_only
async def run_prompt(message: Message, state: FSMContext):
    await state.clear()
    try:
        openai.api_key = config.OPENAI_API_KEY
        model = database.get_ai_status()['model']
        r = openai.chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": "You are a helpful assistant."},
                      {"role": "user", "content": message.text.strip()}]
        )
        await message.answer(r.choices[0].message.content)
    except Exception:
        logger.exception("Prompt failed")
        await message.answer("❌ Prompt failed")

@dp.message(F.text == "💰 Balance")
@admin_only
async def check_balance(message: Message):
    try:
        headers = {"Authorization": f"Bearer {config.OPENAI_API_KEY}"}
        async with httpx.AsyncClient() as client:
            r = await client.get("https://api.openai.com/dashboard/billing/credit_grants", headers=headers)
            data = r.json()
            await message.answer(f"💰 Balance:\nTotal: ${data['total_granted']:.2f}\nUsed: ${data['total_used']:.2f}\nLeft: ${data['total_available']:.2f}")
    except Exception:
        logger.exception("Balance failed")
        await message.answer("❌ Failed to get balance")

@dp.message(F.text == "🔄 Restart Bot")
@admin_only
async def restart_bot(message: Message):
    """Gracefully restarts the bot."""
    try:
        await message.answer("🤖 Restarting bot...")
        # This replaces the current process with a new one
        os.execv(sys.executable, ['python'] + sys.argv)
    except Exception as e:
        logger.exception("Failed to restart bot")
        await message.answer(f"❌ Failed to restart bot: {e}")

# Keyboards
def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="ℹ️ Bot Info"), KeyboardButton(text="🎯 Set Target")],
            [KeyboardButton(text="➕ Add Source"), KeyboardButton(text="❌ Remove Source")],
            [KeyboardButton(text="➕ Add Keyword"), KeyboardButton(text="❌ Remove Keyword")],
            [KeyboardButton(text="➕ Add Type"), KeyboardButton(text="❌ Remove Type")],
            [KeyboardButton(text="🟢 Enable AI"), KeyboardButton(text="🔴 Disable AI")],
            [KeyboardButton(text="🤖 Set Model"), KeyboardButton(text="💬 Prompt")],
            [KeyboardButton(text="💰 Balance"), KeyboardButton(text="🔄 Restart Bot")]
        ],
        resize_keyboard=True
    )

def cancel_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="◀️ Cancel")]], resize_keyboard=True
    )

async def main():
    print("🚀 Bot starting...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
