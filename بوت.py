import time
import feedparser
from googletrans import Translator
import requests

# إعدادات البوت
TELEGRAM_TOKEN = "8185068243:AAHn7U1zyyjq4NH-MqVsC2Z3JcQghwrwkgg"
TELEGRAM_CHAT_ID = "@OnyDiwaniya"
RSS_URL = "https://www.marketwatch.com/rss/topstories/metals"
KEYWORDS = ["gold", "XAU", "USD", "interest rate", "inflation", "market", "central bank"]

# دالة إرسال رسالة للقناة
def send_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "HTML"}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print("Telegram error:", e)

# دالة لترجمة النصوص
def translate_to_arabic(text):
    translator = Translator()
    return translator.translate(text, src='en', dest='ar').text

# دالة لاستخراج الأخبار من RSS
def get_news():
    feed = feedparser.parse(RSS_URL)
    return feed.entries

# دالة لفحص الكلمات المفتاحية
def contains_keywords(title):
    return any(keyword.lower() in title.lower() for keyword in KEYWORDS)

# حلقة المراقبة
def run_bot():
    send_telegram("✅ بوت الأخبار الاقتصادية متصل وجاهز.")
    while True:
        news = get_news()
        for article in news:
            title = article.title
            link = article.link
            if contains_keywords(title):
                translated_title = translate_to_arabic(title)
                msg = f"📰 {translated_title}\n🔗 {link}"
                send_telegram(msg)
        time.sleep(600)  # كل 10 دقائق

if __name__ == "__main__":
    run_bot()
