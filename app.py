from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

TELEGRAM_TOKEN = "7669613396:AAEqH2w9BSjjLoMjljzLaUINo1sPK-o6Yoc"
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
CHAT_ID = 7826229065  # 시나의 개인 텔레그램 ID

@app.route('/')
def home():
    return "🤖 Genie Telegram Webhook Server is running!"

@app.route('/webhook', methods=['POST'])
def telegram_webhook():
    data = request.get_json(silent=True)
    print("📩 Telegram Webhook Received:", data)
    if "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"]["text"]
        reply = f"✨ 지니봇이 응답합니다: {text}"
        send_message(chat_id, reply)
    return jsonify({"ok": True}), 200

@app.route('/send', methods=['POST'])
def send_alert():
    data = request.get_json()
    trigger = data.get("trigger")
    symbol = data.get("symbol")
    message = data.get("message", "📢 No message received.")

    if trigger:
        alert_msg = f"⚡ [Trigger: {trigger}] {symbol or ''} {message}".strip()
    else:
        alert_msg = f"🚨 Genie Alert: {message}"

    send_message(CHAT_ID, alert_msg)
    return jsonify({"ok": True, "sent": alert_msg}), 200

def send_message(chat_id, text):
    url = f"{TELEGRAM_API_URL}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    try:
        res = requests.post(url, json=payload)
        print("📤 Telegram API Response:", res.status_code, res.text)
    except Exception as e:
        print("❌ Error sending message:", e)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
