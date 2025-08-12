from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from config import config


def main_menu():
    """For Admin Control Panel - Inline Version"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="ℹ️ Bot Info", callback_data="admin:info"),
                InlineKeyboardButton(text="🎯 Set Target", callback_data="admin:set_target"),
            ],
            [
                InlineKeyboardButton(text="➕ Add Source", callback_data="admin:add_source"),
                InlineKeyboardButton(
                    text="❌ Remove Source", callback_data="admin:remove_source"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="➕ Add Keyword", callback_data="admin:add_keyword"
                ),
                InlineKeyboardButton(
                    text="❌ Remove Keyword", callback_data="admin:remove_keyword"
                ),
            ],
            [
                InlineKeyboardButton(text="➕ Add Type", callback_data="admin:add_type"),
                InlineKeyboardButton(
                    text="❌ Remove Type", callback_data="admin:remove_type"
                ),
            ],
            [
                InlineKeyboardButton(text="🟢 Enable AI", callback_data="admin:enable_ai"),
                InlineKeyboardButton(
                    text="🔴 Disable AI", callback_data="admin:disable_ai"
                ),
            ],
            [
                InlineKeyboardButton(text="🤖 Set Model", callback_data="admin:set_model"),
                InlineKeyboardButton(text="💬 Prompt", callback_data="admin:prompt"),
            ],
            [
                InlineKeyboardButton(text="💰 Balance", callback_data="admin:balance"),
                InlineKeyboardButton(text="🔄 Restart Bot", callback_data="admin:restart"),
            ],
        ]
    )


def cancel_keyboard():
    """Inline keyboard with a cancel button."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="◀️ Cancel", callback_data="admin:cancel")]
        ]
    )


def model_selection_keyboard():
    """Keyboard for PRO users to select an AI model."""
    models = list(config.AI_MODELS.keys())
    # Create a 2-column layout for the buttons
    keyboard = [models[i : i + 2] for i in range(0, len(models), 2)]
    keyboard.append(["◀️ Cancel"])  # Add a cancel button
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=model) for model in row] for row in keyboard],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def pro_user_menu_keyboard():
    """Main menu for PRO users."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="/ai_status"), KeyboardButton(text="/set_ai_model")],
            [KeyboardButton(text="/set_target"), KeyboardButton(text="/add_source")],
            [
                KeyboardButton(text="/set_filters"),
                KeyboardButton(text="/set_media_types"),
            ],
            [KeyboardButton(text="/enable_ai"), KeyboardButton(text="/disable_ai")],
        ],
        resize_keyboard=True,
    )
