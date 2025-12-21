<h1 align="center">🤖 Save Restricted Content Bot</h1>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python&logoColor=white">
  <img src="https://img.shields.io/badge/Pyrogram-v2-yellow?style=for-the-badge&logo=telegram">
  <img src="https://img.shields.io/badge/MongoDB-Database-green?style=for-the-badge&logo=mongodb">
  <img src="https://img.shields.io/badge/License-MIT-orange?style=for-the-badge&logo=opensourceinitiative">
</p>

<p align="center">
  <b>An advanced Telegram bot by RexBots designed to save restricted content (Text, Media, Files) from both private and public channels.</b>
  <br>
  <i>Features Batch Downloading, Custom Captions, Auto-Delete/Replace support, and a Premium Subscription System.</i>
</p>

<p align="center">
  <a href="https://t.me/RexBots_Official">
    <img src="https://img.shields.io/badge/Support-Channel-blue?style=for-the-badge&logo=telegram">
  </a>
  <a href="https://github.com/abhinai2244/SAVE-RESTRICT-BOT/issues">
    <img src="https://img.shields.io/github/issues/abhinai2244/SAVE-RESTRICT-BOT?style=for-the-badge&logo=github">
  </a>
  <a href="https://github.com/abhinai2244/SAVE-RESTRICT-BOT/forks">
    <img src="https://img.shields.io/github/forks/abhinai2244/SAVE-RESTRICT-BOT?style=for-the-badge&logo=github">
  </a>
</p>

<hr>

## 📑 Table of Contents

