from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from config import config
import database
from keyboards import main_menu, cancel_keyboard
from handlers.state_groups import StateGroups
import openai
import httpx
import subprocess

ai_router = Router()

def admin_only(handler):
    async def wrapper(message: Message, *args, **kwargs):
        if message.from_user.id not in config.ADMIN_IDS:
            await message.answer("🚫 Access denied.")
            return
        return await handler(message, *args, **kwargs)
    return wrapper

# === AI Enable/Disable ===
@ai_router.message(F.text == "🟢 Enable AI")
@admin_only
async def enable_ai(message: Message):
    database.enable_ai()
    await message.answer("✅ AI Enabled")

@ai_router.message(F.text == "🔴 Disable AI")
@admin_only
async def disable_ai(message: Message):
    database.disable_ai()
    await message.answer("✅ AI Disabled")

# === Set AI Model ===
@ai_router.message(F.text == "🤖 Set Model")
@admin_only
async def set_model(message: Message, state: FSMContext):
    await state.set_state(StateGroups.SetAiModel.model)
    models = list(config.AI_MODELS.keys())
    await message.answer("Choose model:\n" + "\n".join(models), reply_markup=cancel_keyboard())

@ai_router.message(StateGroups.SetAiModel.model)
@admin_only
async def save_model(message: Message, state: FSMContext):
    model = message.text.strip()
    if model in config.AI_MODELS:
        database.set_ai_model(config.AI_MODELS[model])
        await message.answer("✅ Model set", reply_markup=main_menu())
    else:
        await message.answer("❌ Unknown model")
    await state.clear()

# === Prompt ===
@ai_router.message(F.text == "💬 Prompt")
@admin_only
async def prompt_start(message: Message, state: FSMContext):
    await state.set_state(StateGroups.AiPrompt.text)
    await message.answer("Send your prompt:", reply_markup=cancel_keyboard())

@ai_router.message(StateGroups.AiPrompt.text)
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
        await message.answer("❌ Prompt failed")

# === Check Balance ===
@ai_router.message(F.text == "💰 Balance")
@admin_only
async def check_balance(message: Message):
    try:
        headers = {"Authorization": f"Bearer {config.OPENAI_API_KEY}"}
        async with httpx.AsyncClient() as client:
            r = await client.get("https://api.openai.com/dashboard/billing/credit_grants", headers=headers)
            data = r.json()
            await message.answer(
                f"💰 Balance:\nTotal: ${data['total_granted']:.2f}\nUsed: ${data['total_used']:.2f}\nLeft: ${data['total_available']:.2f}"
            )
    except Exception:
        await message.answer("❌ Failed to retrieve balance info")

# === Restart Userbot ===
@ai_router.message(F.text == "📄 Save changes")
@admin_only
async def save_changes(message: Message):
    try:
        subprocess.run(["sudo", "systemctl", "restart", "ai_userbot.service"], check=True)
        await message.answer("🔄 Userbot restarted")
    except Exception:
        await message.answer("❌ Failed to restart service")
