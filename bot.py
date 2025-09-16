import logging
import os
import json
import re
from datetime import timedelta
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, PicklePersistence

# Load environment variables from .env file
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID", 0))

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- Constants ---
USERS_FILE = "users.json"
KEYWORDS_FILE = "keywords.json"

# --- Helper Functions ---
def load_keywords():
    """Load keywords from the storage file."""
    try:
        with open(KEYWORDS_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def get_user_ids():
    """Load user IDs from the storage file."""
    try:
        with open(USERS_FILE, "r") as f:
            return set(json.load(f))
    except (FileNotFoundError, json.JSONDecodeError):
        return set()

def add_user_id(user_id):
    """Add a user ID to the storage file."""
    user_ids = get_user_ids()
    if user_id not in user_ids:
        user_ids.add(user_id)
        with open(USERS_FILE, "w") as f:
            json.dump(list(user_ids), f)

# --- Command Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a welcome message and add the user to the user list."""
    user = update.effective_user
    add_user_id(user.id)

    welcome_message = (
        f"Hello {user.mention_html()}! Welcome to your new marketing bot.\n\n"
        "Here are the commands you can use:\n"
        "/start - Shows this welcome message and registers you for updates.\n"
        "/broadcast <message> - (Owner only) Sends a message to all users.\n"
        "/send <id_or_@username> <message> - (Owner only) Sends a message to a group or channel.\n"
        "/schedule <time> <target> <message> - (Owner only) Schedules a message. Time format: 1d2h3m4s.\n"
    )

    await update.message.reply_html(welcome_message)

async def send_to_target(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """(Owner only) Send a message to a specific channel or group."""
    user_id = update.effective_user.id
    if user_id != OWNER_ID:
        await update.message.reply_text("You are not authorized to use this command.")
        return

    if len(context.args) < 2:
        await update.message.reply_text("Usage: /send <channel_or_group_id> <message>")
        return

    target_id = context.args[0]
    message = " ".join(context.args[1:])

    try:
        await context.bot.send_message(chat_id=target_id, text=message)
        await update.message.reply_text(f"Message sent successfully to {target_id}.")
    except Exception as e:
        logger.error(f"Failed to send message to {target_id}: {e}")
        await update.message.reply_text(f"Failed to send message to {target_id}. Error: {e}\n"
                                        f"Make sure the bot is a member of the group/channel and has permission to post.")

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """(Owner only) Broadcast a message to all users."""
    user_id = update.effective_user.id
    if user_id != OWNER_ID:
        await update.message.reply_text("You are not authorized to use this command.")
        return

    message = " ".join(context.args)
    if not message:
        await update.message.reply_text("Please provide a message to broadcast. Usage: /broadcast <message>")
        return

    user_ids = get_user_ids()
    if not user_ids:
        await update.message.reply_text("No users have started the bot yet.")
        return

    success_count = 0
    failure_count = 0
    for uid in user_ids:
        try:
            await context.bot.send_message(chat_id=uid, text=message)
            success_count += 1
        except Exception as e:
            logger.error(f"Failed to send message to {uid}: {e}")
            failure_count += 1

    await update.message.reply_text(f"Broadcast finished.\nSent: {success_count}\nFailed: {failure_count}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle keyword-based auto-replies."""
    message_text = update.message.text.lower()
    keywords = load_keywords()

    for keyword, response in keywords.items():
        # Using \b for word boundary to avoid partial matches
        if re.search(r'\b' + re.escape(keyword.lower()) + r'\b', message_text):
            await update.message.reply_text(response)
            return # Respond once per message

def parse_time(time_str: str) -> int:
    """Parse a time string like 1d2h3m4s into seconds."""
    parts = re.findall(r'(\d+)([dhms])', time_str.lower())
    if not parts:
        return 0

    total_seconds = 0
    for value, unit in parts:
        value = int(value)
        if unit == 'd':
            total_seconds += value * 86400
        elif unit == 'h':
            total_seconds += value * 3600
        elif unit == 'm':
            total_seconds += value * 60
        elif unit == 's':
            total_seconds += value
    return total_seconds

async def scheduled_task(context: ContextTypes.DEFAULT_TYPE):
    """Callback function for scheduled jobs."""
    job = context.job
    target = job.data['target']
    message = job.data['message']
    bot = context.bot

    logger.info(f"Executing scheduled job to target {target}")

    if target == "all":
        user_ids = get_user_ids()
        for uid in user_ids:
            try:
                await bot.send_message(chat_id=uid, text=message)
            except Exception as e:
                logger.error(f"Failed to send scheduled message to user {uid}: {e}")
    else:
        try:
            await bot.send_message(chat_id=target, text=message)
        except Exception as e:
            logger.error(f"Failed to send scheduled message to target {target}: {e}")

async def schedule_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """(Owner only) Schedule a message."""
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("You are not authorized to use this command.")
        return

    if len(context.args) < 3:
        await update.message.reply_text("Usage: /schedule <time> <target|all> <message>")
        return

    time_str = context.args[0]
    target = context.args[1]
    message = " ".join(context.args[2:])

    delay = parse_time(time_str)
    if delay <= 0:
        await update.message.reply_text("Invalid time format. Please use a format like 1d2h3m4s.")
        return

    context.job_queue.run_once(
        scheduled_task,
        when=delay,
        data={'target': target, 'message': message},
        name=f"schedule_{update.effective_message.message_id}"
    )

    await update.message.reply_text(f"Message scheduled to be sent to {target} in {time_str}.")

def main() -> None:
    """Start the bot."""
    persistence = PicklePersistence(filepath="persistence.pickle")
    application = Application.builder().token(TELEGRAM_TOKEN).persistence(persistence).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("broadcast", broadcast))
    application.add_handler(CommandHandler("send", send_to_target))
    application.add_handler(CommandHandler("schedule", schedule_message))

    # Add the message handler for keywords
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()

if __name__ == "__main__":
    main()
