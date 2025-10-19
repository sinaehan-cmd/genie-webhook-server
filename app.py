from flask import Flask, request, jsonify
import json, os
from datetime import datetime

app = Flask(__name__)

# 🔐 비밀키 (네 Genie System과 동일하게 설정)
SECRET_KEY = "my_genie_secret_1234"
LOG_FILE = "logs.json"

@app.route('/')
def home():
    return "🧠 Genie Secure Webhook Server + Log System is running!"

@app.route('/webhook', methods=['POST'])
def webhook():
    # 1️⃣ 인증 검사
    auth_header = request.headers.get("X-Genie-Auth")
    if auth_header != SECRET_KEY:
        print("🚫 Unauthorized access attempt detected!")
        return jsonify({"error": "Unauthorized"}), 401

    # 2️⃣ JSON 본문 수신
    data = request.get_json(silent=True)
    timestamp = datetime.utcnow().isoformat() + "Z"
    log_entry = {"timestamp": timestamp, "data": data}

    # 3️⃣ 로그 파일에 누적 저장
    try:
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                logs = json.load(f)
        else:
            logs = []

        logs.append(log_entry)

        with open(LOG_FILE, "w", encoding="utf-8") as f:
            json.dump(logs, f, ensure_ascii=False, indent=2)

        print(f"📩 Logged new webhook at {timestamp}: {data}")

    except Exception as e:
        print(f"⚠️ Log write error: {e}")

    # 4️⃣ 정상 응답 반환
    return jsonify({"status": "logged", "received": data}), 200
