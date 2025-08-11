from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from config import config

def main_menu():
    """For Admin Control Panel"""
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
        keyboard=[[KeyboardButton(text="◀️ Cancel")]],
        resize_keyboard=True
    )

def model_selection_keyboard():
    """Keyboard for PRO users to select an AI model."""
    models = list(config.AI_MODELS.keys())
    # Create a 2-column layout for the buttons
    keyboard = [models[i:i + 2] for i in range(0, len(models), 2)]
    keyboard.append(["◀️ Cancel"]) # Add a cancel button
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=model) for model in row] for row in keyboard],
        resize_keyboard=True,
        one_time_keyboard=True
    )

def pro_user_menu_keyboard():
    """Main menu for PRO users."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="/ai_status"), KeyboardButton(text="/set_ai_model")],
            [KeyboardButton(text="/set_target"), KeyboardButton(text="/add_source")],
            [KeyboardButton(text="/set_filters"), KeyboardButton(text="/set_media_types")],
            [KeyboardButton(text="/enable_ai"), KeyboardButton(text="/disable_ai")]
        ],
        resize_keyboard=True
    )
