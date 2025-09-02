import time
import feedparser
import requests
from googletrans import Translator
import html
import threading

# -----------------------------
# إعدادات البوت و Telegram
# -----------------------------
TELEGRAM_TOKEN = "8185068243:AAHn7U1zyyjq4NH-MqVsC2Z3JcQghwrwkgg"
TELEGRAM_CHAT_ID = "@OnyDiwaniya"
RSS_URL = "https://www.marketwatch.com/rss/topstories/metals"
CHANNEL_LINK = "https://t.me/OnyDiwaniya"

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

def translate_to_arabic(text):
    for _ in range(3):
        try:
            translated = translator.translate(text, src='en', dest='ar').text
            return html.escape(translated)
        except Exception as e:
            print("Translation error:", e)
            time.sleep(1)
    return html.escape(text)

def summarize_text(text, max_words=20):
    # ملخص بسيط: أول n كلمات
    words = text.split()
    if len(words) <= max_words:
        return text
    return ' '.join(words[:max_words]) + "..."

def get_news():
    feed = feedparser.parse(RSS_URL)
    return feed.entries

posted_urls = set()

def run_bot():
    send_telegram("✅ بوت الأخبار الاقتصادية متصل وجاهز.")
    while True:
        news = get_news()
        for article in news:
            title = article.title
            link = article.link
            description = getattr(article, "summary", "")
            
            if link not in posted_urls:
                translated_title = translate_to_arabic(title)
                translated_summary = translate_to_arabic(summarize_text(description, max_words=25))
                
                # إشعار للأخبار المهمة (مثال: الذهب أو الدولار)
                if "Gold" in title or "XAUUSD" in title:
                    alert_icon = "🟢🔥"
                else:
                    alert_icon = "📰"
                
                msg = f"{alert_icon} <b>{translated_title}</b>\n{translated_summary}\n🔗 <a href='{CHANNEL_LINK}'>قناتنا</a>"
                send_telegram(msg)
                posted_urls.add(link)
                
                time.sleep(2)  # لتخفيف الضغط على Telegram API
        time.sleep(600)  # تحقق كل 10 دقائق

# -----------------------------
# Web Service باستخدام Flask
# -----------------------------
from flask import Flask
app = Flask(__name__)
threading.Thread(target=run_bot).start()  # تشغيل البوت في Thread مستقل

@app.route("/")
def home():
    return "Bot is running ✅"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
