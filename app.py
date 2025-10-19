from flask import Flask, request, jsonify
import requests, os, openai

app = Flask(__name__)

# ✅ 환경 변수 불러오기
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID", 0))
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

# ✅ OpenAI API 키 설정 (1.2.4 구버전 방식)
openai.api_key = OPENAI_API_KEY

@app.route('/')
def home():
    return "🤖 Genie Telegram Webhook Server running with OpenAI v1.2.4"

# ✅ 알림 전송 엔드포인트
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

# ✅ GPT 요청 엔드포인트
@app.route('/ask', methods=['POST'])
def ask_gpt():
    data = request.get_json()
    prompt = data.get("prompt", "")
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # 1.2.4에서는 gpt-4o-mini 지원 X
            messages=[{"role": "user", "content": prompt}]
        )
        answer = response.choices[0].message["content"]
        send_message(CHAT_ID, f"🧠 GPT 응답:\n{answer}")
        return jsonify({"ok": True, "answer": answer}), 200
    except Exception as e:
        print("❌ GPT Error:", e)
        return jsonify({"ok": False, "error": str(e)}), 500

# ✅ 텔레그램 메시지 전송
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
