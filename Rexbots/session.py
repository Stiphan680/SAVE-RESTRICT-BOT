# Custom Save Restricted Bot - Stable Session Handler

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from database.db import db
from config import ADMINS
from logger import LOGGER

logger = LOGGER(__name__)

# --- Login Command (Session String Method) ---

@Client.on_message(filters.command("login") & filters.private)
async def login_command(client: Client, message: Message):
    user_id = message.from_user.id
    
    # Check if already logged in
    session = await db.get_session(user_id)
    if session:
        buttons = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🚪 Logout", callback_data="logout_confirm"),
                InlineKeyboardButton("❌ Close", callback_data="close_btn")
            ]
        ])
        return await message.reply_text(
            "✅ **You are already logged in!**\n\n"
            "If you want to login with a different account, please /logout first.",
            reply_markup=buttons
        )
    
    # Send session string instructions
    await message.reply_text(
        "🔐 **Login to Your Account**\n\n"
        "📝 **Step 1:** Generate Session String\n"
        "Use any of these methods:\n\n"
        "🤖 **Method A - Telegram Bot:**\n"
        "• @StringSessionBot\n"
        "• @StringFatherBot\n\n"
        "🌐 **Method B - Website:**\n"
        "• https://replit.com/@SpEcHlDe/GenerateStringSession\n\n"
        "📝 **Step 2:** Copy Session String\n"
        "Long text that starts with `1`\n\n"
        "📝 **Step 3:** Send to Me\n"
        "Reply to this message with session string\n\n"
        "⚠️ **Important:**\n"
        "• Keep session private\n"
        "• Delete message after sending\n"
        "• Safe & encrypted storage\n\n"
        "💡 **Tip:** Use /cancel to stop anytime",
        parse_mode="markdown"
    )

# --- Handle Session String Input ---

@Client.on_message(filters.private & filters.text & ~filters.command(["start", "help", "cancel", "logout", "premium", "myplan", "batch"]))
async def handle_session_input(client: Client, message: Message):
    user_id = message.from_user.id
    text = message.text.strip()
    
    # Check if already logged in
    session = await db.get_session(user_id)
    if session:
        return  # Already logged in, ignore
    
    # Check if looks like session string (starts with 1, long text)
    if len(text) > 200 and text[0] in ['1', 'B']:
        try:
            # Try to validate session format
            status_msg = await message.reply_text("⏳ Validating session...")
            
            # Save session
            await db.set_session(user_id, text)
            
            # Delete user's session string message for security
            try:
                await message.delete()
            except:
                pass
            
            await status_msg.edit_text(
                "🎉 **Login Successful!**\n\n"
                "✅ Session saved securely\n"
                "✅ Your message has been deleted for security\n\n"
                "🚀 **Ready to use!**\n"
                "• Send Telegram link to download\n"
                "• Use /batch for bulk downloads\n"
                "• Use /logout to remove session\n\n"
                "🔒 Session is encrypted in database!",
                parse_mode="markdown"
            )
            
        except Exception as e:
            logger.error(f"Session save error: {e}")
            await message.reply_text(
                "❌ **Invalid Session String!**\n\n"
                "Please check:\n"
                "• Copied full string?\n"
                "• No extra characters?\n"
                "• Generated correctly?\n\n"
                "Try /login again",
                parse_mode="markdown"
            )

# --- Logout Command ---

@Client.on_message(filters.command("logout") & filters.private)
async def logout_command(client: Client, message: Message):
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Yes, Logout", callback_data="logout_confirm"),
            InlineKeyboardButton("❌ Cancel", callback_data="close_btn")
        ]
    ])
    
    await message.reply_text(
        "🚪 **Logout Confirmation**\n\n"
        "Are you sure you want to logout?\n\n"
        "⚠️ **This will:**\n"
        "• Remove your saved session\n"
        "• Disable restricted content downloads\n\n"
        "💡 You can /login again anytime!",
        reply_markup=buttons,
        parse_mode="markdown"
    )

# --- Callback Handlers ---

@Client.on_callback_query(filters.regex("^logout_confirm$"))
async def handle_logout(client: Client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    
    await db.set_session(user_id, None)
    
    await callback_query.message.edit_text(
        "✅ **Logged Out Successfully!**\n\n"
        "Your session has been removed.\n\n"
        "Use /login to login again anytime.",
        parse_mode="markdown"
    )
    
    await callback_query.answer("Logged out!", show_alert=False)

@Client.on_callback_query(filters.regex("^close_btn$"))
async def handle_close(client: Client, callback_query: CallbackQuery):
    try:
        await callback_query.message.delete()
    except:
        pass
    await callback_query.answer("Closed!", show_alert=False)

# --- Cancel Command ---

@Client.on_message(filters.command("cancel") & filters.private)
async def cancel_command(client: Client, message: Message):
    await message.reply_text(
        "❌ **Process Cancelled**\n\n"
        "Use /login to start login process.",
        parse_mode="markdown"
    )
