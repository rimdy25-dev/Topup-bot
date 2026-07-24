import os
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)
BOT_TOKEN = os.getenv("BOT_TOKEN")

# ==========================================
# ⚙️ ១. ទិន្នន័យអត្ថបទ (អាចកែប្រែតាម Bot បាន)
# ==========================================
BOT_DATA = {
    "welcome_msg": "👋 **សួស្ដីស្វាគមន៍មកកាន់សេវាកម្មទិញពេជ្រស្វ័យប្រវត្តិ!**\n\nសូមជ្រើសរើសហ្គេមដែលអ្នកចង់ទិញពេជ្រ៖",
    "payment_info": "🇰🇭 **សូមស្កេន KHQR ខាងក្រោមដើម្បីទូទាត់ប្រាក់**\n\n(សូមផ្ញើវិក្កយបត្រ/Slip មកកាន់ទីនេះបន្ទាប់ពីបង់រួច)",
    "support_info": "👨‍💻 **សេវាបម្រើអតិថិជន (Support)**\n\nបើមានបញ្ហាឬចម្ងល់ផ្សេងៗ សូមទាក់ទងមកកាន់៖ @YourAdminUsername"
}

# ==========================================
# ⚙️ ២. ទិន្នន័យប៊ូតុង (កែប្រែនៅទីនេះដើម្បីកុំឱ្យបាត់ពេល Server លោត)
# ==========================================
GAMES_MENU = [
    [{"text": "🔥 Free Fire", "callback_data": "game_ff"}],
    [{"text": "⚔️ Mobile Legends", "callback_data": "game_mlbb"}],
    # ➕ បើចង់បន្ថែមហ្គេមថ្មី (ឧ. PUBG) សូមលុបសញ្ញា # ពីមុខជួរខាងក្រោម៖
    # [{"text": "🪂 PUBG Mobile", "callback_data": "game_pubg"}]
]

DIAMOND_PACKAGES = {
    "game_ff": {
        "name": "Free Fire",
        "buttons": [
            [{"text": "💎 100 ពេជ្រ - $1.00", "callback_data": "buy_ff_100"}],
            [{"text": "💎 310 ពេជ្រ - $3.00", "callback_data": "buy_ff_310"}],
            [{"text": "💎 520 ពេជ្រ - $5.00", "callback_data": "buy_ff_520"}]
            # ➕ បន្ថែមកញ្ចប់ FF ថ្មីនៅខាងក្រោមនេះ...
        ]
    },
    "game_mlbb": {
        "name": "Mobile Legends",
        "buttons": [
            [{"text": "💎 78 ពេជ្រ - $1.50", "callback_data": "buy_ml_78"}],
            [{"text": "💎 156 ពេជ្រ - $3.00", "callback_data": "buy_ml_156"}]
            # ➕ បន្ថែមកញ្ចប់ MLBB ថ្មីនៅខាងក្រោមនេះ...
        ]
    }
}

# ==========================================
# ប្រព័ន្ធដំណើរការកូដ (Core System)
# ==========================================
USER_STATE = {}

@app.route('/')
def home():
    return "Diamond Top-Up Bot is Running!"

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

    # ១. ឆែកមើលការវាយបញ្ចូលទិន្នន័យថ្មីពី Admin
    if chat_id in USER_STATE:
        state = USER_STATE[chat_id]
        if state == "EDIT_WELCOME":
            BOT_DATA["welcome_msg"] = text
            del USER_STATE[chat_id]
            send_text(chat_id, "✅ **សារស្វាគមន៍ត្រូវបានកែប្រែជោគជ័យ!**")
            return
        elif state == "EDIT_PAYMENT":
            BOT_DATA["payment_info"] = text
            del USER_STATE[chat_id]
            send_text(chat_id, "✅ **ព័ត៌មានបង់ប្រាក់ត្រូវបានកែប្រែជោគជ័យ!**")
            return
        elif state == "EDIT_SUPPORT":
            BOT_DATA["support_info"] = text
            del USER_STATE[chat_id]
            send_text(chat_id, "✅ **ព័ត៌មាន Support ត្រូវបានកែប្រែជោគជ័យ!**")
            return

    # ២. មុខងារបញ្ជាទូទៅ
    if text == "/start":
        send_user_menu(chat_id)
    elif text == "/admin":
        send_admin_panel(chat_id)
        
    # ៣. មុខងារពេលចុចប៊ូតុងក្នុង Admin Panel
    elif text == "📝 កែសារស្វាគមន៍":
        USER_STATE[chat_id] = "EDIT_WELCOME"
        send_text(chat_id, "✏️ សូមវាយបញ្ចូល **សារស្វាគមន៍ថ្មី** ដែលអ្នកចង់បាន៖")
    elif text == "💳 កែការបង់ប្រាក់":
        USER_STATE[chat_id] = "EDIT_PAYMENT"
        send_text(chat_id, "✏️ សូមវាយបញ្ចូល **ព័ត៌មានបង់ប្រាក់ថ្មី** (លេខកុង ឬ KHQR)៖")
    elif text == "🎧 កែ Support":
        USER_STATE[chat_id] = "EDIT_SUPPORT"
        send_text(chat_id, "✏️ សូមវាយបញ្ចូល **ព័ត៌មាន Admin Support ថ្មី**៖")
    elif text == "➕ របៀបបន្ថែមហ្គេម និង ពេជ្រ":
        send_text(chat_id, "⚠️ **ការណែនាំពីរបៀបបន្ថែមប៊ូតុង៖**\n\nដើម្បីបន្ថែមហ្គេម ឬកញ្ចប់ពេជ្រថ្មី សូមចូលទៅកាន់កូដ `app.py` របស់អ្នក ត្រង់ផ្នែកទី២ (`GAMES_MENU` និង `DIAMOND_PACKAGES`)។ \n\n*ការបន្ថែមក្នុងកូដដោយផ្ទាល់ គឺធានាថាទិន្នន័យមិនបាត់បង់ពេល Server ធ្វើការ Restart។*")
    elif text == "─── ⚙️ រៀបចំប៊ូតុង ───":
        send_text(chat_id, "សូមចុចប៊ូតុងខាងក្រោម ដើម្បីមើលការណែនាំ។")

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
        send_text(chat_id, BOT_DATA["payment_info"])

def send_text(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    requests.post(url, json=payload)

def send_user_menu(chat_id):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": BOT_DATA["welcome_msg"],
        "parse_mode": "Markdown",
        "reply_markup": {"inline_keyboard": GAMES_MENU}
    }
    requests.post(url, json=payload)

def send_admin_panel(chat_id):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    # ទម្រង់ Admin ថ្មី សម្រាប់ Top-Up សុទ្ធ
    keyboard_layout = {
        "keyboard": [
            [{"text": "📝 កែសារស្វាគមន៍"}, {"text": "💳 កែការបង់ប្រាក់"}],
            [{"text": "🎧 កែ Support"}],
            [{"text": "─── ⚙️ រៀបចំប៊ូតុង ───"}],
            [{"text": "➕ របៀបបន្ថែមហ្គេម និង ពេជ្រ"}]
        ],
        "resize_keyboard": True,
        "is_persistent": True,
        "input_field_placeholder": "ផ្ទាំងគ្រប់គ្រង Top-Up..."
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
