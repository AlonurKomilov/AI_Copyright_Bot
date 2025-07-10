# handlers/web.py

from aiogram import Router, F
from aiogram.types import Message
from bs4 import BeautifulSoup
import requests

web_router = Router()

NEWS_URL = "https://kun.uz/news"

@web_router.message(F.text == "/scrape_news")
async def handle_scrape_news(message: Message):
    try:
        response = requests.get(NEWS_URL, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Custom selector based on site structure
        articles = soup.select(".news-title")
        if not articles:
            await message.answer("❌ No articles found.")
            return

        news_titles = [a.get_text(strip=True) for a in articles[:5]]
        text = "\n\n".join(f"📰 {title}" for title in news_titles)
        await message.answer(f"Top headlines from Kun.uz:\n\n{text}")

    except Exception as e:
        print("Web scraping error:", e)
        await message.answer("⚠️ Failed to fetch news from Kun.uz.")
