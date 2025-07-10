from aiogram import Router
from aiogram.types import Message
import httpx
from config import config

payment_router = Router()

# Stripe backend endpoint for creating a checkout session
STRIPE_CREATE_SESSION_URL = "http://localhost:8000/create-checkout-session"  # Replace with your deployed backend URL

@payment_router.message(commands=["buy_pro"])
async def handle_buy_pro_command(message: Message):
    try:
        telegram_id = message.from_user.id

        async with httpx.AsyncClient() as client:
            response = await client.post(
                STRIPE_CREATE_SESSION_URL,
                json={"telegram_id": telegram_id}
            )

        if response.status_code == 200:
            data = response.json()
            checkout_url = data.get("url")

            if checkout_url:
                await message.answer(
                    f"🛍️ To upgrade to PRO, click the link below:\n{checkout_url}"
                )
            else:
                await message.answer("❌ Failed to generate checkout URL.")
        else:
            await message.answer("⚠️ Failed to create Stripe session.")
    except Exception as e:
        await message.answer("❗ An unexpected error occurred while initiating payment.")
