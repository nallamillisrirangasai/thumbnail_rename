import eventlet
eventlet.monkey_patch()  # Apply monkey patching before any other imports

import asyncio
import threading
import uuid
import redis
from flask import Flask, jsonify
from pyrogram import Client
from pyrogram.types import Message

app = Flask(__name__)

# Connect to Redis (store progress even if the app restarts)
redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)

# Initialize Telegram bot (replace with your own API_ID, API_HASH, BOT_TOKEN)
API_ID = 123456  # Replace with your actual API ID
API_HASH = "your_api_hash"  # Replace with your actual API HASH
BOT_TOKEN = "your_bot_token"  # Replace with your bot token

bot = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

async def progress_task(user_id):
    """Async function to update progress."""
    for i in range(1, 11):
        await asyncio.sleep(1)  # Simulate work
        redis_client.set(user_id, i * 10)  # Store in Redis
    redis_client.set(user_id, 100)  # Completion

@app.route("/start-progress", methods=["POST"])
def start_progress():
    """Starts progress and returns user ID."""
    user_id = str(uuid.uuid4())  # Generate a unique user ID
    redis_client.set(user_id, 0)  # Initialize progress

    loop = asyncio.new_event_loop()
    threading.Thread(target=lambda: asyncio.run(progress_task(user_id)), daemon=True).start()

    return jsonify({"message": "Progress started!", "user_id": user_id})

@app.route("/progress/<user_id>")
def get_progress(user_id):
    """Returns progress for a specific user."""
    progress = redis_client.get(user_id) or "User not found"
    return jsonify({"user_id": user_id, "progress": progress})

@bot.on_message()
async def handle_message(client, message: Message):
    """Handles messages from Telegram users."""
    user_id = str(message.from_user.id)
    redis_client.set(user_id, 0)  # Initialize progress
    asyncio.create_task(progress_task(user_id))
    await message.reply_text(f"Progress started! Track at: /progress/{user_id}")

if __name__ == "__main__":
    bot.start()
    app.run(host="0.0.0.0", port=10000, debug=True)
