import os
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")

@app.route('/')
def home():
    return "Diamond Topup Bot is running successfully!"

def send_telegram_alert(customer_name, game_name, game_id, diamonds, amount, txn_id, bank_ref):
    message = (
        "💎 **មានការបញ្ជាទិញពេជ្រថ្មី!**\n\n"
        f"👤 **អតិថិជន:** {customer_name}\n"
        f"🎮 **ឈ្មោះហ្គេម:** {game_name}\n"
        f"🆔 **Game ID:** `{game_id}`\n"
        f"💎 **ចំនួនពេជ្រ:** {diamonds} ពេជ្រ\n"
        f"💰 **តម្លៃសរុប:** ${amount}\n"
        f"🆔 **លេខបញ្ជាក់ (Txn ID):** `{txn_id}`\n"
        f"🏦 **Bakong Ref:** `{bank_ref}`\n"
        "✅ **ស្ថានភាព:** រង់ចាំការផ្ទៀងផ្ទាត់"
    )
    
    inline_keyboard = {
        "inline_keyboard": [
            [
                {"text": "✅ បញ្ជាក់ការបញ្ជូនពេជ្រ", "callback_data": "success_topup"},
                {"text": "❌ មានបញ្ហា / មិនទាន់ចូល", "callback_data": "fail_topup"}
            ]
        ]
    }

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": ADMIN_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",
        "reply_markup": inline_keyboard
    }
    requests.post(url, json=payload)

@app.route('/payment-webhook', methods=['POST'])
def payment_webhook():
    data = request.json
    if data:
        customer_name = data.get("customer_name", "អតិថិជន")
        game_name = data.get("game_name", "Free Fire / MLBB")
        game_id = data.get("game_id", "N/A")
        diamonds = data.get("diamonds", "0")
        amount = data.get("amount", "0.00")
        txn_id = data.get("txn_id", "BK-0000")
        bank_ref = data.get("bank_ref", data.get("externalRef", "N/A"))
        
        send_telegram_alert(customer_name, game_name, game_id, diamonds, amount, txn_id, bank_ref)
        return jsonify({"status": "success", "message": "Diamond order received"})
    
    return jsonify({"status": "error", "message": "No data received"}), 400

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
