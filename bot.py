from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ChatMemberHandler,
    filters,
    ContextTypes,
)
import logging
import os

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Command: /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! I'm your group management bot. Use /help to see available commands.")

# Command: /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "/start - Start the bot\n"
        "/help - Show this help message\n"
        "/ban - Ban a user (reply to their message, admins only)\n"
        "/kick - Kick a user (reply to their message, admins only)\n"
    )
    await update.message.reply_text(help_text)

# Welcome new members
async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        await update.message.reply_text(f"Welcome, {member.full_name}! Please follow the group rules.")

# Check if user is an admin
async def is_admin(update: Update, user_id: int, chat_id: int) -> bool:
    member = await context.bot.get_chat_member(chat_id, user_id)
    return member.status in ["administrator", "creator"]

# Command: /ban
async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        await update.message.reply_text("Please reply to a user's message to ban them.")
        return

    chat_id = update.message.chat_id
    user_id = update.message.from_user.id
    target_user_id = update.message.reply_to_message.from_user.id

    if await is_admin(update, user_id, chat_id):
        try:
            await context.bot.ban_chat_member(chat_id, target_user_id)
            await update.message.reply_text("User has been banned.")
        except Exception as e:
            await update.message.reply_text(f"Error banning user: {e}")
    else:
        await update.message.reply_text("Only admins can ban users.")

# Command: /kick
async def kick(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        await update.message.reply_text("Please reply to a user's message to kick them.")
        return

    chat_id = update.message.chat_id
    user_id = update.message.from_user.id
    target_user_id = update.message.reply_to_message.from_user.id

    if await is_admin(update, user_id, chat_id):
        try:
            await context.bot.ban_chat_member(chat_id, target_user_id)
            await context.bot.unban_chat_member(chat_id, target_user_id)
            await update.message.reply_text("User has been kicked.")
        except Exception as e:
            await update.message.reply_text(f"Error kicking user: {e}")
    else:
        await update.message.reply_text("Only admins can kick users.")

# Filter messages (e.g., remove profanity)
async def filter_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bad_words = ["badword1", "badword2"]  # Customize this list
    message_text = update.message.text.lower()
    if any(word in message_text for word in bad_words):
        await update.message.delete()
        await update.message.reply_text("Please avoid using inappropriate words.")

# Error handler
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Update {update} caused error {context.error}")

def main():
    # Get bot token from environment variable
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN environment variable not set")

    # Initialize the application
    application = Application.builder().token(token).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("ban", ban))
    application.add_handler(CommandHandler("kick", kick))
    application.add_handler(ChatMemberHandler(welcome, ChatMemberHandler.CHAT_MEMBER))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, filter_messages))

    # Error handler
    application.add_error_handler(error_handler)

    # Start the bot with polling
    application.run_polling()

if __name__ == "__main__":
    main()
