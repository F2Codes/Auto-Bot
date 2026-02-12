import json
import time
from collections import defaultdict

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

from database import init_db, add_user
from logger import setup_logger

CONFIG_FILE = "config.json"
user_messages = defaultdict(list)


# ---------------- CONFIG ----------------

def load_config():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)


def setup_token():
    config = load_config()

    if not config["BOT_TOKEN"]:
        token = input("Enter Bot Token: ")
        config["BOT_TOKEN"] = token
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=4)

    if not config["ADMIN_IDS"]:
        admin_id = int(input("Enter Admin ID: "))
        config["ADMIN_IDS"].append(admin_id)
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=4)

    return config


# ---------------- COMMANDS ----------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    add_user(user.id, user.username)
    await update.message.reply_text("🔥 Advanced Bot System Online!")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/start - Start bot\n"
        "/help - Show help"
    )


async def auto_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    config = load_config()

    user_id = update.effective_user.id
    current_time = time.time()

    # Anti-spam check
    user_messages[user_id] = [
        t for t in user_messages[user_id]
        if current_time - t < 10
    ]

    user_messages[user_id].append(current_time)

    if len(user_messages[user_id]) > config["ANTI_SPAM_LIMIT"]:
        await update.message.reply_text("⚠ Slow down!")
        return

    if config["AUTO_REPLY"]:
        await update.message.reply_text(config["AUTO_REPLY_MESSAGE"])


# ---------------- MAIN ----------------

def main():
    setup_logger()
    init_db()
    config = setup_token()

    app = ApplicationBuilder().token(config["BOT_TOKEN"]).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, auto_reply))

    print("🚀 Bot Running...")
    app.run_polling()


if __name__ == "__main__":
    main()
