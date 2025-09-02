from flask import Flask
import threading
import time
import feedparser
import requests
from deep_translator import GoogleTranslator

# -----------------------------
# إعدادات البوت
# -----------------------------
TELEGRAM_TOKEN = "8185068243:AAHn7U1zyyjq4NH-MqVsC2Z3JcQghwrwkgg"
TELEGRAM_CHAT_ID = "@OnyDiwaniya"
RSS_URL = "https://www.marketwatch.com/rss/topstories/metals"
KEYWORDS = ["gold", "XAU", "USD", "interest rate", "inflation", "market", "central bank"]

# -----------------------------
# دوال البوت
# -----------------------------
def send_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "HTML"}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print("Telegram error:", e)

def translate_to_arabic(text):
    try:
        return GoogleTranslator(source='auto', target='ar').translate(text)
    except Exception as e:
        print("Translation error:", e)
        return text

def get_news():
    feed = feedparser.parse(RSS_URL)
    return feed.entries

def contains_keywords(title):
    return any(keyword.lower() in title.lower() for keyword in KEYWORDS)

posted_urls = set()

def run_bot():
    send_telegram("✅ بوت الأخبار الاقتصادية متصل وجاهز.")
    while True:
        news = get_news()
        for article in news:
            title = article.title
            link = article.link
            if link not in posted_urls and contains_keywords(title):
                translated_title = translate_to_arabic(title)
                msg = f"📰 {translated_title}"  # بدون الرابط
                send_telegram(msg)
                posted_urls.add(link)
        time.sleep(600)  # كل 10 دقائق

# -----------------------------
# إعداد Flask لتشغيل Web Service
# -----------------------------
app = Flask(__name__)

# تشغيل البوت في Thread منفصل
threading.Thread(target=run_bot).start()

@app.route("/")
def home():
    return "Bot is running"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
