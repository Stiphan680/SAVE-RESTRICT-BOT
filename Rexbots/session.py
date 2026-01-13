# Custom Save Restricted Bot - Built-in Session Generator with OTP Resend

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import (
    SessionPasswordNeeded, PhoneCodeInvalid, PhoneCodeExpired,
    PhoneNumberInvalid, FloodWait, PasswordHashInvalid
)
from database.db import db
from config import API_ID, API_HASH
import asyncio
import time
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
        self.code_sent_time = None
        self.resend_count = 0

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
        "🔐 **Easy Login - Step 1**\n\n"
        "📱 Send your phone number with country code\n\n"
        "**Examples:**\n"
        "• India: `+919876543210`\n"
        "• USA: `+1234567890`\n"
        "• UK: `+441234567890`\n\n"
        "⚠️ **Important:**\n"
        "• Start with `+` and country code\n"
        "• No spaces or dashes\n"
        "• Your data is safe & encrypted\n\n"
        "💡 Use /cancel anytime to stop",
        parse_mode="markdown"
    )

# --- Handle Login Steps ---

@Client.on_message(filters.private & filters.text & ~filters.command(["start", "help", "cancel", "logout", "premium", "myplan"]))
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
        if not phone.startswith("+") or len(phone) < 10:
            return await message.reply_text(
                "❌ **Invalid Format!**\n\n"
                "Phone number must:\n"
                "• Start with `+` and country code\n"
                "• Be at least 10 digits\n\n"
                "📱 **Example:** `+919876543210`\n\n"
                "🔄 Try again or use /cancel",
                parse_mode="markdown"
            )
        
        status_msg = await message.reply_text("⏳ Sending OTP code...")
        
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
            state.code_sent_time = time.time()
            
            # Create resend button
            buttons = InlineKeyboardMarkup([
                [InlineKeyboardButton("🔄 Resend OTP", callback_data=f"resend_otp_{user_id}")]
            ])
            
            await status_msg.edit_text(
                "✅ **OTP Sent Successfully!**\n\n"
                "📝 **Step 2:** Enter the OTP code\n\n"
                f"📱 Check Telegram on **{phone}**\n"
                "📧 Or check SMS on your device\n\n"
                "⏰ **You have 3-5 minutes**\n\n"
                "💡 **Just send the code:**\n"
                "Example: `12345` (only numbers)\n\n"
                "⚠️ If code doesn't arrive, click Resend below",
                reply_markup=buttons,
                parse_mode="markdown"
            )
            
        except PhoneNumberInvalid:
            await status_msg.edit_text(
                "❌ **Invalid Phone Number!**\n\n"
                "Please verify:\n"
                "• Correct country code?\n"
                "• Active Telegram number?\n"
                "• Format: `+919876543210`\n\n"
                "🔄 Send correct number or /cancel",
                parse_mode="markdown"
            )
        except FloodWait as e:
            await status_msg.edit_text(
                f"⏳ **Rate Limit!**\n\n"
                f"Too many attempts. Wait **{e.value} seconds**\n\n"
                "Then use: /cancel and /login again",
                parse_mode="markdown"
            )
        except Exception as e:
            logger.error(f"Login error (phone): {e}")
            await status_msg.edit_text(
                f"❌ **Error:** Unable to send OTP\n\n"
                "Please try again or contact admin.\n\n"
                f"Error details: `{str(e)[:100]}`",
                parse_mode="markdown"
            )
    
    # Step 2: OTP Code
    elif state.step == "code":
        code = message.text.strip().replace(" ", "").replace("-", "")
        
        # Validate code format
        if not code.isdigit() or len(code) < 5:
            return await message.reply_text(
                "⚠️ **Invalid Code Format!**\n\n"
                "OTP should be:\n"
                "• Only numbers (5-6 digits)\n"
                "• No spaces or dashes\n\n"
                "📝 Example: `12345`\n\n"
                "🔄 Check and send again",
                parse_mode="markdown"
            )
        
        status_msg = await message.reply_text("⏳ Verifying code...")
        
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
            
            await status_msg.edit_text(
                "🎉 **Login Successful!**\n\n"
                "✅ Session saved securely\n"
                "✅ Ready to download restricted content\n\n"
                "🚀 **Start Using:**\n"
                "• Send any Telegram link\n"
                "• Use /batch for bulk downloads\n"
                "• Use /logout to remove session\n\n"
                "🔒 Your session is encrypted!",
                parse_mode="markdown"
            )
            
        except SessionPasswordNeeded:
            # 2FA enabled - need password
            state.step = "password"
            await status_msg.edit_text(
                "🔐 **2FA Enabled**\n\n"
                "📝 **Step 3:** Enter Cloud Password\n\n"
                "🔑 This is your Two-Step Verification password\n\n"
                "⚠️ We don't store passwords\n"
                "💡 Forgot? Reset in Telegram Settings",
                parse_mode="markdown"
            )
            
        except PhoneCodeInvalid:
            # Create resend button
            buttons = InlineKeyboardMarkup([
                [InlineKeyboardButton("🔄 Resend OTP", callback_data=f"resend_otp_{user_id}")]
            ])
            
            await status_msg.edit_text(
                "❌ **Wrong OTP Code!**\n\n"
                "Please check:\n"
                "• Copied correctly?\n"
                "• Latest code?\n"
                "• No extra characters?\n\n"
                "📝 Format: `12345`\n\n"
                "🔄 Send code again or click Resend",
                reply_markup=buttons,
                parse_mode="markdown"
            )
            
        except PhoneCodeExpired:
            # Offer to resend
            buttons = InlineKeyboardMarkup([
                [InlineKeyboardButton("🔄 Get New OTP", callback_data=f"resend_otp_{user_id}")],
                [InlineKeyboardButton("❌ Cancel", callback_data="close_btn")]
            ])
            
            await status_msg.edit_text(
                "⏱️ **OTP Expired!**\n\n"
                "The code has timed out.\n\n"
                "🔄 Click 'Get New OTP' to receive a fresh code\n\n"
                "Or /cancel and /login again",
                reply_markup=buttons,
                parse_mode="markdown"
            )
            
        except Exception as e:
            logger.error(f"Login error (code): {e}")
            await status_msg.edit_text(
                f"❌ **Verification Error**\n\n"
                "Unable to verify code.\n\n"
                "🔄 Try again or /cancel and /login fresh\n\n"
                f"Error: `{str(e)[:100]}`",
                parse_mode="markdown"
            )
    
    # Step 3: 2FA Password
    elif state.step == "password":
        password = message.text.strip()
        
        status_msg = await message.reply_text("⏳ Checking password...")
        
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
            
            await status_msg.edit_text(
                "🎉 **Login Successful!**\n\n"
                "✅ Session saved with 2FA\n"
                "✅ Fully authenticated\n\n"
                "🚀 **Ready!** Send links to download!",
                parse_mode="markdown"
            )
            
        except PasswordHashInvalid:
            await status_msg.edit_text(
                "❌ **Wrong Password!**\n\n"
                "🔄 Try again\n"
                "🚪 /cancel to stop\n\n"
                "💡 Reset: Telegram Settings → Privacy & Security → Two-Step Verification",
                parse_mode="markdown"
            )
            
        except Exception as e:
            logger.error(f"Login error (password): {e}")
            await state.client.disconnect()
            del login_states[user_id]
            await status_msg.edit_text(
                f"❌ **Error:** Password verification failed\n\n"
                "Use /login to try again",
                parse_mode="markdown"
            )

