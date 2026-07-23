import os
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# ==========================================
# 1. ការកំណត់ទូទៅ (Configuration & Settings)
# ==========================================
BOT_TOKEN = os.getenv("BOT_TOKEN") # ទាញយក Token ពី Render Environment

# ទិន្នន័យរក្សាទុកបណ្តោះអាសន្ន (Settings ដែល Admin អាចកែបាន)
SETTINGS = {
    "welcome_msg": "👋 **សួស្ដីស្វាគមន៍មកកាន់សេវាកម្មទិញពេជ្រស្វ័យប្រវត្តិ!**\n\nសូមជ្រើសរើសហ្គេមដែលអ្នកចង់ទិញពេជ្រ៖",
    "payment_info": "🇰🇭 **សូមស្កេន KHQR ខាងក្រោមដើម្បីទូទាត់ប្រាក់**\n\n(សូមផ្ញើវិក្កយបត្រ/Slip មកកាន់ទីនេះបន្ទាប់ពីបង់រួច)"
}

# សម្រាប់ចងចាំថា Admin កំពុងចុចកែអ្វីមួយ (State Machine)
USER_STATE = {}

# ==========================================
# 2. Main Webhook Route (ទទួលសារពី Telegram)
# ==========================================
@app.route('/')
def home():
    return "Full Advanced Telegram Bot is running!"

@app.route('/telegram-bot', methods=['POST'])
def telegram_bot():
    data = request.json
    if not data:
        return jsonify({"status": "error"}), 400

    # ករណីភ្ញៀវចុចប៊ូតុងប្រភេទ Inline (ជាប់សារ)
    if "callback_query" in data:
        handle_callback_query(data["callback_query"])
        return jsonify({"status": "ok"})

    # ករណីភ្ញៀវផ្ញើសារធម្មតា ឬចុចប៊ូតុង Keyboard
    if "message" in data:
        handle_message(data["message"])
        
    return jsonify({"status": "ok"})

# ==========================================
# 3. មុខងារបំបែកការឆ្លើយតប (Message Handler)
# ==========================================
def handle_message(message_data):
    chat_id = message_data["chat"]["id"]
    text = message_data.get("text", "")

    # ក. ឆែកមើលថាតើ Admin កំពុងស្ថិតក្នុងទម្រង់បញ្ចូលទិន្នន័យថ្មីឬអត់?
    if chat_id in USER_STATE:
        state = USER_STATE[chat_id]
        
        if state == "WAITING_FOR_WELCOME_MSG":
            SETTINGS["welcome_msg"] = text # ផ្លាស់ប្តូរសារស្វាគមន៍
            del USER_STATE[chat_id] # លុប State ចោលវិញ
            send_text(chat_id, "✅ **សារស្វាគមន៍ត្រូវបានកែប្រែដោយជោគជ័យ!**")
            return
            
        elif state == "WAITING_FOR_PAYMENT_INFO":
            SETTINGS["payment_info"] = text # ផ្លាស់ប្តូរព័ត៌មានបង់ប្រាក់
            del USER_STATE[chat_id]
            send_text(chat_id, "✅ **ព័ត៌មានបង់ប្រាក់ត្រូវបានកែប្រែដោយជោគជ័យ!**")
            return

    # ខ. ចាប់យក Command ធម្មតា
    if text == "/start":
        send_user_menu(chat_id)
        
    elif text == "/admin":
        send_admin_panel(chat_id)

    # គ. ចាប់យកការចុចប៊ូតុងរបស់ Admin (Reply Keyboard)
    elif text == "📝 Welcome Msg":
        USER_STATE[chat_id] = "WAITING_FOR_WELCOME_MSG"
        send_text(chat_id, "✏️ សូមវាយបញ្ចូល **សារស្វាគមន៍ថ្មី** ដែលអ្នកចង់បាន រួចចុចបញ្ជូន (Send)៖")
        
    elif text == "🔑 CamRapidPay Key": # ប្រើជាឧទាហរណ៍សម្រាប់កែ Payment Info
        USER_STATE[chat_id] = "WAITING_FOR_PAYMENT_INFO"
        send_text(chat_id, "✏️ សូមវាយបញ្ចូល **ព័ត៌មានបង់ប្រាក់ថ្មី** (លេខកុង ឬ KHQR Link) រួចចុចបញ្ជូន៖")
        
    elif text == "💰 ឆែកលុយ API":
        send_text(chat_id, "💵 ទឹកប្រាក់ API បច្ចុប្បន្នរបស់អ្នកគឺ: **$150.00**\n(នេះជាទិន្នន័យឧទាហរណ៍)")
        
    elif text == "👥 Sub Admins":
        send_text(chat_id, "មុខងារបន្ថែម Admin កំពុងអភិវឌ្ឍន៍...")
        
    elif text == "─── ⚙️ Settings ───":
        send_text(chat_id, "នេះគឺជាបន្ទាត់ខណ្ឌចែក មិនមែនជាប៊ូតុងបញ្ជាទេ។")

def handle_callback_query(query_data):
    chat_id = query_data["message"]["chat"]["id"]
    callback_data = query_data["data"]
    
    if callback_data == "game_ff":
        send_diamond_packages(chat_id, "Free Fire")
    elif callback_data == "game_mlbb":
        send_diamond_packages(chat_id, "Mobile Legends")
    elif callback_data.startswith("buy_"):
        # បង្ហាញព័ត៌មានបង់ប្រាក់ដែល Admin បានកំណត់
        send_text(chat_id, SETTINGS["payment_info"])

# ==========================================
# 4. មុខងារផ្ញើសារ (Sending Functions)
# ==========================================
def send_text(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    requests.post(url, json=payload)

def send_user_menu(chat_id):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": SETTINGS["welcome_msg"],
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
        "text": f"🎮 ហ្គេម៖ **{game_name}**\n\nសូមជ្រើសរើសកញ្ចប់ខាងក្រោម៖",
        "parse_mode": "Markdown",
        "reply_markup": {
            "inline_keyboard": [
                [{"text": "💎 100 ពេជ្រ - $1.00", "callback_data": "buy_100"}],
                [{"text": "💎 310 ពេជ្រ - $3.00", "callback_data": "buy_310"}],
                [{"text": "💎 520 ពេជ្រ - $5.00", "callback_data": "buy_520"}]
            ]
        }
    }
    requests.post(url, json=payload)

def send_admin_panel(chat_id):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    # ទម្រង់ Keyboard ដូចរូបភាព
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
        "is_persistent": True,
        "input_field_placeholder": "គ្រប់គ្រងប្រព័ន្ធ Admin..."
    }

    payload = {
        "chat_id": chat_id,
        "text": "🛠 **ផ្ទាំងគ្រប់គ្រង Admin បើកដំណើរការ**\n\nជ្រើសរើសមុខងារដែលអ្នកចង់កំណត់ខាងក្រោម៖",
        "parse_mode": "Markdown",
        "reply_markup": keyboard_layout
    }
    requests.post(url, json=payload)

# ==========================================
# 5. Run Server
# ==========================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
