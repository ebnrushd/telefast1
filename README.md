# Telegram Marketing Bot - Enhanced

This is a powerful and flexible marketing bot for Telegram, built with Python and `python-telegram-bot`. This enhanced version includes interactive features, template management, and more to streamline your marketing efforts.

## Features

*   **Welcome Message**: Greets new users and provides a command list.
*   **User Subscription**: Automatically saves users who start the bot for future broadcasts.
*   **Chat Management**: Save groups and channels to easily send messages to them later.
*   **Message Templates**: Create and manage reusable message templates.
*   **URL Buttons**: Add clickable URL buttons to your templates to direct users to your site.
*   **Interactive Sending**: A user-friendly, menu-based system to send templates to your saved chats.
*   **Broadcasts & Direct Messaging**: Send immediate messages to all users or specific chats.
*   **Scheduled Messages**: Schedule messages to be sent at a future time.
*   **Keyword Auto-Replies**: Automatically replies to messages containing specific keywords.
*   **Statistics**: Get a quick overview of your bot's usage.
*   **Persistence**: Scheduled jobs are saved and will resume even if the bot is restarted.

## Project Structure

```
.
├── .env.example      # Example configuration file
├── .gitignore        # Files to be ignored by Git
├── bot.py            # The main bot logic
├── chats.json        # Stores your saved group/channel IDs
├── keywords.json     # Your keyword-to-response mappings
├── templates.json    # Your saved message templates
├── persistence.pickle # Stores scheduled jobs (auto-generated)
├── README.md         # This file
├── requirements.txt  # Python dependencies
└── users.json        # List of subscribed user IDs (auto-generated)
```

## Setup and Installation

Follow these steps to get your bot up and running.

### 1. Prerequisites

*   Python 3.8 or higher.
*   A Telegram Bot Token from [@BotFather](https://t.me/BotFather).

### 2. Install Dependencies

```bash
# It is recommended to use a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

pip install -r requirements.txt
```

### 3. Configure Your Bot

1.  **Create your configuration file.** Copy the example file to a new file named `.env`:
    ```bash
    cp .env.example .env
    ```
2.  **Open the `.env` file and fill in the values:**
    ```ini
    TELEGRAM_TOKEN=YOUR_TELEGRAM_TOKEN_HERE
    OWNER_ID=YOUR_USER_ID_HERE
    ```
3.  **Find your `OWNER_ID`:** Talk to the bot [@userinfobot](https://t.me/userinfobot) on Telegram to get your user ID.

## Running the Bot

```bash
python bot.py
```
The bot will now be running. All commands listed below (except `/start`) are owner-only.

## How to Use the Bot

### Step 1: Save Your Chats

Before you can send messages to groups or channels, you need to save them.
1.  Add your bot to the group or channel. For channels, make sure the bot is an administrator with permission to post messages.
2.  Go into the group/channel and type the command:
    *   `/add_chat`
3.  The bot will confirm that the chat has been saved. Repeat for all your target chats.
*   To see all saved chats, use: `/list_chats`

### Step 2: Create Message Templates

Create reusable messages for your campaigns.

*   **To create a simple template:**
    *   `/add_template <name> <content>`
    *   Example: `/add_template welcome Welcome to our community!`

*   **To create a template with a clickable button:**
    *   `/add_template <name> <content> | <button_text> | <button_url>`
    *   Example: `/add_template promo Visit our site! | Click Here | https://example.com`

*   To see all your templates, use: `/list_templates`
*   To remove a template, use: `/delete_template <name>`

### Step 3: Send Your Messages

*   **Interactive Send (Recommended):**
    *   `/send`
    *   The bot will reply with a menu of your saved chats. Click one.
    *   It will then show a menu of your saved templates. Click one to send it.

*   **Broadcast to all subscribed users:**
    *   `/broadcast <your message here>`

*   **Schedule a message:**
    *   `/schedule <time> <target> <message>`
    *   `<time>`: e.g., `10m`, `2h`, `1d12h`.
    *   `<target>`: A chat ID, a channel username (e.g., `@mychannel`), or `all` for a broadcast.

### Other Commands

*   **/stats**: Shows the number of subscribed users and saved chats.
*   **/cancel**: Cancels the current operation (like the interactive `/send`).
*   **Keyword Replies**: Edit `keywords.json` to add keyword-based auto-replies.
```
