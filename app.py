import os, datetime, requests
from flask import Flask, request, jsonify, abort
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)

# ── 🔑 ENV
OPENAI_API_KEY   = os.getenv("OPENAI_API_KEY")
TELEGRAM_TOKEN   = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID") or os.getenv("CHAT_ID")
GENIE_SECRET_KEY = os.getenv("GENIE_SECRET_KEY")  # (선택) 텔레그램 웹훅 헤더 검증용
POLL_MINUTES     = int(os.getenv("POLL_MINUTES", "10"))  # 테스트 시 1로

OPENAI_URL = "https://api.openai.com/v1/chat/completions"
TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

# ── 🧩 공통: OpenAI 호출
def call_openai(messages, temperature=0.5):
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "gpt-5",  # 지니코어연동방 지니 호출
        "messages": messages,
        "temperature": temperature,
    }
    res = requests.post(OPENAI_URL, headers=headers, json=payload, timeout=30)
    res.raise_for_status()
    data = res.json()
    return data["choices"][0]["message"]["content"].strip()

# ── 💬 텔레그램 전송
def send_to_telegram(text, chat_id=None):
    if not text:
        return
    cid = chat_id or TELEGRAM_CHAT_ID
    if not cid:
        print("⚠️ TELEGRAM_CHAT_ID/CHAT_ID 미설정")
        return
    payload = {"chat_id": cid, "text": text}
    try:
        requests.post(f"{TELEGRAM_API}/sendMessage", json=payload, timeout=20)
        print(f"✅ {datetime.datetime.utcnow()} | TG sent → {text}")
    except Exception as e:
        print("❌ TG send failed:", e)

# ── 🔁 10분 루프: 코어 → 메시지 생성 → 텔레그램 전송
def scheduled_job():
    try:
        print(f"[{datetime.datetime.utcnow()}] 🔍 Genie Core polling...")
        msg = call_openai([
            {
                "role": "system",
                "content": (
                    "너는 Genie Core.Link.Agent(지니코어연동방지니)야. "
                    "시장/시스템 이벤트를 감지해 텔레그램에 보낼 한 줄 알림을 생성해. "
                    "보낼 게 없으면 반드시 'No update.'라고만 답해."
                )
            },
            {
                "role": "user",
                "content": "최근 전송할 알림이 있어? 있다면 한 줄로."
            }
        ])
        if msg.lower().startswith("no update"):
            print("⏸️ No update.")
        else:
            send_to_telegram(msg)
    except Exception as e:
        print("❌ scheduled_job error:", e)

# ── 🕒 스케줄러
scheduler = BackgroundScheduler()
scheduler.add_job(scheduled_job, "interval", minutes=POLL_MINUTES)
scheduler.start()

# ── ✅ 헬스/진단
@app.route("/")
def index():
    return "🧠 Genie Flask Server Active"

@app.route("/envcheck")
def envcheck():
    ok = {
        "OPENAI_API_KEY": bool(OPENAI_API_KEY),
        "TELEGRAM_TOKEN": bool(TELEGRAM_TOKEN),
        "TELEGRAM_CHAT_ID_or_CHAT_ID": bool(TELEGRAM_CHAT_ID),
        "GENIE_SECRET_KEY": bool(GENIE_SECRET_KEY),
        "POLL_MINUTES": POLL_MINUTES,
    }
    return jsonify(ok)

# ── ✋ 수동 전송
@app.route("/send", methods=["POST"])
def manual_send():
    data = request.get_json(silent=True) or {}
    text = data.get("text", "Manual Trigger")
    chat_id = data.get("chat_id")
    send_to_telegram(text, chat_id=chat_id)
    return jsonify({"ok": True, "sent": text})

# ── 🔄 텔레그램 ↔ 지니코어 양방향(Webhook)
def _verify_telegram_secret():
    """선택: setWebhook 시 보낸 Secret-Token 헤더 검증"""
    if not GENIE_SECRET_KEY:
        return True
    return request.headers.get("X-Telegram-Bot-Api-Secret-Token") == GENIE_SECRET_KEY

@app.route("/webhook", methods=["POST"])
def telegram_webhook():
    # 1) 보안 헤더 검증(선택)
    if not _verify_telegram_secret():
        abort(401)

    data = request.get_json(silent=True) or {}
    msg = data.get("message") or data.get("edited_message") or {}
    chat = (msg.get("chat") or {})
    chat_id = chat.get("id")
    user_text = msg.get("text", "").strip()

    if not chat_id or not user_text:
        return jsonify({"ok": True})  # 무음 처리

    # 2) OpenAI로 답변 생성
    try:
        reply = call_openai([
            {
                "role": "system",
                "content": (
                    "너는 Genie Core.Link.Agent(지니코어연동방지니)야. "
                    "텔레그램에서 온 질문에 짧고 명확하게(최대 2줄) 답해. "
                    "민감정보나 키/토큰 언급 금지."
                )
            },
            {"role": "user", "content": user_text}
        ], temperature=0.4)
    except Exception as e:
        reply = "잠시 혼잡해. 조금 뒤에 다시 시도해줘 🙏"
        print("❌ openai reply error:", e)

    # 3) 응답 전송
    send_to_telegram(reply, chat_id=chat_id)
    return jsonify({"ok": True})

# ── 🚀 실행
if __name__ == "__main__":
    # Render free 인스턴스는 유휴 시 sleep됨. 최초 hit 후 스케줄러가 다시 돈다.
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")))
