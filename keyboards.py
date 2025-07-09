from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="ℹ️ Bot Info"), KeyboardButton(text="🎯 Set Target")],
            [KeyboardButton(text="➕ Add Source"), KeyboardButton(text="❌ Remove Source")],
            [KeyboardButton(text="➕ Add Keyword"), KeyboardButton(text="❌ Remove Keyword")],
            [KeyboardButton(text="➕ Add Type"), KeyboardButton(text="❌ Remove Type")],
            [KeyboardButton(text="🟢 Enable AI"), KeyboardButton(text="🔴 Disable AI")],
            [KeyboardButton(text="🤖 Set Model"), KeyboardButton(text="💬 Prompt")],
            [KeyboardButton(text="💰 Balance"), KeyboardButton(text="📄 Save changes")]
        ],
        resize_keyboard=True
    )

def cancel_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="◀️ Cancel")]
        ],
        resize_keyboard=True
    )
