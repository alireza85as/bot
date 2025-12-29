import os
import threading
import requests
from flask import Flask
import telebot
from bs4 import BeautifulSoup
from apscheduler.schedulers.background import BackgroundScheduler
from zoneinfo import ZoneInfo

TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")   # مثل @mychannel یا -100xxxxxxxx
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

URL = "https://www.tgju.org/profile/price_dollar_rl"
HEADERS = {"User-Agent": "Mozilla/5.0"}


def get_dollar_price():
    r = requests.get(URL, headers=HEADERS, timeout=10)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")

    t = soup.find(attrs={"itemprop": "price"})
    if t:
        return (t.get("content") or t.text).strip()

    d = soup.find(attrs={"data-price": True})
    if d:
        return d["data-price"]

    s = soup.select_one("span.price, span.value")
    if s:
        return s.text.strip()

    return None


def send_price_to_channel():
    try:
        price = get_dollar_price()

        if price:
            bot.send_message(
                CHANNEL_ID,
                f"💵 قیمت دلار آزاد (لحظه‌ای):\n\n{price} تومان"
            )
        else:
            bot.send_message(
                CHANNEL_ID,
                "❗️ نتوانستم قیمت دلار را دریافت کنم."
            )

    except Exception as e:
        print("ERROR:", e)


@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "ربات فعال است و هر ۳۰ دقیقه قیمت دلار را در کانال ارسال می‌کند.")


@app.route("/")
def home():
    return "Bot is running!"


if __name__ == "__main__":
    # راه‌اندازی ارسال زمان‌بندی شده
    scheduler = BackgroundScheduler(timezone=ZoneInfo("Asia/Tehran"))

    # هر روز، هر ۳۰ دقیقه (دقیقه های 0 و 30)
    scheduler.add_job(
        send_price_to_channel,
        'cron',
        minute='0,30'
    )

    scheduler.start()

    # Polling تلگرام
    t = threading.Thread(target=bot.infinity_polling, daemon=True)
    t.start()

    # Flask
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
