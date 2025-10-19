from flask import Flask, request, jsonify
import requests, os, threading, time
import openai

app = Flask(__name__)

# 🔹 환경변수로 관리 (Render 환경변수 설정에 추가!)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "7669613396:AAEqH2w9BSjjLoMjljzLaUINo1sPK-o6Yoc")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
CHAT_ID = int(os.getenv("CHAT_ID", 7826229065))
openai.api_key = os.getenv("OPENAI_API_KEY")  # ✅ 반드시 Render 환경변수에 등록

# ========== 기본 페이지 ==========
@app.route('/')
def home():
    return "🤖 Genie Telegram Webhook Server with GPT is running!"

# ========== 텔레그램 웹훅 ==========
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

# ========== 즉시 알람 발송 ==========
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

# ========== GPT 요청 함수 ==========
def ask_gpt(prompt):
    try:
        res = openai.ChatCompletion.create(
            model="gpt-4o-mini",  # 또는 "gpt-5" 사용 가능
            messages=[{"role": "user", "content": prompt}]
        )
        return res.choices[0].message["content"]
    except Exception as e:
        print("❌ GPT Error:", e)
        return "⚠️ GPT 응답 중 오류가 발생했어요."

# ========== 텔레그램 메시지 전송 ==========
def send_message(chat_id, text):
    url = f"{TELEGRAM_API_URL}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    try:
        res = requests.post(url, json=payload)
        print("📤 Telegram API Response:", res.status_code, res.text)
    except Exception as e:
        print("❌ Error sending message:", e)

# ========== 자동 트리거 (15분마다 실행 예시) ==========
def background_task():
    while True:
        try:
            msg = ask_gpt("Give me a short market summary in one sentence.")
            send_message(CHAT_ID, f"⏰ Auto Update:\n{msg}")
        except Exception as e:
            print("⚠️ Background task error:", e)
        time.sleep(900)  # 900초 = 15분

@app.before_first_request
def start_background_task():
    threading.Thread(target=background_task, daemon=True).start()

# ========== 실행 ==========
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
