import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from dotenv import load_dotenv
import os
from gagstock import start_announcer
from db import save_chat_id, remove_chat_id, get_all_chat_ids, get_chat_names
import web_server

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 7215748787

async def gagstock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    save_chat_id(chat.id, chat.title or chat.username or chat.first_name)
    await update.message.reply_text("✅ Gagstock tracking is active.\nUpdates will be sent to this chat.\n\nMade by: @OchoOcho21")

async def stop_gagstock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    remove_chat_id(chat.id)
    await update.message.reply_text("🛑 Gagstock tracking has been stopped.\n\nMade by: @OchoOcho21")

async def list_chats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    chats = get_chat_names()
    if not chats:
        await update.message.reply_text("No chats registered.")
        return
    msg = "📋 Registered Chats:\n\n" + "\n".join([f"{name} — `{cid}`" for cid, name in chats])
    await update.message.reply_text(msg, parse_mode="Markdown")

async def remove_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    if not context.args:
        await update.message.reply_text("Usage: /removechat <chat_id>")
        return
    try:
        chat_id = int(context.args[0])
        remove_chat_id(chat_id)
        await update.message.reply_text(f"✅ Removed chat ID: {chat_id}")
    except:
        await update.message.reply_text("Invalid chat ID.")

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("gagstock", gagstock))
    app.add_handler(CommandHandler("stopgagstock", stop_gagstock))
    app.add_handler(CommandHandler("listchats", list_chats))
    app.add_handler(CommandHandler("removechat", remove_chat))
    asyncio.get_event_loop().create_task(start_announcer(app.bot))
    app.run_polling()
