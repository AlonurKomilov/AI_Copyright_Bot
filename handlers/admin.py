import os
import sys
import logging
import subprocess
import openai
import httpx

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from config import config
import database
from keyboards import main_menu, cancel_keyboard
from handlers.state_groups import AdminStates  # Corrected import
from models.pro_users import load_pro_users

admin_router = Router()
pro_users = load_pro_users()
logger = logging.getLogger(__name__)

# --- Helper Functions ---

async def is_admin(user_id: int):
    return user_id in config.ADMIN_IDS

async def show_main_menu(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "👋 Welcome to AI Bot Control Panel", reply_markup=main_menu()
    )

# --- Command Handlers ---

@admin_router.message(F.text == "/start")
async def start_command(message: Message, state: FSMContext):
    if not await is_admin(message.from_user.id):
        return await message.answer("🚫 Access denied.")
    await show_main_menu(message, state)

# --- Callback Handlers for Main Menu ---

@admin_router.callback_query(F.data == "admin:cancel")
async def cancel_handler(callback: CallbackQuery, state: FSMContext):
    if not await is_admin(callback.from_user.id):
        return await callback.answer("🚫 Access denied.", show_alert=True)

    await state.clear()
    await callback.message.edit_text(
        "👋 Welcome to AI Bot Control Panel", reply_markup=main_menu()
    )
    await callback.answer("❌ Action cancelled.")

@admin_router.callback_query(F.data == "admin:info")
async def bot_info_callback(callback: CallbackQuery):
    if not await is_admin(callback.from_user.id):
        return await callback.answer("🚫 Access denied.", show_alert=True)
    try:
        ai = database.get_ai_status()
        sources = database.get_all_sources()
        keywords = database.get_all_spam_keywords()
        types = database.get_all_spam_types()

        msg = [
            f"📡 Sources: {', '.join(sources) if sources else 'None'}",
            f"🎯 Target: {database.get_target_chat() or 'Not set'}",
            f"🧾 Keywords: {', '.join(keywords) if keywords else 'None'}",
            f"🧱 Types: {', '.join(types) if types else 'None'}",
            f"🤖 Model: {ai.get('model', 'Not set')}",
            "🟢 AI is ON" if ai.get('enabled') else "🔴 AI is OFF"
        ]
        await callback.message.answer("\n".join(msg), parse_mode=None)
        await callback.answer()
    except Exception as e:
        logger.error(f"Failed to load bot info: {e}")
        await callback.answer("❌ Failed to load bot info.", show_alert=True)

# --- State-based Callback Handlers ---

@admin_router.callback_query(F.data == "admin:add_source")
async def add_source_callback(callback: CallbackQuery, state: FSMContext):
    if not await is_admin(callback.from_user.id):
        return await callback.answer("🚫 Access denied.", show_alert=True)
    await state.set_state(AdminStates.add_source)
    await callback.message.edit_text("Enter @source username:", reply_markup=cancel_keyboard())
    await callback.answer()

@admin_router.callback_query(F.data == "admin:remove_source")
async def del_source_callback(callback: CallbackQuery, state: FSMContext):
    if not await is_admin(callback.from_user.id):
        return await callback.answer("🚫 Access denied.", show_alert=True)
    await state.set_state(AdminStates.remove_source)
    await callback.message.edit_text("Enter @source to remove:", reply_markup=cancel_keyboard())
    await callback.answer()

@admin_router.callback_query(F.data == "admin:set_target")
async def set_target_callback(callback: CallbackQuery, state: FSMContext):
    if not await is_admin(callback.from_user.id):
        return await callback.answer("🚫 Access denied.", show_alert=True)
    await state.set_state(AdminStates.set_target)
    await callback.message.edit_text("Enter @target chat:", reply_markup=cancel_keyboard())
    await callback.answer()

