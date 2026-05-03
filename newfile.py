import json
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters

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

# এটি মেনু কিবোর্ড তৈরি করবে যা সবসময় নিচে থাকবে
def main_menu_keyboard():
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
                
