import os
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")

@app.route('/')
def home():
    return "Auto Diamond Topup Bot is running!"

@app.route('/telegram-bot', methods=['POST'])
def telegram_bot():
    data = request.json
    if data:
        if "message" in data:
            chat_id = data["message"]["chat"]["id"]
            text = data["message"].get("text", "")
            
            if text == "/start":
                send_welcome_menu(chat_id)
                
        elif "callback_query" in data:
            query = data["callback_query"]
            chat_id = query["message"]["chat"]["id"]
            callback_data = query["data"]
            
            if callback_data == "game_ff":
                send_diamond_packages(chat_id, "Free Fire")
            elif callback_data == "game_mlbb":
                send_diamond_packages(chat_id, "Mobile Legends")
            elif callback_data.startswith("buy_"):
                send_khqr_payment(chat_id)
                
    return jsonify({"status": "ok"})

def send_welcome_menu(chat_id):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": "👋 **សួស្ដីស្វាគមន៍មកកាន់សេវាកម្មទិញពេជ្រស្វ័យប្រវត្តិ!**\n\nសូមជ្រើសរើសហ្គេមที่คุณចង់ទិញពេជ្រ៖",
        "parse_mode": "Markdown",
        "reply_markup": {
            "inline_keyboard": [
                [{"text": "🔥 Free Fire", "callback_data": "game_ff"}],
                [{"text": "⚔️ Mobile Legends", "callback_data": "game_mlbb"}]
            ]
        }
    }
    requests.post(url, json=payload)

def send_diamond_packages(chat_id, game_name):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": f"🎮 អ្នកបានជ្រើសរើសហ្គេម **{game_name}**\n\nសូមជ្រើសរើសកញ្ចប់ពេជ្រខាងក្រោម៖",
        "parse_mode": "Markdown",
        "reply_markup": {
            "inline_keyboard": [
                [{"text": "💎 100 ពេជ្រ - $1.00", "callback_data": "buy_100"}],
                [{"text": "💎 310 ពេជ្រ - $3.00", "callback_data": "buy_310"}]
            ]
        }
    }
    requests.post(url, json=payload)

def send_khqr_payment(chat_id):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": "🇰🇭 **សូមស្កេន KHQR ដើម្បីទូទាត់ប្រាក់**\n\n(ផ្ញើ Slip មកទីនេះបន្ទាប់ពីបង់ប្រាក់រួច)",
        "parse_mode": "Markdown"
    }
    requests.post(url, json=payload)

# សម្រាប់รันក្នុងเครื่อง (Local) តែបើនៅលើ Render គឺយើងប្រើ Gunicorn
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