@admin_router.callback_query(F.data == "admin:add_keyword")
async def add_keyword_callback(callback: CallbackQuery, state: FSMContext):
    if not await is_admin(callback.from_user.id):
        return await callback.answer("🚫 Access denied.", show_alert=True)
    await state.set_state(AdminStates.add_spam_keyword)
    await callback.message.edit_text("Enter spam keyword:", reply_markup=cancel_keyboard())
    await callback.answer()

@admin_router.callback_query(F.data == "admin:remove_keyword")
async def remove_keyword_callback(callback: CallbackQuery, state: FSMContext):
    if not await is_admin(callback.from_user.id):
        return await callback.answer("🚫 Access denied.", show_alert=True)
    await state.set_state(AdminStates.remove_spam_keyword)
    await callback.message.edit_text("Enter keyword to remove:", reply_markup=cancel_keyboard())
    await callback.answer()

@admin_router.callback_query(F.data == "admin:add_type")
async def add_type_callback(callback: CallbackQuery, state: FSMContext):
    if not await is_admin(callback.from_user.id):
        return await callback.answer("🚫 Access denied.", show_alert=True)
    await state.set_state(AdminStates.add_spam_type)
    await callback.message.edit_text("Enter type (text/photo/video...):", reply_markup=cancel_keyboard())
    await callback.answer()

@admin_router.callback_query(F.data == "admin:remove_type")
async def remove_type_callback(callback: CallbackQuery, state: FSMContext):
    if not await is_admin(callback.from_user.id):
        return await callback.answer("🚫 Access denied.", show_alert=True)
    await state.set_state(AdminStates.remove_spam_type)
    await callback.message.edit_text("Enter type to remove:", reply_markup=cancel_keyboard())
    await callback.answer()

# --- Message Handlers for States ---

@admin_router.message(AdminStates.add_source)
async def save_source_state(message: Message, state: FSMContext):
    if not await is_admin(message.from_user.id): return
    database.add_source(message.text.strip())
    await message.answer("✅ Source added")
    await show_main_menu(message, state)

@admin_router.message(AdminStates.remove_source)
async def confirm_del_source_state(message: Message, state: FSMContext):
    if not await is_admin(message.from_user.id): return
    database.del_source(message.text.strip())
    await message.answer("✅ Source removed")
    await show_main_menu(message, state)

@admin_router.message(AdminStates.set_target)
async def save_target_state(message: Message, state: FSMContext):
    if not await is_admin(message.from_user.id): return
    database.set_target_chat(message.text.strip())
    await message.answer("✅ Target set")
    await show_main_menu(message, state)

@admin_router.message(AdminStates.add_spam_keyword)
async def save_keyword_state(message: Message, state: FSMContext):
    if not await is_admin(message.from_user.id): return
    database.add_spam_keyword(message.text.strip())
    await message.answer("✅ Keyword added")
    await show_main_menu(message, state)

@admin_router.message(AdminStates.remove_spam_keyword)
async def confirm_remove_keyword_state(message: Message, state: FSMContext):
    if not await is_admin(message.from_user.id): return
    database.del_spam_keyword(message.text.strip())
    await message.answer("✅ Keyword removed")
    await show_main_menu(message, state)

@admin_router.message(AdminStates.add_spam_type)
async def save_type_state(message: Message, state: FSMContext):
    if not await is_admin(message.from_user.id): return
    database.add_spam_type(message.text.strip().lower())
    await message.answer("✅ Type added")
    await show_main_menu(message, state)

@admin_router.message(AdminStates.remove_spam_type)
async def confirm_remove_type_state(message: Message, state: FSMContext):
    if not await is_admin(message.from_user.id): return
    database.del_spam_type(message.text.strip().lower())
    await message.answer("✅ Type removed")
    await show_main_menu(message, state)

# --- Simple Action Callback Handlers ---

@admin_router.callback_query(F.data == "admin:enable_ai")
async def enable_ai_callback(callback: CallbackQuery):
    if not await is_admin(callback.from_user.id):
        return await callback.answer("🚫 Access denied.", show_alert=True)
    database.enable_ai()
    await callback.answer("✅ AI Enabled", show_alert=True)

