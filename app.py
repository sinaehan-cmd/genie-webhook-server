from flask import Flask, request, jsonify

app = Flask(__name__)

# 🔐 간단한 비밀키 (Genie System에서만 알고 있는 값)
SECRET_KEY = "my_genie_secret_1234"

@app.route('/')
def home():
    return "🔒 Genie Secure Webhook Server is running!"

@app.route('/webhook', methods=['POST'])
def webhook():
    # 1️⃣ 헤더 인증 확인
    auth_header = request.headers.get("X-Genie-Auth")
    if auth_header != SECRET_KEY:
        print("🚫 Unauthorized access attempt detected!")
        return jsonify({"error": "Unauthorized"}), 401

    # 2️⃣ JSON 본문 수신
    data = request.get_json(silent=True)
    print("📩 Secure Webhook Received:", data)
    return jsonify({"status": "success", "received": data}), 200
