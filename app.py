import json, os, requests
from datetime import datetime
from flask import Flask, request, jsonify

app = Flask(__name__)

# 기존 값들
SECRET_KEY = os.environ.get("GENIE_SECRET_KEY", "my_genie_secret_1234")
LOG_FILE = "logs.json"

# 🔹 텔레그램 설정 (환경변수에서 읽음)
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")   # 예: 123456789:ABC...
CHAT_ID = os.environ.get("7669613396")                 # 예: 987654321 (문자열 OK)

def send_telegram_message(text):
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("⚠️ TELEGRAM_TOKEN 또는 CHAT_ID 미설정: 메시지 전송 건너뜀")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text}
    try:
        requests.post(url, json=payload, timeout=5)
        print("📤 Telegram message sent!")
    except Exception as e:
        print(f"⚠️ Telegram send error: {e}")

@app.route('/')
def home():
    return "📡 Genie → Telegram Webhook is running!"

@app.route('/webhook', methods=['POST'])
def webhook():
    # 보안키 검사
    auth_header = request.headers.get("X-Genie-Auth")
    if auth_header != SECRET_KEY:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json(silent=True)
    timestamp = datetime.utcnow().isoformat() + "Z"

    # 로그 저장
    logs = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            logs = json.load(f)
    logs.append({"timestamp": timestamp, "data": data})
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)

    # 텔레그램 전송
    msg = f"🚨 Genie Alert\n\nEvent: {data.get('event')}\nMessage: {data.get('message')}\nSource: {data.get('source')}"
    send_telegram_message(msg)

    return jsonify({"status": "sent_to_telegram", "received": data}), 200

@app.route('/logs', methods=['GET'])
def get_logs():
    # 보안키 검사
    auth_header = request.headers.get("X-Genie-Auth")
    if auth_header != SECRET_KEY:
        return jsonify({"error": "Unauthorized"}), 401

    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            return jsonify(json.load(f)), 200
    return jsonify({"message": "No logs yet."}), 200
