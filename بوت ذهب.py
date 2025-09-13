import requests
import asyncio
from telegram import Bot
from datetime import datetime

# =====================
# إعدادات البوت
# =====================
TELEGRAM_TOKEN = '6290973236:AAHxSHfLGrusj4rCxgMP2IoxxP9743wH2As'       # ضع توكن بوتك هنا
CHANNEL_ID = '@OnyDiwaniya'     # ضع معرف القناة هنا
GOLD_API_KEY = 'goldapi-hmsssmfi4p28f-io'      # ضع مفتاح API لأسعار الذهب هنا

# =====================
# دالة لجلب سعر الذهب
# =====================
def get_gold_price():
    url = "https://www.goldapi.io/api/XAU/USD"
    headers = {'x-access-token': GOLD_API_KEY, 'Content-Type': 'application/json'}
    response = requests.get(url, headers=headers)
    data = response.json()
    return data['price']

# =====================
# تحليل بسيط للسعر
# =====================
def analyze_gold(price):
    if price > 2000:
        trend = "ارتفاع محتمل ⚠️"
    elif price < 1800:
        trend = "انخفاض محتمل ⚠️"
    else:
        trend = "سعر مستقر 🟢"
    return trend

# =====================
# إرسال الرسالة بطريقة async
# =====================
async def send_to_telegram(message):
    bot = Bot(token=TELEGRAM_TOKEN)
    await bot.send_message(chat_id=CHANNEL_ID, text=message)

# =====================
# Main function
# =====================
async def main():
    price = get_gold_price()
    trend = analyze_gold(price)
    date = datetime.now().strftime("%Y-%m-%d %H:%M")
    message = f"تحليل الذهب اليوم ({date}):\nالسعر الحالي: ${price}\nالاتجاه المتوقع: {trend}"
    await send_to_telegram(message)

# =====================
# تشغيل البوت
# =====================
if __name__ == "__main__":
    asyncio.run(main())
