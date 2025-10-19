# ✅ Genie Webhook Server - Final Stable Version (Render Compatible)
# -------------------------------------------------------------
from flask import Flask, request, jsonify
import requests, os, threading, time
from openai import OpenAI

# 🔑 OpenAI Client 설정
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 🌐 Flask 앱 생성
app = Flask(__name__)

# ⚙️ 환경 변수 불러오기
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
CHAT_ID = int(os.getenv("CHAT_ID", 0))

# 🧠 상태 변수
background_started = False


# 🏠 기본 페이지
@app.route('/')
def home():
    return "🤖 Genie Telegram Webhook Server with GPT is running!"


# 📩 Telegram Webhook 엔드포인트
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


# 🚨 Genie Alert 엔드포인트 (지니 시스템 → Telegram)
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


# 💬 GPT 응답 함수
def ask_gpt(prompt):
    try:
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        return res.choices[0].message.content
    except Exception as e:
        print("❌ GPT Error:", e)
        return "⚠️ GPT 응답 중 오류가 발생했어요."


# 💌 Telegram 메시지 전송 함수
def send_message(chat_id, text):
    url = f"{TELEGRAM_API_URL}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    try:
        res = requests.post(url, json=payload)
        print("📤 Telegram API Response:", res.status_code, res.text)
    except Exception as e:
        print("❌ Error sending message:", e)


# 🚀 Flask 실행
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
