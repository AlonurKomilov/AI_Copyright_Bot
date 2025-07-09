import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(override=True)

class Config:
    # Telegram API
    API_ID = int(os.getenv("API_ID", "12345"))
    API_HASH = os.getenv("API_HASH", "your_api_hash")
    BOT_TOKEN = os.getenv("BOT_TOKEN", "your_bot_token")

    # Userbot session name
    USERBOT_SESSION = os.getenv("USERBOT_SESSION", "userbot")

    # Database
    DATABASE_NAME = os.getenv("DATABASE_NAME", "userbot.db")

    # OpenAI API
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    # Supported AI models (must match OpenAI format)
    AI_MODELS = {
        "GPT-3.5 Turbo": "gpt-3.5-turbo",
        "GPT-4": "gpt-4",
        "GPT-4 Turbo": "gpt-4-turbo-preview"
    }

    # Default model
    DEFAULT_AI_MODEL = AI_MODELS["GPT-3.5 Turbo"]

    # Admins
    ADMIN_IDS = list(map(int, os.getenv("ADMIN_IDS", "").split(",")))  # comma-separated

config = Config()
