import sqlite3
from pyrogram import Client, filters
import re
import database
import openai
from config import config

def reload_config():
    global SOURCE_CHANNELS, TARGET_CHANNEL, SPAM_KEYWORDS, SPAM_TYPES, AI_SETTINGS
    SOURCE_CHANNELS = database.get_all_sources()
    TARGET_CHANNEL = database.get_target_chat()
    SPAM_KEYWORDS = database.get_all_spam_keywords()
    SPAM_TYPES = database.get_all_spam_types()
    AI_SETTINGS = database.get_ai_status()

reload_config()

openai.api_key = config.OPENAI_API_KEY
DB_NAME = "userbot.db"
SPAM_TYPES = database.get_all_spam_types()
API_ID = 26265257
API_HASH = "d82296fe28dd3589b08624b04449dbf8"

app = Client("userbot", API_ID, API_HASH)

@app.on_message(filters.command("reload"))
async def reload_handler(client, message):
    reload_config()
    await message.reply_text("✅ Configuration reloaded without restart.")


@app.on_message(filters.command("info"))
async def reload_command(client, message):
    msg = ""
    msg += f"Source channels: {", ".join(SOURCE_CHANNELS)}\n"
    msg += f"Target: {TARGET_CHANNEL}\n"

    await message.reply_text(msg)

@app.on_message(filters.chat(SOURCE_CHANNELS))
async def forward_message(client, message):
    text = message.text or message.caption or ""

    for kw in SPAM_KEYWORDS:
        if str(kw).lower() in text.lower():
            return  

    # 2️⃣ Check spammed types (skip if it matches a blocked type)
    spammed_types = SPAM_TYPES
    if ("text" in spammed_types and message.text) or \
       ("file" in spammed_types and message.document) or \
       ("photo" in spammed_types and message.photo) or \
       ("video" in spammed_types and message.video) or \
       ("location" in spammed_types and message.location) or \
       ("contact" in spammed_types and message.contact):
        return 

    if bool(AI_SETTINGS['enabled']):
        text = await paraphrase(text, AI_SETTINGS['model'])

    if message.photo:
        await client.send_photo(TARGET_CHANNEL, message.photo.file_id, caption=text)
    elif message.text:
        await client.send_message(TARGET_CHANNEL, text)
    elif message.video:
        await client.send_video(TARGET_CHANNEL, message.video.file_id, caption=text)
    elif message.document:
        await client.send_document(TARGET_CHANNEL, message.document.file_id, caption=text)
    elif message.audio:
        await client.send_audio(TARGET_CHANNEL, message.audio.file_id, caption=text)
    elif message.voice:
        await client.send_voice(TARGET_CHANNEL, message.voice.file_id, caption=text)
    elif message.sticker:
        await client.send_sticker(TARGET_CHANNEL, message.sticker.file_id)
    elif message.contact:
        await client.send_contact(TARGET_CHANNEL, phone_number=message.contact.phone_number, first_name=message.contact.first_name)
    elif message.location:
        await client.send_location(TARGET_CHANNEL, latitude=message.location.latitude, longitude=message.location.longitude)
    else:
        await message.forward(TARGET_CHANNEL)


async def paraphrase(text, model: str):
    try:
        prompt = """
Remove all Telegram usernames (e.g., @channelname) and Telegram links (e.g., t.me/channelname) from the message.

Rephrase the message naturally to keep the original meaning but avoid sounding like a direct copy.

If the message is not in English, translate it to English before rephrasing.

At the end of the message, add this tag: @abclegacynews
Return only the final, cleaned, English version with your tag at the end—no commentary or symbols.

        """
        response = openai.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": text}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        print("Error while paraphrasing... ", e)
        return None

app.run()
