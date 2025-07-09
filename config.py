import os
from dotenv import load_dotenv

class Config:
    # Telegram API
    load_dotenv(override=True)
    API_ID = int(os.getenv("API_ID", 12345))
    API_HASH = os.getenv("API_HASH", "your_api_hash")
    BOT_TOKEN = os.getenv("BOT_TOKEN", "your_bot_token")
    
    # Database
    DATABASE_NAME = "userbot.db"
    
    # OpenAI
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    AI_MODELS = {
        "GPT-3.5 Turbo": "gpt-3.5-turbo",
        "GPT-4": "gpt-4",
        "GPT-4 Turbo": "gpt-4-turbo-preview"
    }
    DEFAULT_AI_MODEL = "gpt-3.5-turbo"
    
    # Userbot
    USERBOT_SESSION = "userbot"

config = Config()