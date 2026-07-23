import os
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")

@app.route('/')
def home():
    return "Auto Diamond Topup Bot is running!"

# ១. ពេលអតិថិជនផ្ញើសារ ឬ /start ចូលមក
@app.route('/telegram-bot', methods=['POST'])
def telegram_bot():
    data = request.json
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")
        
        if text == "/start":
            send_welcome_menu(chat_id)
            
    elif "callback_query" in data:
        query = data["callback_query"]
        chat_id = query["message"]["chat"]["id"]
        callback_data = query["data"]
        
        # ជ្រើសរើសហ្គេមរួច បង្ហាញកញ្ចប់ពេជ្រ
        if callback_data == "game_ff":
            send_diamond_packages(chat_id, "Free Fire")
        elif callback_data == "game_mlbb":
            send_diamond_packages(chat_id, "Mobile Legends")
            
        # ជ្រើសរើសកញ្ចប់ពេជ្ររួច បង្ហាញ KHQR សម្រាប់បង់ប្រាក់
        elif callback_data.startswith("buy_"):
            package_info = callback_data.replace("buy_", "") # ឧទាហរណ៍: ff_100_1usd
            send_khqr_payment(chat_id, package_info)
            
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
                [{"text": "💎 100 ពេជ្រ - $1.00", "callback_data": "buy_100_1"}],
                [{"text": "💎 310 ពេជ្រ - $3.00", "callback_data": "buy_310_3"}],
                [{"text": "💎 520 ពេជ្រ - $5.00", "callback_data": "buy_520_5"}],
                [{"text": "⬅️ ត្រឡប់ក្រោយ", "callback_data": "back_to_start"}]
            ]
        }
    }
    requests.post(url, json=payload)

def send_khqr_payment(chat_id, package_info):
    # កន្លែងនេះអ្នកអាចដាក់ Link រូបភាព KHQR របស់អ្នក ឬ Dynamic KHQR API 
    # ឧទាហរណ៍បង្ហាញជា QR Code និងតម្លៃ
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": (
            "🇰🇭 **ការទូទាត់ប្រាក់តាមរយៈ Bakong KHQR**\n\n"
            "សូមស្កេន QR Code ខាងក្រោមដើម្បីបង់ប្រាក់៖\n"
            "*(បញ្ជាក់៖ សូមផ្ញើ Slept/Receipt មកទីនេះបន្ទាប់ពីបង់ប្រាក់រួច)*\n\n"
            "✅ បន្ទាប់ពីបង់ប្រាក់រួច សូមចុចប៊ូតុងខាងក្រោមដើម្បីផ្ទៀងផ្ទាត់៖"
        ),
        "parse_mode": "Markdown",
        "reply_markup": {
            "inline_keyboard": [
                [{"text": "✅ ខ្ញុំបានបង់ប្រាក់រួចរាល់", "callback_data": "paid_done"}]
            ]
        }
    }
    requests.post(url, json=payload)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
