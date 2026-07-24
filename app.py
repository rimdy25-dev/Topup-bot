import os
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)
BOT_TOKEN = os.getenv("BOT_TOKEN")

# ==========================================
# ⚙️ កន្លែងកែប្រែពាក្យ និង ប៊ូតុង (អ្នកអាចកែ ឬបន្ថែមនៅទីនេះបាន)
# ==========================================
BOT_MESSAGES = {
    "welcome": "👋 **សួស្ដីស្វាគមន៍មកកាន់សេវាកម្មទិញពេជ្រស្វ័យប្រវត្តិ!**\n\nសូមជ្រើសរើសហ្គេមដែលអ្នកចង់ទិញពេជ្រ៖",
    "payment": "🇰🇭 **សូមស្កេន KHQR ខាងក្រោមដើម្បីទូទាត់ប្រាក់**\n\n(សូមផ្ញើវិក្កយបត្រ/Slip មកកាន់ទីនេះបន្ទាប់ពីបង់រួច)",
}

GAMES_MENU = [
    [{"text": "🔥 Free Fire", "callback_data": "game_ff"}],
    [{"text": "⚔️ Mobile Legends", "callback_data": "game_mlbb"}],
    # បើចង់ថែមហ្គេមថ្មី គ្រាន់តែថែមជួរនៅទីនេះ
]

DIAMOND_PACKAGES = {
    "game_ff": {
        "name": "Free Fire",
        "buttons": [
            [{"text": "💎 100 ពេជ្រ - $1.00", "callback_data": "buy_ff_100"}],
            [{"text": "💎 310 ពេជ្រ - $3.00", "callback_data": "buy_ff_310"}],
            [{"text": "💎 520 ពេជ្រ - $5.00", "callback_data": "buy_ff_520"}]
        ]
    },
    "game_mlbb": {
        "name": "Mobile Legends",
        "buttons": [
            [{"text": "💎 78 ពេជ្រ - $1.50", "callback_data": "buy_ml_78"}],
            [{"text": "💎 156 ពេជ្រ - $3.00", "callback_data": "buy_ml_156"}]
        ]
    }
}

# ==========================================
# ទីតាំងកូដប្រព័ន្ធដំណើរការ (មិនចាំបាច់កែប្រែទេ)
# ==========================================
USER_STATE = {}

@app.route('/')
def home():
    return "Bot is running perfectly!"

@app.route('/telegram-bot', methods=['POST'])
def telegram_bot():
    data = request.json
    if not data:
        return jsonify({"status": "error"}), 400

    if "callback_query" in data:
        handle_callback_query(data["callback_query"])
        return jsonify({"status": "ok"})

    if "message" in data:
        handle_message(data["message"])
        
    return jsonify({"status": "ok"})

def handle_message(message_data):
    chat_id = message_data["chat"]["id"]
    text = message_data.get("text", "")

    if chat_id in USER_STATE:
        state = USER_STATE[chat_id]
        if state == "WAITING_FOR_WELCOME_MSG":
            BOT_MESSAGES["welcome"] = text
            del USER_STATE[chat_id]
            send_text(chat_id, "✅ **សារស្វាគមន៍ត្រូវបានកែប្រែ!**")
            return
        elif state == "WAITING_FOR_PAYMENT_INFO":
            BOT_MESSAGES["payment"] = text
            del USER_STATE[chat_id]
            send_text(chat_id, "✅ **ព័ត៌មានបង់ប្រាក់ត្រូវបានកែប្រែ!**")
            return

    if text == "/start":
        send_user_menu(chat_id)
    elif text == "/admin":
        send_admin_panel(chat_id)
    elif text == "📝 Welcome Msg":
        USER_STATE[chat_id] = "WAITING_FOR_WELCOME_MSG"
        send_text(chat_id, "✏️ សូមវាយបញ្ចូល **សារស្វាគមន៍ថ្មី** ដែលអ្នកចង់បាន៖")
    elif text == "🔑 CamRapidPay Key":
        USER_STATE[chat_id] = "WAITING_FOR_PAYMENT_INFO"
        send_text(chat_id, "✏️ សូមវាយបញ្ចូល **ព័ត៌មានបង់ប្រាក់ថ្មី** (លេខកុង ឬ KHQR Link)៖")
    elif text == "💰 ឆែកលុយ API":
        send_text(chat_id, "💵 ទឹកប្រាក់ API បច្ចុប្បន្នរបស់អ្នកគឺ: **$150.00**")
    elif text == "─── ⚙️ Settings ───":
        send_text(chat_id, "នេះគឺជាបន្ទាត់ខណ្ឌចែក មិនមែនជាប៊ូតុងបញ្ជាទេ។")

def handle_callback_query(query_data):
    chat_id = query_data["message"]["chat"]["id"]
    callback_data = query_data["data"]
    
    if callback_data in DIAMOND_PACKAGES:
        game_info = DIAMOND_PACKAGES[callback_data]
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": f"🎮 ហ្គេម៖ **{game_info['name']}**\n\nសូមជ្រើសរើសកញ្ចប់ខាងក្រោម៖",
            "parse_mode": "Markdown",
            "reply_markup": {"inline_keyboard": game_info['buttons']}
        }
        requests.post(url, json=payload)
        
    elif callback_data.startswith("buy_"):
        send_text(chat_id, BOT_MESSAGES["payment"])

def send_text(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    requests.post(url, json=payload)

def send_user_menu(chat_id):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": BOT_MESSAGES["welcome"],
        "parse_mode": "Markdown",
        "reply_markup": {"inline_keyboard": GAMES_MENU}
    }
    requests.post(url, json=payload)

def send_admin_panel(chat_id):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    keyboard_layout = {
        "keyboard": [
            [{"text": "⏱ ល្បឿន Poll"}, {"text": "💰 ឆែកលុយ API"}],
            [{"text": "🖼 Welcome Photo"}, {"text": "🔄 ធ្វើឱ្យទាន់សម័យ"}],
            [{"text": "🔔 Notify Channel"}, {"text": "🧪 តេស្ត Notify"}],
            [{"text": "─── ⚙️ Settings ───"}],
            [{"text": "✏️ កែ Support"}, {"text": "👥 Sub Admins"}],
            [{"text": "🔑 CamRapidPay Key"}, {"text": "📝 Welcome Msg"}],
            [{"text": "💎 Premium Emoji"}]
        ],
        "resize_keyboard": True,
        "is_persistent": True
    }
    payload = {
        "chat_id": chat_id,
        "text": "🛠 **ផ្ទាំងគ្រប់គ្រង Admin បើកដំណើរការ**\n\nជ្រើសរើសមុខងារដែលអ្នកចង់កំណត់ខាងក្រោម៖",
        "parse_mode": "Markdown",
        "reply_markup": keyboard_layout
    }
    requests.post(url, json=payload)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
