from pyrogram import Client, filters
import os

# Replace these with your bot credentials
API_ID = 123456  # Get this from https://my.telegram.org/apps
API_HASH = "your_api_hash"
BOT_TOKEN = "your_bot_token"

app = Client("rename_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Start Command
@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text("Hello! Send me a file, and I'll rename it.")

# File Rename Handler
@app.on_message(filters.document | filters.video | filters.photo)
async def rename_file(client, message):
    file = message.document or message.video or message.photo
    if not file:
        return
    
    await message.reply_text("Send me the new name (with extension).")

    @app.on_message(filters.text)
    async def get_new_name(client, new_msg):
        new_name = new_msg.text
        path = await client.download_media(message)  # Download file
        new_path = f"{new_name}"

        os.rename(path, new_path)  # Rename file
        await message.reply_document(new_path, caption="Here is your renamed file!")

app.run()

user_thumbnails = {}

@app.on_message(filters.command("setthumb"))
async def set_thumbnail(client, message):
    if message.photo:
        user_thumbnails[message.from_user.id] = message.photo.file_id
        await message.reply_text("Thumbnail saved!")
    else:
        await message.reply_text("Please send an image.")

@app.on_message(filters.command("clearthumb"))
async def clear_thumbnail(client, message):
    user_thumbnails.pop(message.from_user.id, None)
    await message.reply_text("Thumbnail cleared.")

@app.on_message(filters.document | filters.video)
async def rename_with_thumbnail(client, message):
    user_id = message.from_user.id
    file = message.document or message.video
    file_path = await client.download_media(file)

    await message.reply_text("Send new filename (with extension).")

    @app.on_message(filters.text)
    async def rename_and_send(client, new_msg):
        new_name = new_msg.text
        os.rename(file_path, new_name)

        thumb = user_thumbnails.get(user_id, None)
        await message.reply_document(new_name, thumb=thumb, caption="Here is your renamed file!")
