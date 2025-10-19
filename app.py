from flask import Flask, request, jsonify
import json, os
from datetime import datetime

app = Flask(__name__)

SECRET_KEY = "my_genie_secret_1234"
LOG_FILE = "logs.json"

@app.route('/')
def home():
    return "🧠 Genie Secure Webhook Server + Log System is running!"

@app.route('/webhook', methods=['POST'])
def webhook():
    auth_header = request.headers.get("X-Genie-Auth")
    if auth_header != SECRET_KEY:
        print("🚫 Unauthorized access attempt detected!")
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json(silent=True)
    timestamp = datetime.utcnow().isoformat() + "Z"
    log_entry = {"timestamp": timestamp, "data": data}

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

    return jsonify({"status": "logged", "received": data}), 200

# ✅ 새로 추가: 보안 로그 조회용 엔드포인트
@app.route('/logs', methods=['GET'])
def get_logs():
    auth_header = request.headers.get("X-Genie-Auth")
    if auth_header != SECRET_KEY:
        return jsonify({"error": "Unauthorized"}), 401

    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            logs = json.load(f)
        return jsonify(logs), 200
    else:
        return jsonify({"message": "No logs yet."}), 200
