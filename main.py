import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import config
from handlers.admin import admin_router
from handlers.ai import ai_router

# Logging config
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

# Bot setup
bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher()

# Register all routers
def register_routers(dp: Dispatcher):
    dp.include_router(admin_router)
    dp.include_router(ai_router)

async def main():
    print("🚀 AI Control Bot starting...")
    register_routers(dp)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Bot stopped.")
