import time
import feedparser
import requests
import threading
from flask import Flask
import html
from googletrans import Translator  # إضافة الترجمة

# -----------------------------
# إعدادات البوت و Telegram
# -----------------------------
TELEGRAM_TOKEN = "8185068243:AAHn7U1zyyjq4NH-MqVsC2Z3JcQghwrwkgg"
TELEGRAM_CHAT_ID = "@OnyDiwaniya"
CHANNEL_LINK = "https://t.me/OnyDiwaniya"

# -----------------------------
# مصادر أخبار الفوركس
# -----------------------------
RSS_FEEDS = [
    "https://www.investing.com/rss/news.rss",
    "https://www.dailyfx.com/feeds/forex.xml",
    "https://www.fxstreet.com/rss/news"
]

# -----------------------------
# الكلمات المفتاحية للفوركس
# -----------------------------
FOREX_KEYWORDS = [
    "forex", "currency", "exchange rate",
    "usd", "dollar",
    "eur", "euro",
    "gbp", "pound", "sterling",
    "jpy", "yen",
    "chf", "swiss franc",
    "cad", "loonie",
    "aud", "aussie",
    "nzd", "kiwi",
    "central bank", "interest rate", "monetary policy"
]

IGNORE_KEYWORDS = ["lottery", "jackpot", "crypto", "bitcoin", "lotto"]

posted_urls = set()
translator = Translator()

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

def summarize_text(text, max_words=25):
    words = text.split()
    if len(words) <= max_words:
        return text
    return ' '.join(words[:max_words]) + "..."

def translate_text(text, dest="ar"):
    try:
        return translator.translate(text, dest=dest).text
    except Exception as e:
        print("Translation error:", e)
        return text  # fallback للنص الأصلي

def get_news():
    entries = []
    for feed_url in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            entries.extend(feed.entries)
        except Exception as e:
            print("Feed error:", e)
    return entries

# -----------------------------
# فلترة أخبار الفوركس فقط
# -----------------------------
def is_forex_related(title):
    title_lower = title.lower()
    if any(word in title_lower for word in IGNORE_KEYWORDS):
        return False
    return any(keyword in title_lower for keyword in FOREX_KEYWORDS)

# -----------------------------
# تشغيل البوت
# -----------------------------
def run_bot():
    send_telegram("✅ Bot started. Tracking Forex news with translation...")
    while True:
        news = get_news()
        for article in news:
            title = article.title
            link = article.link
            description = getattr(article, "summary", "")

            if link not in posted_urls and is_forex_related(title):
                summary = summarize_text(description)

                # ترجمة العنوان والملخص
                translated_title = translate_text(title)
                translated_summary = translate_text(summary)

                msg = (
                    f"💹 <b>{html.escape(translated_title)}</b>\n"
                    f"{html.escape(translated_summary)}\n"
                    f"🔗 <a href='{CHANNEL_LINK}'>قناتنا</a>"
                )
                send_telegram(msg)
                posted_urls.add(link)
                time.sleep(2)

        time.sleep(600)

# -----------------------------
# Web Service باستخدام Flask
# -----------------------------
app = Flask(__name__)
threading.Thread(target=run_bot).start()

@app.route("/")
def home():
    return "Forex Bot with Translation is running ✅"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
