# Telegram Marketing Bot

This is a powerful and flexible marketing bot for Telegram, built with Python and `python-telegram-bot`.

## Features

*   **Welcome Message**: Greets new users who start the bot.
*   **User Subscription**: Automatically saves users who start the bot for future broadcasts.
*   **Broadcasts**: As the bot owner, you can send a message to all subscribed users at once.
*   **Group & Channel Messaging**: Send messages to any group or channel the bot is a member of.
*   **Keyword Auto-Replies**: Automatically replies to messages containing specific keywords.
*   **Scheduled Messages**: Schedule messages to be sent at a future time to users, groups, or channels.
*   **Persistence**: Scheduled jobs are saved and will resume even if the bot is restarted.

## Project Structure

```
.
├── .env              # Configuration file for your secrets
├── .gitignore        # Files to be ignored by Git
├── bot.py            # The main bot logic
├── keywords.json     # Your keyword-to-response mappings
├── persistence.pickle # Stores scheduled jobs (auto-generated)
├── README.md         # This file
├── requirements.txt  # Python dependencies
└── users.json        # List of subscribed user IDs (auto-generated)
```

## Setup and Installation

Follow these steps to get your bot up and running.

### 1. Prerequisites

*   Python 3.8 or higher.
*   A Telegram Bot Token. If you don't have one, talk to [@BotFather](https://t.me/BotFather) on Telegram to create a new bot and get your token.

### 2. Clone the Repository & Install Dependencies

First, get the code and navigate into the directory. Then, install the required Python libraries.

```bash
# It is recommended to use a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

pip install -r requirements.txt
```

### 3. Configure Your Bot

You need to provide your bot's token and your own Telegram user ID.

1.  **Rename `.env.example` to `.env` (if applicable) or create a new `.env` file.** This file already exists in your directory.
2.  **Open the `.env` file and fill in the values:**

    ```ini
    TELEGRAM_TOKEN=YOUR_TELEGRAM_TOKEN_HERE
    OWNER_ID=YOUR_USER_ID_HERE
    ```

3.  **How to get your `OWNER_ID`?**
    *   On Telegram, find the bot [@userinfobot](https://t.me/userinfobot).
    *   Start a chat with it and it will immediately reply with your User ID.

### 4. Customize Keywords

Open the `keywords.json` file to define your own keyword-based auto-replies. The format is a simple JSON object where the key is the keyword (case-insensitive) and the value is the response the bot should send.

```json
{
  "help": "Please tell me what you need help with.",
  "pricing": "You can find our pricing at example.com/pricing."
}
```

## Running the Bot

To start the bot, simply run the `bot.py` script:

```bash
python bot.py
```

You should see log messages in your terminal indicating that the bot has started successfully.

## How to Use the Bot

Interact with your bot on Telegram. Only the `OWNER_ID` you specified can use the administrative commands.

### Commands

*   `/start`
    *   For regular users: Displays the welcome message and subscribes them to broadcasts.
    *   For everyone: A good way to check if the bot is running.

*   `/broadcast <message>`
    *   (Owner only) Sends the `<message>` to every user who has started the bot.
    *   Example: `/broadcast Hello everyone! We have a new promotion today.`

*   `/send <target> <message>`
    *   (Owner only) Sends the `<message>` to a specific group or channel.
    *   `<target>` can be the numerical ID of the group/channel or its public username (e.g., `@channel_name`).
    *   **Note**: The bot must be a member of the group or an admin in the channel (with post permissions).
    *   Example: `/send @my_channel_name Check out our latest update!`
    *   Example: `/send -1001234567890 This is a message to a private channel.`

*   `/schedule <time> <target> <message>`
    *   (Owner only) Schedules a message to be sent later.
    *   `<time>`: A relative time duration. Examples: `10m` (10 minutes), `2h` (2 hours), `1d12h` (1 day and 12 hours).
    *   `<target>`: The same as the `/send` command, or the special keyword `all` to schedule a broadcast to all users.
    *   Example: `/schedule 1h30m all Our webinar starts in 90 minutes!`
    *   Example: `/schedule 1d @my_channel_name Big announcement tomorrow!`
