# MNFDiscordMatureVerification
A Discord bot built with discord.py to handle user verification for mature content roles by requesting a secret phrase and photo ID. The bot streamlines the verification process and allows admins to approve or deny requests with simple button interactions.

## ⭐ Features

- **Verification Process:** Users can request verification for a mature role by providing a secret phrase hidden in the rules and a photo ID.

- **Admin Approval:** Admins receive the verification request in a private channel with buttons to Approve or Deny.

- **Secure Attachments:** Only images are accepted as attachments.

- **User Notifications:** Users are notified via DM when their request is approved or denied.

- **Secret Phrase Validation:** Ensures users provide the correct secret phrase, promoting rule compliance.

## 📦 Requirements
- Python 3.11+
- discord.py
- python-dotenv (optional for local development)
- A Discord bot token (created through the Discord Developer Portal)

## ⚙️ **Installation**

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/your-username/discord-verification-bot.git
   cd discord-verification-bot

2. Create a Virtual Environment:

    ```bash 
    python -m venv bot-env
    source bot-env/bin/activate  # On Windows: bot-env\Scripts\activate
    ```

3. Install Dependencies:

    ```bash
    pip install -r requirements.txt
    ```

4. Create a .env file in the root directory:

    ```
    DISCORD_BOT_TOKEN=your_discord_bot_token
    ADMIN_CHANNEL_ID=123456789012345678
    MATURE_ROLE_ID=987654321098765432
    ```

    The bot needs `Enable Message Content Intent`, `Server Members Intent`, and `Presence Intent` in the bot settings. 
    
    Use the OAuth2 URL generator to invite the bot to your server with bot and applications.commands scopes, and give it appropriate permissions (`Send Messages`, `Attach Files`, and `Manage Roles`).

5. Activate the Virtual Environment and Run the Bot:
    ```bash
    source bot-env/bin/activate  # On Windows: bot-env\Scripts\activate
    python bot.py
    ```

## 💬 Contributing
Contributions are welcome! If you find a bug or want to improve the bot, please open an issue or submit a pull request.