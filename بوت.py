import os
import json
import requests
import websocket

# -----------------------------
# إعدادات البوت والقناة
# -----------------------------
TELEGRAM_TOKEN = "8185068243:AAHn7U1zyyjq4NH-MqVsC2Z3JcQghwrwkgg"
TELEGRAM_CHAT_ID = "@OnyDiwaniya"
FINNHUB_API_KEY = "d2r2sk9r01qlk22reqbgd2r2sk9r01qlk22reqc0"

# -----------------------------
# دالة إرسال رسالة للقناة
# -----------------------------
def send_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False,
    }
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print("Telegram error:", e)

# -----------------------------
# دالة ترجمة النصوص للعربية
# -----------------------------
def translate_to_arabic(text):
    # هنا نستخدم ترجمة Google Translate API أو أي خدمة ترجمة
    # للتمثيل سنعيد النص كما هو (استبدل هذه الدالة بخدمة ترجمة فعلية)
    return text  # استبدل هذا بالكود الفعلي للترجمة

# -----------------------------
# معالجة الأخبار الواردة
# -----------------------------
def on_message(ws, message):
    data = json.loads(message)
    if "data" in data:
        for item in data["data"]:
            headline = item.get("headline", "")
            source = item.get("source", "")
            url = item.get("url", "")
            # ترجمة الخبر للعربية
            headline_ar = translate_to_arabic(headline)
            msg = f"💱 <b>{headline_ar}</b>\n📌 {source}\n🔗 {url}"
            send_telegram(msg)

def on_error(ws, error):
    print("Error:", error)

def on_close(ws, close_status_code, close_msg):
    print("Closed connection")

# -----------------------------
# عند فتح الاتصال
# -----------------------------
def on_open(ws):
    # رسالة اختبار للتأكد أن البوت شغال
    send_telegram("✅ اختبار: البوت متصل الآن وجاهز لإرسال الأخبار بالعربية.")

    # مصادقة
    auth = {"type": "auth", "token": FINNHUB_API_KEY}
    ws.send(json.dumps(auth))

    # قراءة الرموز من ملف خارجي symbols.txt
    try:
        with open("symbols.txt", "r") as f:
            symbols = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        # رموز افتراضية لو الملف غير موجود
        symbols = ["OANDA:EURUSD", "OANDA:GBPUSD", "OANDA:USDJPY", "OANDA:XAUUSD", "OANDA:XAGUSD"]

    # الاشتراك في جميع الأزواج
    for sym in symbols:
        ws.send(json.dumps({"type": "subscribe", "symbol": sym}))
        print("Subscribed:", sym)

# -----------------------------
# تشغيل البوت
# -----------------------------
if __name__ == "__main__":
    ws = websocket.WebSocketApp(
        "wss://ws.finnhub.io?token=" + FINNHUB_API_KEY,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
        on_open=on_open,
    )
    ws.run_forever()
