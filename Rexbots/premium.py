# Custom Save Restricted Bot

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from database.db import db
from config import ERROR_MESSAGE, ADMINS, ADMIN_USERNAME
import datetime
import asyncio
from logger import LOGGER

logger = LOGGER(__name__)

# --- User Commands ---

@Client.on_message(filters.command("myplan") & filters.private)
async def myplan(client: Client, message: Message):
    expiry = await db.check_premium(message.from_user.id)
    if expiry:
        # Check if expired
        try:
            exp_date = datetime.datetime.fromisoformat(expiry)
            if datetime.datetime.now() > exp_date:
                await db.remove_premium(message.from_user.id)
                return await message.reply_text("**__Your Premium Plan has expired.__** 😞\n\nUse /premium to buy a new plan.")
            
            time_left = exp_date - datetime.datetime.now()
            days = time_left.days
            await message.reply_text(f"**🌟 Premium User**\n\n**Expiry:** `{exp_date.strftime('%Y-%m-%d %H:%M:%S')}`\n**Days Left:** `{days}` Days")
        except:
             await message.reply_text(f"**🌟 Premium User**\n\n**Expiry:** `{expiry}`")
    else:
        await message.reply_text("**__You are currently on the Free Plan.__**\n\nUse /premium to upgrade.")

@Client.on_message(filters.command("premium") & filters.private)
async def buy_premium(client: Client, message: Message):
    text = (
        "<b>💎 Premium Plans - Unlimited Access!</b>\n\n"
        "<blockquote><b>✨ Premium Benefits:</b>\n"
        "<b>• ♾️ Unlimited Downloads</b>\n"
        "<b>• ⚡ Fastest Download Speed</b>\n"
        "<b>• 📦 Batch/Bulk Download</b>\n"
        "<b>• 📝 Custom Caption & Thumbnail</b>\n"
        "<b>• 🚀 Priority Support</b>\n"
        "<b>• 🚫 No Cooldowns</b></blockquote>\n\n"
        "<b>💰 Pricing (India):</b>\n"
        "<blockquote>📌 <b>1 Month</b> - ₹99\n"
        "📌 <b>3 Months</b> - ₹249 <i>(Save 17%)</i>\n"
        "📌 <b>6 Months</b> - ₹449 <i>(Save 25%)</i>\n"
        "📌 <b>1 Year</b> - ₹799 <i>(Save 33%)</i></blockquote>\n\n"
        f"<b>💳 Payment Methods:</b>\n"
        "<blockquote>• UPI / PhonePe / Paytm\n"
        "• Google Pay / BHIM\n"
        "• Bank Transfer</blockquote>\n\n"
        f"<b>👤 Contact Admin:</b> {ADMIN_USERNAME}\n\n"
        "<blockquote><b>⚠️ How to Buy:</b>\n"
        f"1️⃣ Message {ADMIN_USERNAME}\n"
        "2️⃣ Choose your plan\n"
        "3️⃣ Make payment via UPI\n"
        "4️⃣ Send payment screenshot\n"
        "5️⃣ Get instant premium activation! 🎉</blockquote>"
    )
    
    # Button to contact admin
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("💬 Contact Admin", url=f"https://t.me/{ADMIN_USERNAME.replace('@', '')}")
        ],
        [
            InlineKeyboardButton("❌ Close", callback_data="close_btn")
        ]
    ])
    
    await message.reply_text(text, reply_markup=buttons, parse_mode="html")

# --- Admin Commands ---

@Client.on_message(filters.command("add_premium") & filters.user(ADMINS))
async def add_premium_cmd(client: Client, message: Message):
    if len(message.command) < 3:
        return await message.reply_text("**Usage:** `/add_premium user_id days`")
    
    try:
        user_id = int(message.command[1])
        days = int(message.command[2])
        expiry_date = datetime.datetime.now() + datetime.timedelta(days=days)
        
        await db.add_premium(user_id, expiry_date.isoformat())
        await message.reply_text(f"✅ **User `{user_id}` added to Premium for {days} days.**\n\n**Expiry:** `{expiry_date.strftime('%Y-%m-%d %H:%M:%S')}`")
        
        try:
            await client.send_message(
                user_id, 
                f"🎉 **Congratulations!**\n\n"
                f"You have been upgraded to **Premium** for **{days} days**.\n\n"
                f"✨ Enjoy unlimited downloads and premium features!\n\n"
                f"**Expiry:** `{expiry_date.strftime('%Y-%m-%d %H:%M:%S')}`"
            )
        except:
            pass
            
    except Exception as e:
        logger.error(f"Error adding premium: {e}")
        await message.reply_text(f"Error: {e}")

@Client.on_message(filters.command("remove_premium") & filters.user(ADMINS))
async def remove_premium_cmd(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("**Usage:** `/remove_premium user_id`")
    
    try:
        user_id = int(message.command[1])
        await db.remove_premium(user_id)
        await message.reply_text(f"✅ **User `{user_id}` removed from Premium.**")
        
        try:
            await client.send_message(user_id, "❌ **Your Premium Plan has been revoked by Admin.**")
        except:
            pass

    except Exception as e:
        logger.error(f"Error removing premium: {e}")
        await message.reply_text(f"Error: {e}")

@Client.on_message(filters.command("premium_users") & filters.user(ADMINS))
async def premium_users_list(client: Client, message: Message):
    users = await db.get_premium_users()
    count = 0
    text = "**💎 Premium Users List:**\n\n"
    async for user in users:
        text += f"`{user['id']}` - Exp: {user.get('premium_expiry', 'Unknown')}\n"
        count += 1
    
    if count == 0:
        text += "No premium users found."
    else:
        text += f"\n**Total Premium Users:** {count}"
        
    await message.reply_text(text)
