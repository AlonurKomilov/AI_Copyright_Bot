import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config import config
from handlers.admin import admin_router
from handlers.ai import ai_router
from handlers.license import license_router
from handlers.pro_settings import pro_router

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

# Bot and dispatcher setup
bot = Bot(token=config.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())

# Register all routers
def register_routers(dispatcher: Dispatcher):
    dispatcher.include_router(admin_router)
    dispatcher.include_router(ai_router)
    dispatcher.include_router(license_router)
    dispatcher.include_router(pro_router)

from scheduler import run_scheduler

async def main():
    print("🚀 Bot is starting...")
    register_routers(dp)

    # Start the scheduler as a background task
    asyncio.create_task(run_scheduler())

    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("❌ Bot stopped.")