# --- Resend OTP Callback ---

@Client.on_callback_query(filters.regex("^resend_otp_"))
async def resend_otp_callback(client: Client, callback_query):
    user_id = int(callback_query.data.split("_")[-1])
    
    # Security check
    if callback_query.from_user.id != user_id:
        return await callback_query.answer("❌ Not authorized!", show_alert=True)
    
    if user_id not in login_states:
        return await callback_query.answer("❌ Login session expired. Use /login", show_alert=True)
    
    state = login_states[user_id]
    
    # Rate limit check
    if state.code_sent_time and (time.time() - state.code_sent_time) < 30:
        remaining = 30 - int(time.time() - state.code_sent_time)
        return await callback_query.answer(
            f"⏳ Please wait {remaining} seconds before resending",
            show_alert=True
        )
    
    try:
        # Resend code
        sent_code = await state.client.send_code(state.phone)
        state.phone_code_hash = sent_code.phone_code_hash
        state.code_sent_time = time.time()
        state.resend_count += 1
        
        await callback_query.answer("✅ New OTP sent!", show_alert=False)
        
        await callback_query.message.edit_text(
            f"✅ **New OTP Sent! (Resend #{state.resend_count})**\n\n"
            f"📱 Check Telegram on **{state.phone}**\n\n"
            "📝 Send the new code when you receive it\n\n"
            "⏰ Valid for 3-5 minutes",
            parse_mode="markdown"
        )
        
    except FloodWait as e:
        await callback_query.answer(
            f"⏳ Too many requests! Wait {e.value}s",
            show_alert=True
        )
    except Exception as e:
        logger.error(f"Resend OTP error: {e}")
        await callback_query.answer("❌ Failed to resend. Try /login again", show_alert=True)

# --- Cancel & Logout (same as before) ---

@Client.on_message(filters.command("cancel") & filters.private)
async def cancel_login(client: Client, message: Message):
    user_id = message.from_user.id
    
    if user_id in login_states:
        state = login_states[user_id]
        
        if state.client:
            try:
                await state.client.disconnect()
            except:
                pass
        
        del login_states[user_id]
        
        await message.reply_text(
            "❌ **Login Cancelled**\n\n"
            "Use /login to start again anytime.",
            parse_mode="markdown"
        )
    else:
        await message.reply_text("No active process to cancel.")

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
        "Remove your saved session?\n\n"
        "⚠️ You'll need to /login again",
        reply_markup=buttons,
        parse_mode="markdown"
    )

@Client.on_callback_query(filters.regex("logout_confirm"))
async def handle_logout(client: Client, callback_query):
    user_id = callback_query.from_user.id
    
    await db.set_session(user_id, None)
    
    await callback_query.message.edit_text(
        "✅ **Logged Out!**\n\n"
        "Session removed successfully.\n\n"
        "Use /login anytime to login again.",
        parse_mode="markdown"
    )
    
    await callback_query.answer("Logged out!", show_alert=False)
