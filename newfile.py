import json
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters

# --- CONFIGURATION ---
TOKEN = "8510852001:AAGvKEQt5yrXSfU5KoyHU2bn8l6drfd-yz8"
ADMIN_USERNAME = "@TRUST_BUY_SELL_BD" 
CHANNEL_LINK = "@ONLINE_INCOME_ZONE_24X"
PAYMENT_PROOF_CHANNEL = "@RS_SOCIAL_SERVICE_0" 
TWITTER_LINK = "https://x.com/CryptoA19075"
REFER_BONUS = 0.04               
MIN_WITHDRAW = 0.35              

# Database file
DB_FILE = "users_data.json"

def load_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            try: return json.load(f)
            except: return {}
    return {}

def save_data(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

users = load_data()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    name = update.effective_user.first_name
    
    if user_id not in users:
        users[user_id] = {"balance": 0.0, "referred_by": None, "awaiting_address": False}
        args = context.args
        if args and args[0] != user_id:
            referrer_id = args[0]
            if referrer_id in users:
                users[user_id]["referred_by"] = referrer_id
                users[referrer_id]["balance"] = round(users[referrer_id]["balance"] + REFER_BONUS, 2)
                try:
                    await context.bot.send_message(chat_id=int(referrer_id), text=f"🎊 New Referral! {name} joined. You earned {REFER_BONUS} USDT.")
                except: pass
        save_data(users)

    keyboard = [
        [InlineKeyboardButton("💰 Balance", callback_data='balance'), InlineKeyboardButton("👫 Refer & Earn", callback_data='refer')],
        [InlineKeyboardButton("📝 Tasks", callback_data='tasks'), InlineKeyboardButton("💳 Withdraw", callback_data='withdraw')],
        [InlineKeyboardButton("📢 Official Channel", url=f"https://t.me/{CHANNEL_LINK.replace('@','')}")]
    ]
    await update.message.reply_text(f"Hello {name}! 👋\nWelcome to TaskToEarn.", reply_markup=InlineKeyboardMarkup(keyboard))

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = str(query.from_user.id)
    await query.answer()

    if query.data == 'balance':
        bal = users[user_id]['balance']
        await query.message.reply_text(f"💵 Your Current Balance: {bal} USDT")
    
    elif query.data == 'refer':
        link = f"https://t.me/tasktoearn_official_bot?start={user_id}"
        await query.message.reply_text(f"🔗 Your Referral Link:\n{link}\n\nEarn {REFER_BONUS} USDT per refer! 💸")

    elif query.data == 'tasks':
        markup = InlineKeyboardMarkup([[InlineKeyboardButton("Follow on X", url=TWITTER_LINK)]])
        await query.message.reply_text(f"📝 Tasks:\n1. Follow X account\n2. Join our Telegram channel", reply_markup=markup)

    elif query.data == 'withdraw':
        bal = users[user_id]['balance']
        if bal >= MIN_WITHDRAW:
            users[user_id]["awaiting_address"] = True
            save_data(users)
            await query.message.reply_text(f"✅ Balance: {bal} USDT\nPlease send your **TON Wallet Address** (e.g., Tonkeeper):")
        else:
            await query.message.reply_text(f"❌ Minimum withdraw is {MIN_WITHDRAW} USDT. You need {round(MIN_WITHDRAW - bal, 2)} USDT more.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    name = update.effective_user.first_name
    username = update.effective_user.username or "N/A"

    if user_id in users and users[user_id].get("awaiting_address"):
        address = update.message.text
        bal = users[user_id]['balance']
        
        users[user_id]["awaiting_address"] = False
        save_data(users)

        # 1. Notify User
        await update.message.reply_text(f"✅ TON Withdrawal Request Submitted!\nCheck status here: {PAYMENT_PROOF_CHANNEL}")

        # 2. Post to Payment Proof Channel
        proof_text = (
            "🚀 **NEW WITHDRAWAL REQUEST**\n\n"
            f"👤 **User:** {name} (@{username})\n"
            f"💰 **Amount:** {bal} USDT\n"
            f"📍 **Network:** TON\n"
            f"🔑 **Address:** `{address}`\n"
            f"🛠 **Status:** ⏳ Pending Review"
        )
        try:
            await context.bot.send_message(chat_id=PAYMENT_PROOF_CHANNEL, text=proof_text, parse_mode='Markdown')
        except Exception as e:
            print(f"Error posting to channel: {e}")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("Bot is running with TON address support...")
    app.run_polling()
