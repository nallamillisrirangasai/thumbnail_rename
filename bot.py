from pyrogram import Client, filters
import os

# Replace these with your bot credentials
API_ID = 123456  # Get this from https://my.telegram.org/apps
API_HASH = "your_api_hash"
BOT_TOKEN = "your_bot_token"

app = Client("rename_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Store user data
user_files = {}  # Stores user-uploaded files for batch renaming
user_thumbnails = {}  # Stores thumbnails for users

# 🚀 Start Command
@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text("Hello! Send me a file, and I'll rename it.\n\n"
                             "Commands:\n"
                             "/rename - Rename a single file\n"
                             "/rename_all - Rename all files in batch\n"
                             "/setthumb - Set a thumbnail\n"
                             "/clearthumb - Clear the saved thumbnail")

# 📁 Single File Rename Handler
@app.on_message(filters.document | filters.video)
async def single_file_handler(client, message):
    user_id = message.from_user.id
    file = message.document or message.video

    file_path = await client.download_media(file)
    await message.reply_text("Send me the new name (including extension).")

    @app.on_message(filters.text & filters.user(user_id))
    async def rename_single_file(client, new_msg):
        new_name = new_msg.text
        new_path = os.path.join(os.path.dirname(file_path), new_name)

        os.rename(file_path, new_path)
        thumb = user_thumbnails.get(user_id)

        await message.reply_document(new_path, caption="Here is your renamed file!", thumb=thumb)
        await new_msg.reply_text("✅ File renamed and sent!")

        # Remove the handler after renaming to prevent multiple triggers
        app.remove_handler(rename_single_file)

# 📦 Bulk Rename - File Collection
@app.on_message(filters.document | filters.video)
async def collect_bulk_files(client, message):
    user_id = message.from_user.id
    file = message.document or message.video

    if user_id not in user_files:
        user_files[user_id] = []

    user_files[user_id].append(file.file_id)
    await message.reply_text("File added! Send more files or type `/rename_all` to rename all.")

# 🔄 Bulk Rename Execution
@app.on_message(filters.command("rename_all"))
async def rename_bulk(client, message):
    user_id = message.from_user.id

    if user_id not in user_files or not user_files[user_id]:
        await message.reply_text("No files to rename.")
        return

    await message.reply_text("Send the new name pattern (e.g., file_#.mp4, file_#.jpg).\n"
                             "`#` will be replaced by numbers.")

    @app.on_message(filters.text & filters.user(user_id))
    async def rename_bulk_files(client, new_msg):
        name_pattern = new_msg.text
        renamed_files = []

        for i, file_id in enumerate(user_files[user_id], start=1):
            file_path = await client.download_media(file_id)
            new_name = name_pattern.replace("#", str(i))
            new_path = os.path.join(os.path.dirname(file_path), new_name)

            os.rename(file_path, new_path)
            renamed_files.append(new_path)

            await message.reply_document(new_path, caption=f"Renamed to {new_name}")

        user_files[user_id] = []
        await new_msg.reply_text("✅ All files renamed and sent!")

        app.remove_handler(rename_bulk_files)

# 🖼️ Set Thumbnail
@app.on_message(filters.command("setthumb") & filters.photo)
async def set_thumbnail(client, message):
    user_thumbnails[message.from_user.id] = message.photo.file_id
    await message.reply_text("✅ Thumbnail saved!")

# ❌ Clear Thumbnail
@app.on_message(filters.command("clearthumb"))
async def clear_thumbnail(client, message):
    user_thumbnails.pop(message.from_user.id, None)
    await message.reply_text("✅ Thumbnail cleared.")

app.run()
