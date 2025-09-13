import requests
from telegram import Bot
from datetime import datetime

# إعدادات البوت
TELEGRAM_TOKEN = '6290973236:AAHxSHfLGrusj4rCxgMP2IoxxP9743wH2As'
CHANNEL_ID = '@OnyDiwaniya'
GOLD_API_KEY = 'goldapi-hmsssmfi4p28f-io'

# دالة لجلب سعر الذهب الحالي
def get_gold_price():
    url = "https://www.goldapi.io/api/XAU/USD"
    headers = {'x-access-token': GOLD_API_KEY, 'Content-Type': 'application/json'}
    response = requests.get(url, headers=headers)
    data = response.json()
    return data['price']

# دالة بسيطة لتحليل السعر
def analyze_gold(price):
    # تحليل بسيط: إشعار حسب مستوى السعر
    if price > 2000:
        trend = "ارتفاع محتمل ⚠️"
    elif price < 1800:
        trend = "انخفاض محتمل ⚠️"
    else:
        trend = "سعر مستقر 🟢"
    return trend

# إرسال التحليل للقناة
def send_to_telegram(message):
    bot = Bot(token=TELEGRAM_TOKEN)
    bot.send_message(chat_id=CHANNEL_ID, text=message)

# تنفيذ البوت
if __name__ == "__main__":
    price = get_gold_price()
    trend = analyze_gold(price)
    date = datetime.now().strftime("%Y-%m-%d %H:%M")
    message = f"تحليل الذهب اليوم ({date}):\nالسعر الحالي: ${price}\nالاتجاه المتوقع: {trend}"
    send_to_telegram(message)
