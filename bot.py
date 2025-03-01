from pyrogram import Client, filters, idle
import os
from flask import Flask
from threading import Thread

# Load environment variables
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Initialize Pyrogram Client
app = Client("bulk_thumbnail_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Flask app to keep Render alive
web_app = Flask(_name_)

@web_app.route('/')
def home():
    return "Bot is running!"

# Directory to save thumbnails and keywords
THUMB_DIR = "thumbnails"
KEYWORDS_FILE = "keywords.txt"
os.makedirs(THUMB_DIR, exist_ok=True)

# Load user keywords from file
user_keywords = {}

if os.path.exists(KEYWORDS_FILE):
    with open(KEYWORDS_FILE, "r") as f:
        for line in f:
            user_id, keyword = line.strip().split(":", 1)
            user_keywords[int(user_id)] = keyword

# Save user keywords
def save_keywords():
    with open(KEYWORDS_FILE, "w") as f:
        for user_id, keyword in user_keywords.items():
            f.write(f"{user_id}:{keyword}\n")

# Command to set a custom default keyword
@app.on_message(filters.command("set_default"))
async def set_default_keyword(client, message):
    if len(message.command) < 2:
        await message.reply_text("⚠ Please provide a default keyword. Example: /set_default @Animes2u")
        return

    keyword = " ".join(message.command[1:])
    user_keywords[message.from_user.id] = keyword
    save_keywords()
    await message.reply_text(f"✅ Default keyword set to: {keyword}")

# Command to set a thumbnail
@app.on_message(filters.command("set_thumb") & filters.photo)
async def set_thumbnail(client, message):
    file_path = os.path.join(THUMB_DIR, f"{message.from_user.id}.jpg")
    await client.download_media(message.photo, file_name=file_path)
    await message.reply_text("✅ Thumbnail saved successfully!")

# Command to change the thumbnail and rename the file
@app.on_message(filters.document)
async def change_thumbnail(client, message):
    thumb_path = os.path.join(THUMB_DIR, f"{message.from_user.id}.jpg")
    default_keyword = user_keywords.get(message.from_user.id, "Default")

    if not os.path.exists(thumb_path):
        await message.reply_text("⚠ No thumbnail found! Send an image with /set_thumb to set one.")
        return

    await message.reply_text("🔄 Changing thumbnail and renaming file...")

    # Download the document
    file_path = await message.download()
    
    if not file_path:
        await message.reply_text("❌ Failed to download file.")
        return
    
    try:
        # Rename the file by adding the user-defined default keyword
        dir_name, original_filename = os.path.split(file_path)
        new_filename = f"{default_keyword} {original_filename}"
        new_file_path = os.path.join(dir_name, new_filename)
        os.rename(file_path, new_file_path)

        # Send the renamed document with the new thumbnail
        await client.send_document(
            chat_id=message.chat.id,
            document=new_file_path,
            thumb=thumb_path,  # Attach the new thumbnail
            caption=f"✅ File renamed and thumbnail changed: {new_filename}",
        )
        await message.reply_text("✅ Done! Here is your updated file.")
    except Exception as e:
        await message.reply_text(f"❌ Failed to process file: {e}")

# Start command
@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text("👋 Hello! Use /set_default <keyword> to set a custom word before file names.\nSend an image with /set_thumb to set a thumbnail, then send a file to rename and change its thumbnail.")

# Run Flask in a separate thread
def run_flask():
    port = int(os.environ.get("PORT", 8080))
    web_app.run(host="0.0.0.0", port=port)

if _name_ == "_main_":
    print("🤖 Bot is starting...")

    # Start Flask server in a separate thread
    flask_thread = Thread(target=run_flask, daemon=True)
    flask_thread.start()

    # Start Pyrogram bot
    app.start()
    print("✅ Bot is online and ready to receive commands.")

    # Keep bot running and listening to messages
    idle()

    print("🛑 Bot stopped.")
    app.stop()
