import logging
import os
import json
import re
from datetime import timedelta
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    PicklePersistence,
    ConversationHandler,
    CallbackQueryHandler,
)

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
CHATS_FILE = "chats.json"
TEMPLATES_FILE = "templates.json"

# Conversation states
SELECTING_CHAT, SELECTING_TEMPLATE = range(2)

# --- Helper Functions ---
def load_templates():
    """Load templates from the storage file."""
    try:
        with open(TEMPLATES_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_template(name, content, button_text=None, button_url=None):
    """Save a template to the storage file, with optional button data."""
    templates = load_templates()
    template_data = {"content": content}
    if button_text and button_url:
        template_data["button_text"] = button_text
        template_data["button_url"] = button_url
    templates[name] = template_data
    with open(TEMPLATES_FILE, "w") as f:
        json.dump(templates, f, indent=4)

def delete_template_from_file(name):
    """Delete a template from the storage file."""
    templates = load_templates()
    if name in templates:
        del templates[name]
        with open(TEMPLATES_FILE, "w") as f:
            json.dump(templates, f, indent=4)
        return True
    return False

def load_chats():
    """Load chats from the storage file."""
    try:
        with open(CHATS_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_chat(chat_id, chat_title, chat_type):
    """Save a chat to the storage file."""
    chats = load_chats()
    chats[str(chat_id)] = {"title": chat_title, "type": chat_type}
    with open(CHATS_FILE, "w") as f:
        json.dump(chats, f, indent=4)

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
        "/start - Shows this welcome message.\n"
        "--- Chat Management ---\n"
        "/add_chat - Use in a group/channel to save it.\n"
        "/list_chats - Show saved chats.\n"
        "--- Template Management ---\n"
        "/add_template &lt;name&gt; &lt;content&gt; [| &lt;btn_text&gt; | &lt;btn_url&gt;]\n"
        "/list_templates\n"
        "/delete_template &lt;name&gt;\n"
        "--- Messaging ---\n"
        "/broadcast &lt;message&gt; - Sends a message to all users.\n"
        "/send - Interactively send a template to a saved chat.\n"
        "/schedule &lt;time&gt; &lt;target&gt; &lt;message&gt; - Schedules a message.\n"
        "--- Other ---\n"
        "/stats - Show bot statistics.\n"
    )

    await update.message.reply_html(welcome_message)

async def add_template(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """(Owner only) Adds a message template, optionally with a button."""
    if update.effective_user.id != OWNER_ID:
        return

    if len(context.args) < 2:
        await update.message.reply_text("Usage: /add_template <name> <content> [| <button_text> | <button_url>]")
        return

    full_args_str = " ".join(context.args)
    name = context.args[0]

    parts = full_args_str[len(name):].strip().split('|')
    content = parts[0].strip()

    button_text, button_url = None, None
    if len(parts) == 3:
        button_text = parts[1].strip()
        button_url = parts[2].strip()
        if not (button_text and button_url):
            await update.message.reply_text("Button text and URL must both be provided if you use the button syntax.")
            return
        save_template(name, content, button_text, button_url)
        await update.message.reply_text(f"Template '{name}' with button saved successfully.")
    else:
        save_template(name, content)
        await update.message.reply_text(f"Template '{name}' saved successfully.")

async def list_templates(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """(Owner only) Lists all message templates."""
    if update.effective_user.id != OWNER_ID:
        return
    templates = load_templates()
    if not templates:
        await update.message.reply_text("No templates saved yet. Use /add_template to create one.")
        return
    message = "<b>Saved Templates:</b>\n\n"
    for name, data in templates.items():
        message += f"<b>Name:</b> {name}\n"
        message += f"<b>Content:</b> {data['content']}\n"
        if "button_text" in data:
            message += f"<b>Button:</b> [{data['button_text']}]({data['button_url']})\n"
        message += "--------------------\n"
    await update.message.reply_html(message)

async def delete_template(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """(Owner only) Deletes a message template."""
    if update.effective_user.id != OWNER_ID:
        return
    if not context.args:
        await update.message.reply_text("Usage: /delete_template <name>")
        return
    name = context.args[0]
    if delete_template_from_file(name):
        await update.message.reply_text(f"Template '{name}' deleted successfully.")
    else:
        await update.message.reply_text(f"Template '{name}' not found.")

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """(Owner only) Displays bot statistics."""
    if update.effective_user.id != OWNER_ID:
        return

    user_ids = get_user_ids()
    chats = load_chats()

    message = (
        "<b>Bot Statistics:</b>\n\n"
        f"<b>Subscribed Users:</b> {len(user_ids)}\n"
        f"<b>Saved Chats:</b> {len(chats)}\n"
    )

    await update.message.reply_html(message)

async def add_chat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """(Owner only) Adds a chat to the list of saved chats."""
    user = update.effective_user
    chat = update.effective_chat

    if user.id != OWNER_ID:
        await update.message.reply_text("You are not authorized to use this command.")
        return

    if chat.type == "private":
        await update.message.reply_text("This command can only be used in a group or channel.")
        return

    save_chat(chat.id, chat.title, chat.type)
    await update.message.reply_text(f"Success! Chat '{chat.title}' ({chat.type}) has been saved.")

async def list_chats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """(Owner only) Lists all saved chats."""
    user = update.effective_user
    if user.id != OWNER_ID:
        await update.message.reply_text("You are not authorized to use this command.")
        return

    chats = load_chats()
    if not chats:
        await update.message.reply_text("No chats have been saved yet. Use /add_chat in a group or channel to save it.")
        return

    message = "<b>Saved Chats:</b>\n\n"
    for chat_id, chat_info in chats.items():
        message += f"<b>Title:</b> {chat_info['title']}\n"
        message += f"<b>Type:</b> {chat_info['type']}\n"
        message += f"<b>ID:</b> <code>{chat_id}</code>\n"
        message += "--------------------\n"

    await update.message.reply_html(message)

async def send_interactive(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the interactive process to send a message."""
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("You are not authorized to use this command.")
        return ConversationHandler.END

    chats = load_chats()
    if not chats:
        await update.message.reply_text("No chats saved. Use /add_chat in a group/channel first.")
        return ConversationHandler.END

    keyboard = []
    for chat_id, chat_info in chats.items():
        keyboard.append([InlineKeyboardButton(f"{chat_info['title']} ({chat_info['type']})", callback_data=chat_id)])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Please select a destination:", reply_markup=reply_markup)

    return SELECTING_CHAT

async def select_chat_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles chat selection and asks for template selection."""
    query = update.callback_query
    await query.answer()

    chat_id = query.data
    context.user_data['selected_chat_id'] = chat_id

    templates = load_templates()
    if not templates:
        await query.edit_message_text("No templates found. Please add one with /add_template.")
        return ConversationHandler.END

    keyboard = []
    for name in templates.keys():
        keyboard.append([InlineKeyboardButton(name, callback_data=name)])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("Please select a message template:", reply_markup=reply_markup)

    return SELECTING_TEMPLATE

async def select_template_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles template selection and sends the message."""
    query = update.callback_query
    await query.answer()

    template_name = query.data
    chat_id = context.user_data.get('selected_chat_id')

    templates = load_templates()
    template = templates.get(template_name)

    if not chat_id or not template:
        await query.edit_message_text("Error: Could not find chat or template. Please start again.")
        return ConversationHandler.END

    reply_markup = None
    if "button_text" in template and "button_url" in template:
        button = InlineKeyboardButton(template["button_text"], url=template["button_url"])
        reply_markup = InlineKeyboardMarkup([[button]])

    try:
        await context.bot.send_message(
            chat_id=chat_id,
            text=template['content'],
            reply_markup=reply_markup,
            parse_mode='HTML' # Assume content might have HTML
        )
        await query.edit_message_text(f"Message sent successfully to chat ID {chat_id}.")
    except Exception as e:
        logger.error(f"Failed to send interactive message to {chat_id}: {e}")
        await query.edit_message_text(f"Failed to send message. Error: {e}")

    context.user_data.clear()
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    await update.message.reply_text("Operation cancelled.")
    context.user_data.clear()
    return ConversationHandler.END

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

def create_application() -> Application:
    """Create and configure the Telegram bot application."""
    persistence = PicklePersistence(filepath="persistence.pickle")
    application = Application.builder().token(TELEGRAM_TOKEN).persistence(persistence).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("add_chat", add_chat))
    application.add_handler(CommandHandler("list_chats", list_chats))
    application.add_handler(CommandHandler("add_template", add_template))
    application.add_handler(CommandHandler("list_templates", list_templates))
    application.add_handler(CommandHandler("delete_template", delete_template))
    application.add_handler(CommandHandler("stats", stats))
    application.add_handler(CommandHandler("broadcast", broadcast))
    application.add_handler(CommandHandler("schedule", schedule_message))

    # Setup ConversationHandler for interactive send
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("send", send_interactive)],
        states={
            SELECTING_CHAT: [CallbackQueryHandler(select_chat_callback)],
            SELECTING_TEMPLATE: [CallbackQueryHandler(select_template_callback)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    application.add_handler(conv_handler)

    # Add the message handler for keywords
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    return application
