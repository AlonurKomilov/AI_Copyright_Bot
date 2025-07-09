import logging
from aiogram import BaseMiddleware
from aiogram.types import Message, Update
from typing import Callable, Awaitable, Dict, Any
from config import config

logger = logging.getLogger("middleware")

class LoggingMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        user = event.from_user
        username = f"@{user.username}" if user.username else "NoUsername"
        user_id = user.id
        text = event.text or ""

        if user_id not in config.ADMIN_IDS:
            logger.warning(f"[UNAUTHORIZED] ❌ {username} ({user_id}) tried: {text}")
        else:
            logger.info(f"[AUTHORIZED] ✅ {username} ({user_id}) sent: {text}")

        return await handler(event, data)
