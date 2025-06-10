import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from dotenv import load_dotenv
import os
from gagstock import start_announcer
from db import save_chat_id, remove_chat_id
import web_server

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

async def gagstock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    save_chat_id(chat.id)
    await update.message.reply_text("✅ Gagstock tracking is active.\nUpdates will be sent to this chat.\n\nMade by: @OchoOcho21")

async def stop_gagstock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    remove_chat_id(chat.id)
    await update.message.reply_text("🛑 Gagstock tracking has been stopped.\n\nMade by: @OchoOcho21")

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("gagstock", gagstock))
    app.add_handler(CommandHandler("stopgagstock", stop_gagstock))
    asyncio.get_event_loop().create_task(start_announcer(app.bot))
    app.run_polling()
