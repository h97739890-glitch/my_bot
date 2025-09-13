import requests
import asyncio
import pandas as pd
import pandas_ta as ta
import matplotlib.pyplot as plt
import pytz
from telegram import Bot
from datetime import datetime

# إعدادات البوت
TELEGRAM_TOKEN = 'YOUR_BOT_TOKEN'
CHANNEL_ID = '@YourChannelUsername'
GOLD_API_KEY = 'YOUR_GOLD_API_KEY'

# المنطقة الزمنية
baghdad_tz = pytz.timezone('Asia/Baghdad')

# دالة لجلب أسعار الذهب التاريخية (ساعية)
def get_gold_prices():
    url = "https://www.goldapi.io/api/XAU/USD/1h"  # افترض أن GoldAPI توفر بيانات كل ساعة
    headers = {'x-access-token': GOLD_API_KEY, 'Content-Type': 'application/json'}
    response = requests.get(url, headers=headers)
    data = response.json()
    
    df = pd.DataFrame(data)
    df['price'] = pd.to_numeric(df['price'])
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df

# تحليل الذهب وإعطاء توصية
def analyze_gold(df):
    df['RSI'] = ta.rsi(df['price'], length=14)
    df['SMA50'] = ta.sma(df['price'], length=50)
    df['EMA20'] = ta.ema(df['price'], length=20)
    
    latest = df.iloc[-1]
    rsi = latest['RSI']
    price = latest['price']
    sma50 = latest['SMA50']
    ema20 = latest['EMA20']

    if rsi > 70:
        recommendation = "بيع ⚠️ (تشبع شرائي)"
    elif rsi < 30:
        recommendation = "شراء 🟢 (تشبع بيعي)"
    else:
        recommendation = "احتفاظ/مراقبة ⚪"

    return price, rsi, sma50, ema20, recommendation

# رسم المخطط وحفظه كصورة
def plot_chart(df):
    plt.figure(figsize=(10,5))
    plt.plot(df['timestamp'], df['price'], label='Gold Price', color='gold')
    plt.plot(df['timestamp'], df['SMA50'], label='SMA50', color='blue', linestyle='--')
    plt.plot(df['timestamp'], df['EMA20'], label='EMA20', color='red', linestyle='--')
    plt.title("سعر الذهب والمؤشرات الفنية")
    plt.xlabel("الوقت")
    plt.ylabel("السعر USD")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("gold_chart.png")
    plt.close()

# إرسال الرسالة مع الصورة
async def send_to_telegram(message):
    bot = Bot(token=TELEGRAM_TOKEN)
    await bot.send_message(chat_id=CHANNEL_ID, text=message)
    await bot.send_photo(chat_id=CHANNEL_ID, photo=open("gold_chart.png", "rb"))

# الوظيفة الرئيسية
async def main():
    df = get_gold_prices()
    price, rsi, sma50, ema20, recommendation = analyze_gold(df)
    plot_chart(df)
    
    now = datetime.now(baghdad_tz)
    formatted_time = now.strftime("%Y-%m-%d %H:%M")
    
    message = (
        f"تحليل الذهب ({formatted_time}):\n"
        f"السعر الحالي: ${price:.2f}\n"
        f"RSI: {rsi:.2f}\n"
        f"SMA50: ${sma50:.2f}\n"
        f"EMA20: ${ema20:.2f}\n"
        f"التوصية: {recommendation}"
    )
    
    await send_to_telegram(message)

# تشغيل البوت كل ساعة
async def scheduler():
    while True:
        try:
            await main()
        except Exception as e:
            print("Error:", e)
        await asyncio.sleep(3600)  # تحديث كل ساعة

if __name__ == "__main__":
    asyncio.run(scheduler())
