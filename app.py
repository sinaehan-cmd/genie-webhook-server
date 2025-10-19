from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 Telegram Webhook Test Server is running!"

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json(silent=True)
    print("📩 Telegram Webhook Received:", data)
    return jsonify({"ok": True}), 200
