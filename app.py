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

# ព័ត៌មានគណនីហាងនិង Bot Token របស់អ្នក
BAKONG_ACCOUNT = "sokheng_ly@bkrt"
STORE_NAME = "PVH TOPUP"
TELEGRAM_BOT_TOKEN = "PUT_YOUR_TELEGRAM_BOT_TOKEN_HERE"  # ដាក់ Token Bot របស់អ្នកត្រង់នេះ


# --- ផ្នែក Flask (សម្រាប់បង្កើត QR) ---
@app.route("/generate_qr/<float:amount>", methods=["GET"])
def generate_qr(amount):
  qr_data = f"https://bakong.nbc.gov.kh/qr?account={BAKONG_ACCOUNT}&amount={amount}&currency=USD"
  img = qrcode.make(qr_data)
  buf = io.BytesIO()
  img.save(buf, format="PNG")
  buf.seek(0)
  return send_file(buf, mimetype="image/png")


# --- ផ្នែក Telegram Bot (ពេលអតិថិជនប្រើ Bot) ---
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

  # បង្កើត Link យក QR ពី Flask របស់យើង
  # (ប្រសិនបើ Deploy លើ Render ត្រូវដូរ http://localhost:5000 ទៅជា Link Render របស់អ្នក)
  qr_url = f"http://localhost:5000/generate_qr/{amount}"

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
  # បើកដំណើរការ Flask និង Telegram Bot ក្នុងពេលជាមួយគ្នា
  # (សម្រាប់ Telegram Bot ពេញលេញ គេច្រើនរៀបចំ Run Bot ដាច់ដោយឡែកពី Flask Webhook)
  app.run(host="0.0.0.0", port=5000, debug=True)
