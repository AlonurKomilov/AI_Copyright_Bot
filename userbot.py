import sqlite3
from pyrogram import Client, filters
import re
import database
import openai
from config import config
import base64
import io
import datetime

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

    # AI Processing Logic
    if message.photo and not message.caption and bool(AI_SETTINGS['enabled']):
        # If it's a photo without a caption and AI is on, generate a new one.
        generated_caption = await generate_caption_for_image(message)
        if generated_caption:
            text = generated_caption
    elif bool(AI_SETTINGS['enabled']) and text:
        # For all other message types with text, paraphrase it.
        paraphrased_content = await paraphrase(text, AI_SETTINGS['model'])
        if paraphrased_content:
            text = paraphrased_content

    # Queueing Logic
    content_type = None
    file_id = None
    caption = text

    if message.photo:
        content_type = 'photo'
        file_id = message.photo.file_id
    elif message.video:
        content_type = 'video'
        file_id = message.video.file_id
    elif message.document:
        content_type = 'document'
        file_id = message.document.file_id
    elif message.audio:
        content_type = 'audio'
        file_id = message.audio.file_id
    elif message.voice:
        content_type = 'voice'
        file_id = message.voice.file_id
    elif message.sticker:
        content_type = 'sticker'
        file_id = message.sticker.file_id
    elif message.text:
        content_type = 'text'
        caption = text # Caption is the text itself for text messages
    # Note: 'contact' and 'location' are not handled in this version for simplicity.

    if not content_type:
        return # Skip unsupported message types

    # Calculate scheduled time
    last_scheduled_time = database.get_last_scheduled_time()
    if last_scheduled_time:
        scheduled_for = last_scheduled_time + datetime.timedelta(minutes=30)
    else:
        scheduled_for = datetime.datetime.now() + datetime.timedelta(minutes=5)

    # Add to queue
    database.add_to_queue(
        source_message_id=message.id,
        source_chat_id=message.chat.id,
        content_type=content_type,
        file_id=file_id,
        caption=caption,
        scheduled_for=scheduled_for
    )
    print(f"✅ Message from {message.chat.title} queued for {scheduled_for.strftime('%Y-%m-%d %H:%M:%S')}")


async def generate_caption_for_image(message):
    try:
        # Download image to an in-memory buffer
        image_buffer = io.BytesIO()
        await message.download(in_memory=True, file_name=image_buffer)
        image_buffer.seek(0)

        # Encode image to Base64
        base64_image = base64.b64encode(image_buffer.read()).decode('utf-8')

        prompt_text = "Bu rasmda nima tasvirlanganini qisqa va tushunarli qilib, bir nechta gap bilan tavsiflab ber."

        response = openai.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt_text},
                        {
                            "type": "image_url",
                            "image_url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    ]
                }
            ],
            max_tokens=300
        )
        caption = response.choices[0].message.content
        return f"{caption}\n\n@abclegacynews"
    except Exception as e:
        print(f"Error generating caption for image: {e}")
        return None


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
