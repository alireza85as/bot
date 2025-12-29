import os
import threading
import requests
from flask import Flask
import telebot
from bs4 import BeautifulSoup

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

URL = "https://www.tgju.org/profile/price_dollar_rl"
HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def get_dollar_price():
    r = requests.get(URL, headers=HEADERS, timeout=10)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")

    # 1) معمولا قیمت داخل itemprop=price است
    t = soup.find(attrs={"itemprop": "price"})
    if t:
        return (t.get("content") or t.text).strip()

    # 2) fallback: اگر data-price داشت
    d = soup.find(attrs={"data-price": True})
    if d:
        return d["data-price"]

    # 3) آخرین راه‌حل
    s = soup.select_one("span.price, span.value")
    if s:
        return s.text.strip()

    return None


@bot.message_handler(commands=['start'])
def start(message):
    price = get_dollar_price()

    if price:
        bot.reply_to(
            message,
            f"💵 قیمت دلار آزاد (لحظه‌ای):\n\n{price} تومان"
        )
    else:
        bot.reply_to(
            message,
            "متاسفانه نتونستم قیمت دلار رو دریافت کنم. لطفاً بعداً دوباره امتحان کن."
        )


@bot.message_handler(func=lambda m: True)
def echo(message):
    bot.reply_to(message, "برای دریافت قیمت دلار دستور /start را ارسال کن.")


@app.route("/")
def home():
    return "Telegram Bot is running!"


if __name__ == "__main__":
    t = threading.Thread(target=bot.infinity_polling, daemon=True)
    t.start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
