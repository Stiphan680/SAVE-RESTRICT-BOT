# Custom Save Restricted Bot - Batch Command

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
import pyrogram.enums as enums

@Client.on_message(filters.command("batch") & filters.private)
async def batch_command(client: Client, message: Message):
    """
    Batch/Bulk download command - Shows instructions on how to use batch mode
    """
    
    batch_text = (
        "<b>📦 Batch/Bulk Download Guide</b>\n\n"
        "<blockquote><b>🔹 What is Batch Mode?</b>\n"
        "Download multiple messages at once from a channel/chat.</blockquote>\n\n"
        "<blockquote><b>📝 How to Use:</b>\n\n"
        "<b>Step 1:</b> Get the message link\n"
        "• Go to the channel\n"
        "• Forward first message to @missrose_bot\n"
        "• Get the message ID (e.g., 100)\n\n"
        "<b>Step 2:</b> Get last message ID\n"
        "• Forward last message\n"
        "• Get ID (e.g., 150)\n\n"
        "<b>Step 3:</b> Create batch link\n"
        "• Format: <code>https://t.me/ChannelName/FirstID-LastID</code>\n"
        "• Example: <code>https://t.me/example/100-150</code></blockquote>\n\n"
        "<blockquote><b>✨ Examples:</b>\n\n"
        "<b>Public Channel:</b>\n"
        "<code>https://t.me/channelname/1-10</code>\n\n"
        "<b>Private Channel:</b>\n"
        "<code>https://t.me/c/1234567890/1-10</code>\n\n"
        "<b>Single Message:</b>\n"
        "<code>https://t.me/channelname/5</code></blockquote>\n\n"
        "<blockquote><b>⚠️ Important Notes:</b>\n"
        "• You must <code>/login</code> first for restricted content\n"
        "• Use <code>/cancel</code> to stop batch download\n"
        "• Bot processes 1 message every 3 seconds\n"
        "• Large batches may take time</blockquote>\n\n"
        "<blockquote><b>💡 Pro Tips:</b>\n"
        "• Start with small batches (5-10 messages)\n"
        "• Monitor progress in chat\n"
        "• Cancel anytime with /cancel\n"
        "• Bot shows download/upload progress</blockquote>"
    )
    
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔐 Login First", callback_data="login_help"),
        ],
        [
            InlineKeyboardButton("🏠 Home", callback_data="start_btn"),
            InlineKeyboardButton("❌ Close", callback_data="close_btn")
        ]
    ])
    
    await message.reply_text(
        text=batch_text,
        reply_markup=buttons,
        parse_mode=enums.ParseMode.HTML,
        disable_web_page_preview=True
    )

# Callback handler for login help
@Client.on_callback_query(filters.regex("^login_help$"))
async def login_help_callback(client: Client, callback_query):
    login_text = (
        "<b>🔐 How to Login</b>\n\n"
        "<blockquote><b>📝 Step-by-step:</b>\n\n"
        "<b>1.</b> Use <code>/login</code> command\n\n"
        "<b>2.</b> Generate session string:\n"
        "• Bot: @StringSessionBot\n"
        "• Or: @StringFatherBot\n\n"
        "<b>3.</b> Follow bot instructions:\n"
        "• Enter phone number\n"
        "• Enter OTP code\n"
        "• Enter password (if 2FA enabled)\n\n"
        "<b>4.</b> Copy the session string\n\n"
        "<b>5.</b> Send it to me\n\n"
        "<b>6.</b> ✅ Done! Start downloading</blockquote>\n\n"
        "<blockquote><b>⚠️ Security:</b>\n"
        "• Session is encrypted\n"
        "• We auto-delete your message\n"
        "• Use /logout to remove session</blockquote>"
    )
    
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔙 Back to Batch", callback_data="batch_help"),
        ],
        [
            InlineKeyboardButton("🏠 Home", callback_data="start_btn"),
            InlineKeyboardButton("❌ Close", callback_data="close_btn")
        ]
    ])
    
    await callback_query.message.edit_text(
        text=login_text,
        reply_markup=buttons,
        parse_mode=enums.ParseMode.HTML
    )
    await callback_query.answer()

# Callback to go back to batch help
@Client.on_callback_query(filters.regex("^batch_help$"))
async def batch_help_callback(client: Client, callback_query):
    batch_text = (
        "<b>📦 Batch/Bulk Download Guide</b>\n\n"
        "<blockquote><b>🔹 What is Batch Mode?</b>\n"
        "Download multiple messages at once from a channel/chat.</blockquote>\n\n"
        "<blockquote><b>📝 How to Use:</b>\n\n"
        "<b>Step 1:</b> Get the message link\n"
        "• Go to the channel\n"
        "• Forward first message to @missrose_bot\n"
        "• Get the message ID (e.g., 100)\n\n"
        "<b>Step 2:</b> Get last message ID\n"
        "• Forward last message\n"
        "• Get ID (e.g., 150)\n\n"
        "<b>Step 3:</b> Create batch link\n"
        "• Format: <code>https://t.me/ChannelName/FirstID-LastID</code>\n"
        "• Example: <code>https://t.me/example/100-150</code></blockquote>\n\n"
        "<blockquote><b>✨ Examples:</b>\n\n"
        "<b>Public Channel:</b>\n"
        "<code>https://t.me/channelname/1-10</code>\n\n"
        "<b>Private Channel:</b>\n"
        "<code>https://t.me/c/1234567890/1-10</code>\n\n"
        "<b>Single Message:</b>\n"
        "<code>https://t.me/channelname/5</code></blockquote>\n\n"
        "<blockquote><b>⚠️ Important Notes:</b>\n"
        "• You must <code>/login</code> first for restricted content\n"
        "• Use <code>/cancel</code> to stop batch download\n"
        "• Bot processes 1 message every 3 seconds\n"
        "• Large batches may take time</blockquote>\n\n"
        "<blockquote><b>💡 Pro Tips:</b>\n"
        "• Start with small batches (5-10 messages)\n"
        "• Monitor progress in chat\n"
        "• Cancel anytime with /cancel\n"
        "• Bot shows download/upload progress</blockquote>"
    )
    
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔐 Login First", callback_data="login_help"),
        ],
        [
            InlineKeyboardButton("🏠 Home", callback_data="start_btn"),
            InlineKeyboardButton("❌ Close", callback_data="close_btn")
        ]
    ])
    
    await callback_query.message.edit_text(
        text=batch_text,
        reply_markup=buttons,
        parse_mode=enums.ParseMode.HTML,
        disable_web_page_preview=True
    )
    await callback_query.answer()
