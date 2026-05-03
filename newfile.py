import json
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

# --- CONFIGURATION ---
TOKEN = "8510852001:AAGvKEQt5yrXSfU5KoyHU2bn8l6drfd-yz8"
ADMIN_USERNAME = "@TRUST_BUY_SELL_BD" 
CHANNEL_LINK = "@ONLINE_INCOME_ZONE_24X"
PAYMENT_PROOF_CHANNEL = "@RS_SOCIAL_SERVICE_0" 
TWITTER_LINK = "https://x.com/CryptoA19075"
REFER_BONUS = 0.04               
MIN_WITHDRAW = 0.35              

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

# এটি নিচের স্থায়ী মেনু কিবোর্ড তৈরি করবে
def main_menu():
    keyboard = [
        ['💰 Balance', '👫 Refer & Earn'],
        ['📝 Tasks', '💳 Withdraw']
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

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

    welcome_text = f"Hello {name}! 👋\nWelcome to TaskToEarn.\n\nUse the menu buttons below to navigate."
    await update.message.reply_text(welcome_text, reply_markup=main_menu())

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    text = update.message.text

    if user_id not in users:
        return

    # ১. ব্যালেন্স বাটন
    if text == '💰 Balance':
        bal = users[user_id]['balance']
        await update.message.reply_text(f"💵 Your Current Balance: {bal} USDT")
    
    # ২. রেফার বাটন
    elif text == '👫 Refer & Earn':
        link = f"https://t.me/tasktoearn_official_bot?start={user_id}"
        await update.message.reply_text(f"🔗 Your Referral Link:\n{link}\n\nEarn {REFER_BONUS} USDT per refer! 💸")

    # ৩. টাস্ক বাটন
    elif text == '📝 Tasks':
        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("Follow on X", url=TWITTER_LINK)],
            [InlineKeyboardButton("Join Channel", url=f"https://t.me/{CHANNEL_LINK.replace('@','')}")]
        ])
        await update.message.reply_text(f"📝 Complete the tasks below:", reply_markup=markup)

    # ৪. উইথড্র বাটন
    elif text == '💳 Withdraw':
        bal = users[user_id]['balance']
        if bal >= MIN_WITHDRAW:
            users[user_id]["awaiting_address"] = True
            save_data(users)
            await update.message.reply_text(f"✅ Your Balance: {bal} USDT\nPlease send your **TON Wallet Address**:")
        else:
            await update.message.reply_text(f"❌ Minimum withdraw is {MIN_WITHDRAW} USDT. You need {round(MIN_WITHDRAW - bal, 2)} USDT more.")

    # ৫. ওয়ালেট অ্যাড্রেস ইনপুট নেওয়া
    elif users[user_id].get("awaiting_address"):
        address = text
        bal = users[user_id]['balance']
        users[user_id]["awaiting_address"] = False
        save_data(users)

        await update.message.reply_text(f"✅ Withdrawal Request Submitted!\nCheck status here: {PAYMENT_PROOF_CHANNEL}")

        proof_text = (
            "🚀 **NEW WITHDRAWAL REQUEST**\n\n"
            f"👤 **User:** {update.effective_user.first_name}\n"
            f"💰 **Amount:** {bal} USDT\n"
            f"📍 **Network:** TON\n"
            f"🔑 **Address:** `{address}`\n"
            f"🛠 **Status:** ⏳ Pending Review"
        )
        try:
            await context.bot.send_message(chat_id=PAYMENT_PROOF_CHANNEL, text=proof_text, parse_mode='Markdown')
        except: pass

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    # সব টেক্সট মেসেজ হ্যান্ডেল করার জন্য
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("Bot is running perfectly...")
    app.run_polling()
    
