import os
import pandas as pd
import ta
import telebot
import time
import requests
import os
from dotenv import load_dotenv
import telebot

# .env fayldan ma'lumotlarni yuklash
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

print("BOT_TOKEN:", BOT_TOKEN)
print("CHAT_ID:", CHAT_ID)

bot = telebot.TeleBot(BOT_TOKEN)
bot.send_message(CHAT_ID, "✅ Bot muvaffaqiyatli ishga tushdi!")

bot = telebot.TeleBot(BOT_TOKEN)

def get_data():
    url = "https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1h&limit=200"
    data = requests.get(url).json()
    df = pd.DataFrame(data,columns=[
        'time','open','high','low','close','volume','close_time',
        'qav','trades','tbbav','tbqav','ignore'
    ])
    df['close'] = df['close'].astype(float)
    return df



def get_signal(df):
    close = df['close']

    # RSI hisoblash
    rsi = ta.momentum.RSIIndicator(close, window=14).rsi()
    last_rsi = round(rsi.iloc[-1], 2)

    # MACD hisoblash
    macd = ta.trend.MACD(close)
    macd_val = round(macd.macd_diff().iloc[-1], 4)

    # Hozirgi narx
    price = round(close.iloc[-1], 5)

    # Signal logikasi
    if last_rsi < 30 and macd_val > 0:
        signal = "BUY"
        reason = "RSI oversold va MACD bullish"
    elif last_rsi > 70 and macd_val < 0:
        signal = "SELL"
        reason = "RSI overbought va MACD bearish"
    else:
        signal = "NO SIGNAL"
        reason = "Bozor notekis"

    # To‘liq signal matni
    msg = f"""
📢 Signal: {signal}
🧮 Indikator: RSI ({last_rsi}), MACD ({macd_val})
💰 Narx: {price}
💡 Sabab: {reason}
⏰ Timeframe: 1H
    """
    return msg.strip()


while True:
    try:
        df = get_data()
        signal = get_signal(df)
        bot.send_message(CHAT_ID, signal)
        print('Signal yuborildi:',signal)
        time.sleep(60 * 60 )
    except Exception as e:
        print('Xato:',e)
        time.sleep(60)

