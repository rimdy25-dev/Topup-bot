import io
import os
import qrcode
from flask import Flask, jsonify, request, send_file
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
)

app = Flask(__name__)

# ==========================================
# ការកំណត់ព័ត៌មានហាង និង Bot Token
# ==========================================
BAKONG_ACCOUNT = "sokheng_ly@bkrt"
STORE_NAME = "PVH TOPUP"
TELEGRAM_BOT_TOKEN = "ដាក់_Telegram_Bot_Token_របស់អ្នកត្រង់នេះ"


# ==========================================
# ផ្នែក Flask (សម្រាប់បង្កើត QR កូដ)
# ==========================================
@app.route("/", methods=["GET"])
def home():
  return (
      jsonify({
          "status": "online",
          "store": STORE_NAME,
          "account": BAKONG_ACCOUNT,
          "message": "PVH Topup Bot & QR Server is running!",
      }),
      200,
  )


@app.route("/generate_qr/<float:amount>", methods=["GET"])
def generate_qr(amount):
  """បង្កើតរូបភាព QR ស្វ័យប្រវត្តសម្រាប់ស្កេនបង់ប្រាក់"""
  try:
    qr_data = f"https://bakong.nbc.gov.kh/qr?account={BAKONG_ACCOUNT}&amount={amount}&currency=USD"
    img = qrcode.make(qr_data)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return send_file(buf, mimetype="image/png")
  except Exception as e:
    return jsonify({"error": str(e)}), 500


@app.route("/webhook/payment", methods=["POST"])
def payment_webhook():
  """Webhook ទទួលដំណឹងពេលលុយចូលគណនីស្វ័យប្រវត្ត"""
  try:
    data = request.json or {}
    receiver = data.get("receiver")
    amount = data.get("amount")
    currency = data.get("currency")
    sender = data.get("sender")

    if receiver == BAKONG_ACCOUNT:
      print(f"ទទួលបានប្រាក់ចំនួន: {amount} {currency} ពី {sender}")
      return (
          jsonify({
              "status": "success",
              "message": "Payment received automatically",
          }),
          200,
      )

    return jsonify({"status": "failed", "message": "Invalid receiver"}), 400
  except Exception as e:
    return jsonify({"error": str(e)}), 500


# ==========================================
# ផ្នែក Telegram Bot (សម្រាប់អតិថិជនចុចទិញ)
# ==========================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
  keyboard = [
      [InlineKeyboardButton("💎 ទិញពេជ្រ $1 (លោត QR)", callback_data="topup_1")],
      [InlineKeyboardButton("💎 ទិញពេជ្រ $5 (លោត QR)", callback_data="topup_5")],
  ]
  reply_markup = InlineKeyboardMarkup(keyboard)
  await update.message.reply_text(
      "សូមស្វាគមន៍មកកាន់ហាង PVH TOPUP!\nសូមជ្រើសរើសកញ្ចប់ពេជ្រដែលអ្នកចង់ទិញ៖",
      reply_markup=reply_markup,
  )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
  query = update.callback_query
  await query.answer()

  if query.data == "topup_1":
    amount = 1
  elif query.data == "topup_5":
    amount = 5
  else:
    amount = 1

  # Link សម្រាប់ទាញយករូបភាព QR ពី Server របស់អ្នក
  # បើដាក់លើ Render ត្រូវប្តូរ http://localhost:5000 ទៅជា Link Render របស់អ្នក (ឧ៖ https://xxxx.onrender.com)
  base_url = "http://localhost:5000"
  qr_url = f"{base_url}/generate_qr/{amount}"

  await query.message.reply_text(
      f"KHQR សម្រាប់ទូទាត់ទឹកប្រាក់ចំនួន **${amount}**\n"
      f"ឈ្មោះគណនី: `{BAKONG_ACCOUNT}`\n\n"
      "សូមប្រើប្រាស់แပប ABA ឬ Bakong ដើម្បីស្កេនបង់ប្រាក់ខាងក្រោមនេះ៖"
  )
  await query.message.reply_photo(
      photo=qr_url,
      caption=(
          "⚠️ បង់ប្រាក់រួចសូមរង់ចាំបន្តិច ប្រព័ន្ធនឹងបញ្ចូលពេជ្រឱ្យស្វ័យប្រវត្ត!"
      ),
  )


if __name__ == "__main__":
  # ចំណាំ៖ បើ Run ក្នុង Localhost ដើម្បីតេស្ត Bot អាចប្រើវិធីដាច់ដោយឡែក
  # ប៉ុន្តែបើស្តង់ដារ Render គឺវាដំណើរការ Flask សិន
  app.run(host="0.0.0.0", port=5000, debug=True)
