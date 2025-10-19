from flask import Flask, request, jsonify
import requests, os, threading, time
import openai

app = Flask(__name__)

# 🔹 환경 변수 불러오기
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
CHAT_ID = int(os.getenv("CHAT_ID", 0))
openai.api_key = os.getenv("OPENAI_API_KEY")

# ✅ 첫 요청 전에 백그라운드 루프가 한 번만 실행되도록 제어용 변수
background_started = False

@app.route('/')
def home():
    return "🤖 Genie Telegram Webhook Server with GPT is running!"

@app.route('/webhook', methods=['POST'])
def telegram_webhook():
    data = request.get_json(silent=True)
    print("📩 Telegram Webhook Received:", data)
    if "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"]["text"]
        reply = ask_gpt(f"User said: {text}")
        send_message(chat_id, f"✨ GPT Response:\n{reply}")
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

from openai import OpenAI
client = OpenAI()
def ask_gpt(prompt):
    try:
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        return res.choices[0].message["content"]
    except Exception as e:
        print("❌ GPT Error:", e)
        return "⚠️ GPT 응답 중 오류가 발생했어요."

def send_message(chat_id, text):
    url = f"{TELEGRAM_API_URL}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    try:
        res = requests.post(url, json=payload)
        print("📤 Telegram API Response:", res.status_code, res.text)
    except Exception as e:
        print("❌ Error sending message:", e)

# ✅ Flask 3.0 호환용 백그라운드 루프
@app.before_request
def start_background_once():
    global background_started
    if not background_started:
        print("🌀 Starting background task loop...")
        threading.Thread(target=background_task, daemon=True).start()
        background_started = True

def background_task():
    while True:
        try:
            msg = ask_gpt("Give me a one-sentence crypto market summary.")
            send_message(CHAT_ID, f"⏰ Auto Update:\n{msg}")
        except Exception as e:
            print("⚠️ Background task error:", e)
        time.sleep(900)  # 15분마다 실행

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
