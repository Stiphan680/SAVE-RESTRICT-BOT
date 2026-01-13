# Custom Save Restricted Bot - Built-in Session Generator

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import (
    SessionPasswordNeeded, PhoneCodeInvalid, PhoneCodeExpired,
    PhoneNumberInvalid, FloodWait, PasswordHashInvalid
)
from database.db import db
from config import API_ID, API_HASH
import asyncio
from logger import LOGGER

logger = LOGGER(__name__)

# Store temporary login states
login_states = {}

class LoginState:
    def __init__(self):
        self.phone = None
        self.phone_code_hash = None
        self.client = None
        self.step = "phone"  # phone, code, password, done

# --- Login Command ---

@Client.on_message(filters.command("login") & filters.private)
async def login_command(client: Client, message: Message):
    user_id = message.from_user.id
    
    # Check if already logged in
    session = await db.get_session(user_id)
    if session:
        buttons = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🚪 Logout", callback_data="logout_confirm"),
                InlineKeyboardButton("❌ Cancel", callback_data="close_btn")
            ]
        ])
        return await message.reply_text(
            "✅ **You are already logged in!**\n\n"
            "If you want to login with a different account, please /logout first.",
            reply_markup=buttons
        )
    
    # Start login process
    login_states[user_id] = LoginState()
    
    await message.reply_text(
        "🔐 **Login to Your Telegram Account**\n\n"
        "**Step 1/3:** Send your phone number with country code\n\n"
        "📱 **Format:** `+919876543210`\n"
        "🌍 **Example:** `+1234567890` (USA), `+919876543210` (India)\n\n"
        "⚠️ **Important:**\n"
        "• Include country code (+91 for India)\n"
        "• No spaces or special characters\n"
        "• This is safe - we don't store your password\n\n"
        "💡 **Tip:** Use /cancel to stop login process anytime.",
        parse_mode="markdown"
    )

# --- Handle Phone Number ---

