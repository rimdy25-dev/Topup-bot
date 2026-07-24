import io
import os
import qrcode
from flask import Flask, jsonify, request, send_file

app = Flask(__name__)

# ព័ត៌មានគណនីបង់ប្រាក់
BAKONG_ACCOUNT = "sokheng_ly@bkrt"
STORE_NAME = "PVH TOPUP"


@app.route("/", methods=["GET"])
def home():
  return (
      jsonify({
          "status": "online",
          "store": STORE_NAME,
          "account": BAKONG_ACCOUNT,
          "message": "KHQR Generator API is running successfully!",
      }),
      200,
  )


@app.route("/generate_qr/<float:amount>", methods=["GET"])
def generate_qr(amount):
  """API សម្រាប់បង្កើតរូបភាព QR Code តាមទឹកប្រាក់"""
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
  """Webhook ទទួលដំំណឹងពេលមានលុយចូល"""
  try:
    data = request.json or {}
    receiver = data.get("receiver")
    amount = data.get("amount")
    currency = data.get("currency")
    sender = data.get("sender")

    if receiver == BAKONG_ACCOUNT:
      print(f"ទទួលបានប្រាក់: {amount} {currency} ពី {sender}")
      return (
          jsonify({
              "status": "success",
              "message": "Payment verified automatically",
          }),
          200,
      )

    return jsonify({"status": "failed", "message": "Invalid receiver"}), 400
  except Exception as e:
    return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5000)
