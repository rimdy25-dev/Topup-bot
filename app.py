import os
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")

def send_telegram_alert(customer_name, game_id, amount, txn_id):
    message = (
        "🔔 **មានការ Top Up ថ្មី!**\n\n"
        f"👤 **អតិថិជន:** {customer_name}\n"
        f"🎮 **Game ID:** {game_id}\n"
        f"💰 **ចំនួនទឹកប្រាក់:** ${amount}\n"
        f"🆔 **លេខប្រតិបត្តិការ:** `{txn_id}`\n"
        "✅ **ស្ថានភាព:** ទូទាត់ជោគជ័យ"
    )
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": ADMIN_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    requests.post(url, json=payload)

@app.route('/payment-webhook', methods=['POST'])
def payment_webhook():
    # កូដសម្រាប់รับទិន្នន័យរបស់អ្នក
    return jsonify({"status": "success"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