@admin_router.callback_query(F.data == "admin:disable_ai")
async def disable_ai_callback(callback: CallbackQuery):
    if not await is_admin(callback.from_user.id):
        return await callback.answer("🚫 Access denied.", show_alert=True)
    database.disable_ai()
    await callback.answer("✅ AI Disabled", show_alert=True)

@admin_router.callback_query(F.data == "admin:restart")
async def restart_bot_callback(callback: CallbackQuery):
    if not await is_admin(callback.from_user.id):
        return await callback.answer("🚫 Access denied.", show_alert=True)
    try:
        await callback.message.edit_text("🤖 Restarting bot...")
        await callback.answer()
        os.execv(sys.executable, ['python'] + sys.argv)
    except Exception as e:
        logger.exception("Failed to restart bot")
        await callback.message.answer(f"❌ Failed to restart bot: {e}")

# --- AI-related Callback Handlers ---

@admin_router.callback_query(F.data == "admin:set_model")
async def set_model_callback(callback: CallbackQuery, state: FSMContext):
    if not await is_admin(callback.from_user.id):
        return await callback.answer("🚫 Access denied.", show_alert=True)
    await state.set_state(AdminStates.set_ai_model)
    models = list(config.AI_MODELS.keys())
    await callback.message.edit_text(
        "Choose model:\n" + "\n".join(models), reply_markup=cancel_keyboard()
    )
    await callback.answer()

@admin_router.message(AdminStates.set_ai_model)
async def save_model_state(message: Message, state: FSMContext):
    if not await is_admin(message.from_user.id): return
    model_key = message.text.strip()
    if model_key in config.AI_MODELS:
        database.set_ai_model(config.AI_MODELS[model_key])
        await message.answer(f"✅ Model set to {model_key}")
    else:
        await message.answer("❌ Unknown model")
    await show_main_menu(message, state)


@admin_router.callback_query(F.data == "admin:prompt")
async def prompt_callback(callback: CallbackQuery, state: FSMContext):
    if not await is_admin(callback.from_user.id):
        return await callback.answer("🚫 Access denied.", show_alert=True)
    await state.set_state(AdminStates.ai_prompt)
    await callback.message.edit_text("Send your prompt:", reply_markup=cancel_keyboard())
    await callback.answer()

@admin_router.message(AdminStates.ai_prompt)
async def run_prompt_state(message: Message, state: FSMContext):
    if not await is_admin(message.from_user.id): return
    await state.clear()
    await message.answer("⏳ Running prompt...")
    try:
        openai.api_key = config.OPENAI_API_KEY
        model = database.get_ai_status()['model']
        r = await openai.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": message.text.strip()},
            ],
            timeout=120.0,
        )
        await message.answer(r.choices[0].message.content)
    except Exception as e:
        logger.exception("Prompt failed")
        await message.answer(f"❌ Prompt failed: {e}")
    finally:
        await show_main_menu(message, state)


@admin_router.callback_query(F.data == "admin:balance")
async def check_balance_callback(callback: CallbackQuery):
    if not await is_admin(callback.from_user.id):
        return await callback.answer("🚫 Access denied.", show_alert=True)
    try:
        await callback.answer("💰 Checking balance...")
        headers = {"Authorization": f"Bearer {config.OPENAI_API_KEY}"}
        async with httpx.AsyncClient() as client:
            r = await client.get(
                "https://api.openai.com/dashboard/billing/credit_grants", headers=headers
            )
            r.raise_for_status()
            data = r.json()
            await callback.message.answer(
                f"💰 Balance:\n"
                f"Total: ${data.get('total_granted', 0):.2f}\n"
                f"Used: ${data.get('total_used', 0):.2f}\n"
                f"Left: ${data.get('total_available', 0):.2f}"
            )
    except Exception as e:
        logger.exception("Balance check failed")
        await callback.message.answer(f"❌ Failed to get balance: {e}")

# Note: "/manage_pro" handler is not included as it's a text command
# and doesn't fit the inline keyboard flow. It can be kept as is.
