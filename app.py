from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# ✅ 여기를 추가해야 함
TELEGRAM_TOKEN = "7669613396:AAEqH2w9BSjjLoMjljzLaUINo1sPK-o6Yoc"
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

@app.route('/')
def home():
    return "🤖 Telegram Webhook Test Server is running!"

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json(silent=True)
    print("📩 Telegram Webhook Received:", data)

    if "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"]["text"]
        reply = f"✨ 지니봇이 응답합니다: {text}"

        # ✅ Flask 서버가 텔레그램에 응답 보내기
        send_message(chat_id, reply)

    return jsonify({"ok": True}), 200


def send_message(chat_id, text):
    url = f"{TELEGRAM_API_URL}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, json=payload)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
