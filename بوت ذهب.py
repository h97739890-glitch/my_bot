import requests
import pandas as pd
import pandas_ta as ta
import matplotlib.pyplot as plt
import pytz
from telegram import Bot
from datetime import datetime
import asyncio
import threading
from flask import Flask
import os

# =====================
# إعدادات البوت
# =====================
TELEGRAM_TOKEN = "6290973236:AAHxSHfLGrusj4rCxgMP2IoxxP9743wH2As"
CHANNEL_ID = "@OnyDiwaniya"
GOLD_API_KEY = "goldapi-hmsssmfi4p28f-io"

baghdad_tz = pytz.timezone("Asia/Baghdad")
bot = Bot(token=TELEGRAM_TOKEN)

CSV_FILE = "gold_prices.csv"

# =====================
# جلب السعر الحالي للذهب
# =====================
def get_gold_price():
    url = "https://www.goldapi.io/api/XAU/USD"
    headers = {"x-access-token": GOLD_API_KEY, "Content-Type": "application/json"}
    response = requests.get(url, headers=headers)
    data = response.json()
    price = float(data["price"])
    timestamp = datetime.now(baghdad_tz)
    return timestamp, price

# =====================
# تحديث CSV
# =====================
def update_csv(timestamp, price):
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
    else:
        df = pd.DataFrame(columns=["timestamp", "price"])

    df = df.append({"timestamp": timestamp, "price": price}, ignore_index=True)
    df.to_csv(CSV_FILE, index=False)
    return df

# =====================
# تحليل الذهب
# =====================
def analyze_gold(df):
    if len(df) < 2:
        # بيانات قليلة، نعطي توصية عامة
        latest = df.iloc[-1]
        return latest['price'], None, None, None, "لا توجد بيانات كافية"
    
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

# =====================
# رسم المخطط
# =====================
def plot_chart(df):
    plt.figure(figsize=(10, 5))
    plt.plot(df['timestamp'], df['price'], label="Gold Price", color="gold")
    if 'SMA50' in df.columns:
        plt.plot(df['timestamp'], df['SMA50'], label="SMA50", color="blue", linestyle='--')
    if 'EMA20' in df.columns:
        plt.plot(df['timestamp'], df['EMA20'], label="EMA20", color="red", linestyle='--')
    plt.title("سعر الذهب والمؤشرات الفنية")
    plt.xlabel("الوقت")
    plt.ylabel("السعر USD")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("gold_chart.png")
    plt.close()

# =====================
# إرسال الرسائل
# =====================
async def send_message(text, with_chart=False, df=None):
    await bot.send_message(chat_id=CHANNEL_ID, text=text)
    if with_chart and df is not None:
        plot_chart(df)
        await bot.send_photo(chat_id=CHANNEL_ID, photo=open("gold_chart.png", "rb"))

# =====================
# منطق البوت
# =====================
async def run_bot():
    counter = 0
    while True:
        try:
            timestamp, price = get_gold_price()
            df = update_csv(timestamp, price)
            price, rsi, sma50, ema20, recommendation = analyze_gold(df)
            formatted_time = timestamp.strftime("%Y-%m-%d %H:%M")

            # كل ساعة تحليل مفصل
            if counter % 4 == 0:
                message = (
                    f"📊 تحليل الذهب/دولار ({formatted_time}):\n"
                    f"السعر الحالي: ${price:.2f}\n"
                    f"RSI: {rsi if rsi is not None else 'N/A'}\n"
                    f"SMA50: {sma50 if sma50 is not None else 'N/A'}\n"
                    f"EMA20: {ema20 if ema20 is not None else 'N/A'}\n"
                    f"التوصية: {recommendation}"
                )
                await send_message(message, with_chart=True, df=df)
            else:
                # كل 15 دقيقة إشعارات
                if recommendation in ["بيع ⚠️ (تشبع شرائي)", "شراء 🟢 (تشبع بيعي)"]:
                    msg = f"تنبيه ({formatted_time}): {recommendation} عند السعر ${price:.2f}"
                else:
                    msg = f"⏳ ({formatted_time}) الاحتفاظ/المراقبة: السعر ${price:.2f}, RSI={rsi if rsi is not None else 'N/A'}"
                await send_message(msg)

            counter += 1
        except Exception as e:
            print("❌ Error:", e)

        await asyncio.sleep(900)  # كل 15 دقيقة

# =====================
# Flask server لإبقاء Render شغال
# =====================
app = Flask(__name__)

@app.route("/")
def home():
    return "Gold Bot is running!"

def run_flask():
    app.run(host="0.0.0.0", port=10000)

# =====================
# التشغيل
# =====================
if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    asyncio.run(run_bot())
