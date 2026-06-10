import os
import time
import threading
import requests
from flask import Flask
import telebot
from bs4 import BeautifulSoup
from apscheduler.schedulers.background import BackgroundScheduler
from zoneinfo import ZoneInfo

TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

URL = "https://www.tgju.org/profile/price_dollar_rl"
HEADERS = {"User-Agent": "Mozilla/5.0"}


def get_dollar_price():
    r = requests.get(URL, headers=HEADERS, timeout=10)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")

    # حالت‌های مختلف گرفتن قیمت
    t = soup.find(attrs={"itemprop": "price"})
    if t:
        rial = (t.get("content") or t.text).strip()
    else:
        d = soup.find(attrs={"data-price": True})
        if d:
            rial = d["data-price"]
        else:
            s = soup.select_one("span.price, span.value")
            if s:
                rial = s.text.strip()
            else:
                return None

    # پاکسازی
    rial = rial.replace(",", "").replace(" ", "")

    
    toman = round(int(rial) / 10)

    return toman


def send_price_to_channel():
    try:
        price = get_dollar_price()

        if price:
            time.sleep(3)
            bot.send_message(
                CHANNEL_ID,
                f"🔖 قیمت دلار:\n\n📥 دلار آزاد {price:,} تومان 💵"
            )
        else:
            print("❗️ نتوانستم قیمت دلار را دریافت کنم.")
            

    except Exception as e:
        print("ERROR:", e)


@bot.message_handler(commands=['start'])
def start(message):
    price = get_dollar_price()
    time.sleep(3)
    bot.reply_to(
        message,
                f"🔖 قیمت دلار:\n\n📥 دلار آزاد {price:,} تومان 💵"
            )


@app.route("/")
def home():
    return "Bot is running!"


if __name__ == "__main__":
    # زمان‌بندی بر اساس ساعت ایران
    scheduler = BackgroundScheduler(timezone=ZoneInfo("Asia/Tehran"))

    scheduler.add_job(
        send_price_to_channel,
        'cron',
        minute='0'
    )

    scheduler.start()
    
    t = threading.Thread(target=bot.infinity_polling, daemon=True)
    t.start()

    # Flask
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
