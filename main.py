import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config import config
from handlers.admin import admin_router
from handlers.ai import ai_router
from handlers.license import (
    license_router,
    auto_revoke_expired_pros,
    notify_expiring_pro_users,
    notify_expired_pro_users
)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

# Bot and dispatcher setup
bot = Bot(token=config.BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())

# Register all routers
def register_routers(dispatcher: Dispatcher):
    dispatcher.include_router(admin_router)
    dispatcher.include_router(ai_router)
    dispatcher.include_router(license_router)

async def main():
    print("🚀 Bot is starting...")
    register_routers(dp)

    # Launch background tasks
    asyncio.create_task(auto_revoke_expired_pros())
    asyncio.create_task(notify_expiring_pro_users(bot))
    asyncio.create_task(notify_expired_pro_users(bot))

    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("❌ Bot stopped.")
