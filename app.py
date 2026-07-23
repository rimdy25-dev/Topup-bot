import os
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")

@app.route('/')
def home():
    return "Bakong Topup Bot is running successfully!"

def send_telegram_alert(customer_name, game_id, amount, txn_id, bank_ref):
    message = (
        "🇰🇭 **មានការទូទាត់ Bakong KHQR ថ្មី!**\n\n"
        f"👤 **អតិថិជន:** {customer_name}\n"
        f"🎮 **Game ID:** {game_id}\n"
        f"💰 **ចំនួនទឹកប្រាក់:** ${amount}\n"
        f"🆔 **លេខបញ្ជាក់ (Txn ID):** `{txn_id}`\n"
        f"🏦 **Bakong Ref:** `{bank_ref}`\n"
        "✅ **ស្ថានភាព:** ទូទាត់ជោគជ័យ"
    )
    
    inline_keyboard = {
        "inline_keyboard": [
            [
                {"text": "✅ បានពិនិត្យរួចរាល់", "callback_data": "verified"},
                {"text": "❌ មានបញ្ហា", "callback_data": "issue"}
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
        # ទាញយកទិន្នន័យដែលផ្ញើមកពីប្រព័ន្ធទូទាត់ Bakong/KHQR របស់អ្នក
        customer_name = data.get("customer_name", "អតិថិជន KHQR")
        game_id = data.get("game_id", "N/A")
        amount = data.get("amount", "0.00")
        txn_id = data.get("txn_id", "BK-0000")
        bank_ref = data.get("bank_ref", data.get("externalRef", "N/A"))
        
        # ផ្ញើសារជូនដំណឹងចូល Telegram
        send_telegram_alert(customer_name, game_id, amount, txn_id, bank_ref)
        return jsonify({"status": "success", "message": "Alert sent successfully"})
    
    return jsonify({"status": "error", "message": "No data received"}), 400

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
