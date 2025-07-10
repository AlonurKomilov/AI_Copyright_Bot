# Stripe integration using FastAPI for your Telegram bot backend

import stripe
from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
import os

# Setup Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")  # your secret key from stripe dashboard
YOUR_DOMAIN = os.getenv("STRIPE_SUCCESS_URL", "https://yourdomain.com")

# FastAPI app instance
app = FastAPI()

# Optional: manage license activations
active_licenses = set()

class CreateCheckoutSessionRequest(BaseModel):
    telegram_id: int

@app.post("/create-checkout-session")
async def create_checkout_session(data: CreateCheckoutSessionRequest):
    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': 'AI Bot Pro Access',
                        },
                        'unit_amount': 500,  # $5.00 (500 cents)
                    },
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url=f"{YOUR_DOMAIN}/success?telegram_id={data.telegram_id}",
            cancel_url=f"{YOUR_DOMAIN}/cancel",
            metadata={"telegram_id": str(data.telegram_id)}
        )
        return {"url": checkout_session.url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    # Handle the checkout.session.completed event
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        telegram_id = session["metadata"].get("telegram_id")
        # Add to active licenses
        if telegram_id:
            active_licenses.add(int(telegram_id))
            print(f"✅ Telegram ID {telegram_id} upgraded to PRO")

    return {"status": "success"}

# Utility
@app.get("/is_pro/{telegram_id}")
async def is_pro_user(telegram_id: int):
    return {"pro": telegram_id in active_licenses}
