import asyncio
import database
from pyrogram import Client
from config import config

# Use the same session as userbot.py to operate as the same user
app = Client("userbot")

async def run_scheduler():
    """
    Checks the database for due posts and sends them to the target channel.
    Runs in a continuous loop.
    """
    print("⏰ Scheduler started, will check for due posts every minute.")
    while True:
        try:
            # We need to get the target channel inside the loop
            # in case it's changed in the admin panel.
            target_channel = database.get_target_chat()
            if not target_channel:
                # print("Scheduler: No target channel set. Waiting...")
                await asyncio.sleep(60)
                continue

            due_posts = database.get_due_posts()
            if due_posts:
                print(f"📬 Found {len(due_posts)} posts to send.")

            async with app:
                for post in due_posts:
                    post_id, content_type, file_id, caption = post
                    try:
                        print(f"  -> Sending post {post_id} of type '{content_type}'...")
                        if content_type == 'text':
                            await app.send_message(target_channel, caption)
                        elif content_type == 'photo':
                            await app.send_photo(target_channel, file_id, caption=caption)
                        elif content_type == 'video':
                            await app.send_video(target_channel, file_id, caption=caption)
                        elif content_type == 'document':
                            await app.send_document(target_channel, file_id, caption=caption)
                        elif content_type == 'audio':
                            await app.send_audio(target_channel, file_id, caption=caption)
                        elif content_type == 'voice':
                            await app.send_voice(target_channel, file_id, caption=caption)
                        elif content_type == 'sticker':
                            await app.send_sticker(target_channel, file_id)

                        # If sending was successful, remove from queue
                        database.remove_from_queue(post_id)
                        print(f"  ✅ Post {post_id} sent and removed from queue.")

                    except Exception as e:
                        print(f"  ❌ Error sending post {post_id}: {e}")
                        # Optionally, you could add logic here to handle failed posts,
                        # e.g., mark them as failed instead of deleting. For now, we just log it.

        except Exception as e:
            print(f"An error occurred in the scheduler loop: {e}")

        # Wait for 60 seconds before the next check
        await asyncio.sleep(60)
