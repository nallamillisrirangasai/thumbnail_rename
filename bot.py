from pyrogram import Client, filters
import os

# Replace with your own credentials
API_ID = 123456  # Replace with your API ID
API_HASH = "your_api_hash"  # Replace with your API HASH
BOT_TOKEN = "your_bot_token"  # Replace with your bot token

bot = Client("FileRenameBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@bot.on_message(filters.document | filters.video | filters.photo)
async def file_handler(client, message):
    # Save file
    file_path = await message.download()
    
    # Ask user for new file name
    await message.reply_text("Send me the new name (without extension).")
    
    # Wait for user response
    @bot.on_message(filters.text)
    async def rename_file(client, new_message):
        new_name = new_message.text
        file_extension = os.path.splitext(file_path)[1]  # Get file extension
        new_file_path = new_name + file_extension
        
        os.rename(file_path, new_file_path)
        await new_message.reply_document(new_file_path, caption="Here is your renamed file.")

bot.run()
