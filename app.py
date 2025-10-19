from flask import Flask, request, jsonify
import requests, os
from openai import OpenAI

# ✅ OpenAI 클라이언트 생성 (이 방식만 지원됨)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = Flask(__name__)

# ✅ 환경 변수 불러오기
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
CHAT_ID = int(os.getenv("CHAT_ID", 0))

@app.route('/')
def home():
    return "🤖 Genie Webhook Server connected to Telegram + OpenAI (v1.3.7)"

# ✅ 텔레그램 알림 전송 엔드포인트
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

# ✅ GPT 호출 (새 SDK 문법)
@app.route('/ask', methods=['POST'])
def ask_gpt():
    data = request.get_json()
    prompt = data.get("prompt", "")
    try:
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        answer = res.choices[0].message.content
        send_message(CHAT_ID, f"🧠 GPT 응답:\n{answer}")
        return jsonify({"ok": True, "answer": answer}), 200
    except Exception as e:
        print("❌ GPT Error:", e)
        return jsonify({"ok": False, "error": str(e)}), 500

# ✅ 텔레그램 전송 함수
def send_message(chat_id, text):
    url = f"{TELEGRAM_API_URL}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    try:
        res = requests.post(url, json=payload)
        print("📤 Telegram API Response:", res.status_code, res.text)
    except Exception as e:
        print("❌ Telegram Error:", e)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