@Client.on_message(filters.private & filters.text & ~filters.command(["start", "help", "cancel", "logout"]))
async def handle_login_steps(client: Client, message: Message):
    user_id = message.from_user.id
    
    # Check if user is in login process
    if user_id not in login_states:
        return
    
    state = login_states[user_id]
    
    # Step 1: Phone Number
    if state.step == "phone":
        phone = message.text.strip()
        
        # Validate phone format
        if not phone.startswith("+"):
            return await message.reply_text(
                "❌ **Invalid Format!**\n\n"
                "Phone number must start with country code.\n\n"
                "📱 **Example:** `+919876543210`\n\n"
                "Try again or use /cancel to stop.",
                parse_mode="markdown"
            )
        
        try:
            # Create temporary client
            temp_client = Client(
                f"login_{user_id}",
                api_id=API_ID,
                api_hash=API_HASH,
                phone_number=phone,
                in_memory=True
            )
            
            await temp_client.connect()
            
            # Send code
            sent_code = await temp_client.send_code(phone)
            state.phone = phone
            state.phone_code_hash = sent_code.phone_code_hash
            state.client = temp_client
            state.step = "code"
            
            await message.reply_text(
                "✅ **OTP Sent Successfully!**\n\n"
                "**Step 2/3:** Enter the OTP code\n\n"
                f"📱 Check Telegram messages on **{phone}**\n"
                "📧 Or check SMS if you're using a different device\n\n"
                "⏰ **You have 2-3 minutes** to enter the code\n\n"
                "💡 **Tip:** Code format: `12345` (just numbers, no spaces)",
                parse_mode="markdown"
            )
            
        except PhoneNumberInvalid:
            await message.reply_text(
                "❌ **Invalid Phone Number!**\n\n"
                "Please check:\n"
                "• Correct country code?\n"
                "• Number is active?\n"
                "• Format: `+919876543210`\n\n"
                "Try again or /cancel to stop.",
                parse_mode="markdown"
            )
        except FloodWait as e:
            await message.reply_text(
                f"⏳ **Too Many Attempts!**\n\n"
                f"Please wait **{e.value} seconds** and try again.\n\n"
                "Use /cancel and then /login after waiting.",
                parse_mode="markdown"
            )
        except Exception as e:
            logger.error(f"Login error (phone): {e}")
            await message.reply_text(
                f"❌ **Error:** {str(e)}\n\n"
                "Please try again or contact admin.",
                parse_mode="markdown"
            )
    
    # Step 2: OTP Code
    elif state.step == "code":
        code = message.text.strip().replace(" ", "").replace("-", "")
        
        try:
            # Sign in with code
            await state.client.sign_in(state.phone, state.phone_code_hash, code)
            
            # Success! Export session
            session_string = await state.client.export_session_string()
            
            # Save to database
            await db.set_session(user_id, session_string)
            
            # Disconnect temp client
            await state.client.disconnect()
            
            # Clear login state
            del login_states[user_id]
            
            await message.reply_text(
                "🎉 **Login Successful!**\n\n"
                "✅ Your session has been saved securely\n"
                "✅ You can now download restricted content\n\n"
                "🚀 **What's Next?**\n"
                "• Send any Telegram link to download\n"
                "• Use /batch for bulk downloads\n"
                "• Use /logout to remove your session\n\n"
                "💡 Your session is encrypted and safe!",
                parse_mode="markdown"
            )
            
        except SessionPasswordNeeded:
            # 2FA enabled - need password
            state.step = "password"
            await message.reply_text(
                "🔐 **2FA Password Required**\n\n"
                "**Step 3/3:** Enter your Cloud Password\n\n"
                "🔑 This is the password you set for Two-Step Verification\n\n"
                "⚠️ **Note:** We don't store your password\n"
                "💡 If you forgot, use /cancel and reset via Telegram settings",
                parse_mode="markdown"
            )
            
        except PhoneCodeInvalid:
            await message.reply_text(
                "❌ **Invalid OTP Code!**\n\n"
                "Please check and try again:\n"
                "• Code copied correctly?\n"
                "• No extra spaces?\n"
                "• Code format: `12345`\n\n"
                "⏰ Send the code again (you have time!)",
                parse_mode="markdown"
            )
            
        except PhoneCodeExpired:
            await state.client.disconnect()
            del login_states[user_id]
            await message.reply_text(
                "⏱️ **OTP Expired!**\n\n"
                "The code has expired. Please start again:\n\n"
                "Use /login to get a fresh OTP",
                parse_mode="markdown"
            )
            
        except Exception as e:
            logger.error(f"Login error (code): {e}")
            await message.reply_text(
                f"❌ **Error:** {str(e)}\n\n"
                "Please use /login to start again.",
                parse_mode="markdown"
            )
    
    # Step 3: 2FA Password (if needed)
    elif state.step == "password":
        password = message.text.strip()
        
        try:
            # Check password
            await state.client.check_password(password)
            
            # Export session
            session_string = await state.client.export_session_string()
            
            # Save to database
            await db.set_session(user_id, session_string)
            
            # Disconnect
            await state.client.disconnect()
            
            # Clear state
            del login_states[user_id]
            
            await message.reply_text(
                "🎉 **Login Successful!**\n\n"
                "✅ Your session has been saved securely\n"
                "✅ 2FA verified successfully\n\n"
                "🚀 **Ready to use!**\n"
                "Send any Telegram link to start downloading!",
                parse_mode="markdown"
            )
            
        except PasswordHashInvalid:
            await message.reply_text(
                "❌ **Wrong Password!**\n\n"
                "Please try again or:\n"
                "• /cancel to stop\n"
                "• Reset password in Telegram Settings → Privacy",
                parse_mode="markdown"
            )
            
        except Exception as e:
            logger.error(f"Login error (password): {e}")
            await state.client.disconnect()
            del login_states[user_id]
            await message.reply_text(
                f"❌ **Error:** {str(e)}\n\n"
                "Please use /login to try again.",
                parse_mode="markdown"
            )

# --- Cancel Login ---

@Client.on_message(filters.command("cancel") & filters.private)
async def cancel_login(client: Client, message: Message):
    user_id = message.from_user.id
    
    if user_id in login_states:
        state = login_states[user_id]
        
        # Disconnect client if exists
        if state.client:
            try:
                await state.client.disconnect()
            except:
                pass
        
        # Clear state
        del login_states[user_id]
        
        await message.reply_text(
            "❌ **Login Process Cancelled**\n\n"
            "Use /login to start again anytime.",
            parse_mode="markdown"
        )
    else:
        await message.reply_text("No active login process to cancel.")

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
        "• You won't be able to download restricted content\n"
        "• You'll need to /login again to use the bot\n\n"
        "💡 You can login again anytime!",
        reply_markup=buttons,
        parse_mode="markdown"
    )

# Handle logout callback
@Client.on_callback_query(filters.regex("logout_confirm"))
async def handle_logout(client: Client, callback_query):
    user_id = callback_query.from_user.id
    
    await db.set_session(user_id, None)
    
    await callback_query.message.edit_text(
        "✅ **Logged Out Successfully!**\n\n"
        "Your session has been removed.\n\n"
        "Use /login to login again anytime.",
        parse_mode="markdown"
    )
    
    await callback_query.answer("Logged out successfully!", show_alert=False)
