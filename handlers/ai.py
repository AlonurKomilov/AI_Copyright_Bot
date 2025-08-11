import logging
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from config import config
import database
from keyboards import main_menu, cancel_keyboard
from handlers.state_groups import Conversation # Import Conversation state
import openai
import httpx
import subprocess
from main import bot
from models.pro_users import load_pro_users

ai_router = Router()
logger = logging.getLogger(__name__)

# Define the daily request limit for free users
FREE_TIER_LIMIT = 5
# Define the maximum number of messages to keep in history
CONVERSATION_HISTORY_LIMIT = 10

def admin_only(handler):
    async def wrapper(message: Message, *args, **kwargs):
        if message.from_user.id not in config.ADMIN_IDS:
            await message.answer("🚫 Access denied.")
            return
        return await handler(message, *args, **kwargs)
    return wrapper

@ai_router.message(F.text == "/clear")
async def clear_conversation_history(message: Message, state: FSMContext):
    """Clears the user's conversation history."""
    await state.clear()
    await message.answer("✅ Your conversation history has been cleared.")

# === AI Enable/Disable (Admin) ===
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

# === Set AI Model (Admin) ===
# ... (admin model setting handlers remain unchanged)

# === Check Balance (Admin) ===
# ... (balance check handler remains unchanged)

# === Restart Userbot (Admin) ===
# ... (restart handler remains unchanged)


# === Handle any text message as a prompt ===
@ai_router.message(F.text)
async def handle_text_message(message: Message, state: FSMContext):
    """Handle all text messages for AI conversation."""
    user_id = message.from_user.id
    ai_status = database.get_ai_status()

    # 1. Check if AI is enabled globally
    if not ai_status or not ai_status['enabled']:
        return

    # 2. Check if the message is a command that should be ignored
    if message.text.startswith('/'):
        # Allow /clear to pass through to its handler
        if message.text != '/clear':
            return

    # 3. Check user's tier and limits
    pro_users = load_pro_users()
    is_pro = str(user_id) in pro_users and pro_users[str(user_id)].active

    if not is_pro:
        request_count = database.check_and_update_user(user_id)
        if request_count >= FREE_TIER_LIMIT:
            await message.answer("ℹ️ You have reached your daily limit of free requests.\nUpgrade to PRO for unlimited access.")
            return

    # 4. Determine which model to use
    model_to_use = ai_status['model']
    if is_pro:
        user_pro_settings = pro_users[str(user_id)]
        if not user_pro_settings.ai_enabled:
            return
        model_to_use = user_pro_settings.ai_model

    # 5. Process the prompt with conversation history
    try:
        await bot.send_chat_action(message.chat.id, 'typing')
        openai.api_key = config.OPENAI_API_KEY

        # Get history from state
        history = await state.get_data()
        messages = history.get("messages", [])

        # Add the new user message
        messages.append({"role": "user", "content": message.text.strip()})

        # Ensure history does not exceed the limit
        if len(messages) > CONVERSATION_HISTORY_LIMIT:
            messages = messages[-CONVERSATION_HISTORY_LIMIT:]

        # System prompt can be the first message if history is empty
        if not any(m['role'] == 'system' for m in messages):
            messages.insert(0, {"role": "system", "content": "You are a helpful assistant."})

        r = openai.chat.completions.create(
            model=model_to_use,
            messages=messages
        )
        response_text = r.choices[0].message.content

        # Add AI response to history
        messages.append({"role": "assistant", "content": response_text})
        await state.update_data(messages=messages)

        await message.answer(response_text)

        if not is_pro:
            database.increment_request_count(user_id)

    except Exception as e:
        logger.error(f"Error processing AI prompt for user {user_id} with model {model_to_use}: {e}")
        await message.answer("❌ An error occurred while processing your request. Please try again later.")
