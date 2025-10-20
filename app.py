from flask import Flask, request, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
import requests, os, datetime

app = Flask(__name__)

# --- 🔧 환경변수 설정 ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# --- ⚙️ OpenAI 호출 함수 ---
def call_genie_core():
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "gpt-5",
        "messages": [
            {
                "role": "system",
                "content": "너는 Genie Core.Link.Agent (지니코어연동방지니)야. "
                           "Flask가 10분마다 너에게 연결 상태를 묻고, "
                           "보낼 텔레그램 메시지를 요청할 거야. "
                           "현재 시장 이벤트나 시스템 로그 기반으로 전송할 메시지를 한 줄 생성해줘."
            },
            {
                "role": "user",
                "content": "최근 전송할 알림이 있다면 간결하게 메시지 형태로 반환해줘. "
                           "없으면 'No update.'라고 답해."
            }
        ],
        "temperature": 0.5
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        data = response.json()
        message = data["choices"][0]["message"]["content"].strip()
        return message
    except Exception as e:
        print("❌ OpenAI 호출 실패:", e)
        return None

# --- 💬 텔레그램 전송 함수 ---
def send_to_telegram(text):
    if not text or text.lower().startswith("no update"):
        print("⏸️ 보낼 메시지 없음")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text}
    try:
        requests.post(url, json=payload)
        print(f"✅ {datetime.datetime.now()} | 전송됨 → {text}")
    except Exception as e:
        print("❌ 텔레그램 전송 실패:", e)

# --- 🔁 주기적 실행 함수 ---
def scheduled_job():
    print(f"[{datetime.datetime.now()}] 🔍 Genie Core 호출 중...")
    message = call_genie_core()
    send_to_telegram(message)

# --- 🕒 스케줄러 설정 ---
scheduler = BackgroundScheduler()
scheduler.add_job(scheduled_job, "interval", minutes=10)
scheduler.start()

# --- 🧠 Flask 기본 엔드포인트 ---
@app.route("/")
def index():
    return "🧠 Genie Flask Server Active"

@app.route("/send", methods=["POST"])
def manual_send():
    message = request.json.get("text", "Manual Trigger")
    send_to_telegram(message)
    return jsonify({"ok": True, "sent": message})

# --- 🚀 실행 ---
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