- [🚀 Features](#-features)
- [🛠 Deployment](#-deployment)
  - [Prerequisites](#prerequisites)
  - [Environment Variables](#environment-variables)
  - [Local Setup](#local-setup)
  - [Docker](#docker)
- [📝 Commands](#-commands)
- [📂 Project Structure](#-project-structure)
- [🤝 Contributors](#-contributors)
- [📞 Support](#-support)

<hr>

## 🚀 Features

| Feature | Description |
| :--- | :--- |
| **🔐 Save Restricted** | Download text, media, and files from channels where saving/forwarding is restricted. |
| **📦 Batch Mode** | Bulk download messages from any Public or Private channel using `/batch`. |
| **🔑 User Login** | Secure login with your Telegram account using `/login` (Session String). |
| **🎨 Customization** | Set custom **Captions** and **Thumbnails**. |
| **✂️ Text Manipulation** | Auto-delete or replace specific words in filenames and captions. |
| **💎 Premium System** | Integrated subscription system for Free vs Premium users. |
| **👮 Admin Control** | Broadcast messages, ban/unban users, manage premium access, and set dump chats. |
| **💾 Persistent Data** | Users and settings are stored securely in **MongoDB**. |
| **🔄 Keep-Alive** | Built-in mechanism to keep the bot running on platforms like Render/Heroku. |

<hr>

## 🛠 Deployment

<p align="center">
  <a href="https://heroku.com/deploy?template=https://github.com/abhinai2244/SAVE-RESTRICT-BOT">
    <img src="https://www.herokucdn.com/deploy/button.svg" alt="Deploy to Heroku">
  </a>
</p>

### Prerequisites

*   Python 3.10+
*   MongoDB Connection String
*   Telegram API ID & Hash
*   Bot Token

### Environment Variables

<details>
<summary><b>Click to view required variables</b></summary>

| Variable | Description | Example |
| :--- | :--- | :--- |
| `BOT_TOKEN` | Your Telegram Bot Token from @BotFather | `12345:ABC-DEF...` |
| `API_ID` | Your Telegram API ID from my.telegram.org | `1234567` |
| `API_HASH` | Your Telegram API Hash from my.telegram.org | `a1b2c3d4...` |
| `ADMINS` | Comma-separated list of Admin User IDs | `12345678,87654321` |
| `DB_URI` | Your MongoDB Connection String | `mongodb+srv://user:pass@...` |
| `DB_NAME` | Database Name (default: `SaveRestricted2`) | `SaveRestrictedBot` |
| `LOG_CHANNEL` | Channel ID for logging new users and errors | `-100123456789` |
| `ERROR_MESSAGE` | Send error messages to user (`True`/`False`) | `True` |
| `KEEP_ALIVE_URL` | URL to ping for keep-alive (optional) | `https://your-app.onrender.com` |

</details>

### Local Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/abhinai2244/SAVE-RESTRICT-BOT.git
    cd SAVE-RESTRICT-BOT
    ```

2.  **Install dependencies:**
    ```bash
    pip3 install -r requirements.txt
    ```

3.  **Run the bot:**
    ```bash
    python3 bot.py
    ```

### Docker

```bash
docker build -t rexbots-save-content .
docker run -d --env-file .env rexbots-save-content
```

<hr>

## 📝 Commands

<details open>
<summary><b>👤 User Commands</b></summary>

| Command | Description |
| :--- | :--- |
| `/start` | Check if the bot is running. |
| `/help` | Get detailed help instructions. |
| `/login` | Login to your account (via Session String). |
| `/logout` | Logout from your account. |
| `/batch` | Bulk save messages from a channel. |
| `/cancel` | Cancel any ongoing batch process. |
| `/myplan` | Check your current subscription plan. |
| `/premium` | View premium plan details. |
| `/settings` | Open the interactive settings menu. |

</details>

<details>
<summary><b>⚙️ Customization & Settings</b></summary>

| Command | Description |
| :--- | :--- |
| `/set_caption` | Set a custom caption for your files. |
| `/see_caption` | View your current custom caption. |
| `/del_caption` | Delete your custom caption. |
| `/set_thumb` | Reply to a photo to set it as a thumbnail. |
| `/view_thumb` | View your current thumbnail. |
| `/del_thumb` | Delete your custom thumbnail. |
| `/thumb_mode` | Toggle thumbnail usage (Custom vs Default). |
| `/set_del_word` | Set words to auto-remove from captions/filenames. |
| `/rem_del_word` | Remove words from the auto-delete list. |
| `/set_repl_word` | Set words to auto-replace. |
| `/rem_repl_word` | Remove a replacement word pair. |
| `/setchat` | Set the dump chat ID for forwarded content. |

</details>

<details>
<summary><b>👮 Admin Commands</b></summary>

| Command | Description |
| :--- | :--- |
| `/broadcast` | Broadcast a message to all users. |
| `/ban` / `/unban` | Ban or Unban a user from the bot. |
| `/add_premium` | Grant premium status to a user (`/add_premium <id> <time>`). |
| `/remove_premium` | Revoke premium status from a user. |
| `/set_dump` | Set a dump chat for a specific user. |
| `/users` | View total number of bot users. |
| `/premium_users` | List all active premium users. |
| `/dblink` | Get the database connection string. |

</details>

<hr>

## 📂 Project Structure

```
├── Rexbots/               # Main source code directory
│   ├── admin.py           # Admin command handlers
│   ├── broadcast.py       # Broadcast functionality
│   ├── caption.py         # Caption management
│   ├── premium.py         # Premium system logic
│   ├── settings.py        # Settings and configuration
│   └── ...
├── database/              # Database interaction layer
├── bot.py                 # Bot entry point
├── app.py                 # Flask app for keep-alive
├── config.py              # Configuration variables
├── Dockerfile             # Docker build instructions
├── requirements.txt       # Python dependencies
└── README.md              # Project documentation
```

<hr>

## 🤝 Contributors

A huge thanks to the developers who made this project possible:

<div align="center">

| [**Abhi**](https://t.me/about_zani/143) | [**Abhinav**](https://t.me/adityaabhinav) | [**Bharat**](https://t.me/Bharath_boy) | [**Master**](https://t.me/V_Sbotmaker) |
| :---: | :---: | :---: | :---: |
| Owner | Developer | Developer | Developer |

</div>

<hr>

## 📞 Support

For queries, feature requests, or bug reports, join our official channel:

<div align="center">
  <a href="https://t.me/RexBots_Official">
    <img src="https://img.shields.io/badge/RexBots-Official%20Channel-blue?style=for-the-badge&logo=telegram&logoColor=white&height=40">
  </a>
</div>
