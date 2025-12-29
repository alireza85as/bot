import telebot
from flask import Flask
import os

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)

@app.route("/")
def home():
    return "Telegram Bot is running!"

@bot.message_handler(func=lambda m: True)
def echo(message):
    bot.reply_to(message, "سلام! پیام‌ت رسید.")

if __name__ == "__main__":
    import threading
    t = threading.Thread(target=bot.infinity_polling)
    t.start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
