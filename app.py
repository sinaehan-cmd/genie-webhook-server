import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

TELEGRAM_API_URL = "https://api.telegram.org/bot7669613396:AAEqH2w9BSjjLoMjljzLaUINo1sPK-o6Yoc"

@app.route('/')
def home():
    return "🤖 Telegram Webhook Test Server is running!"

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json(silent=True)
    print("📩 Telegram Webhook Received:", data)
    return jsonify({"ok": True}), 200

def send_message(chat_id, text):
    url = f"{TELEGRAM_API_URL}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    try:
        res = requests.post(url, json=payload)
        print("📤 Telegram API Response:", res.status_code, res.text)
    except Exception as e:
        print("❌ Error sending message:", e)

@app.route('/send', methods=['POST'])
def send_alert():
    data = request.get_json()
    message = data.get("message", "📢 No message received.")
    chat_id = 7826229065  # 네 텔레그램 chat_id
    send_message(chat_id, f"🎯 Genie Alert: {message}")
    return jsonify({"ok": True, "sent": message}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)

