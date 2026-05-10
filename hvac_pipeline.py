import anthropic
from flask import Flask, request, jsonify
from config import CONFIG

client = anthropic.Anthropic()
app = Flask(__name__)

def normalize_intent(intent):
    if not intent or not isinstance(intent, str):
        return "GENERAL"

    intent = intent.upper().strip()

    for i in CONFIG["intents"]:
        if i in intent:
            return i

    return "GENERAL"

def classify_with_ai(text):
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=50,
        temperature=0,
        system=(
            f"You classify {CONFIG['industry']} voicemails into "
            f"{', '.join(CONFIG['intents'])}. Return ONLY one word."
        ),
        messages=[{"role": "user", "content": text}]
    )

    raw = response.content[0].text.strip()
    return normalize_intent(raw)

def route_intent(intent, phone):
    intent = normalize_intent(intent)
    return CONFIG["messages"][intent]

def process(text, phone):
    intent = classify_with_ai(text)
    result = route_intent(intent, phone)

    return {
        "industry": CONFIG["industry"],
        "intent": intent,
        "result": result
    }

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json() or {}

    text = (data.get("text") or "").strip()
    phone = (data.get("phone") or "").strip()

    if not text or not phone:
        return jsonify({"error": "missing text or phone"}), 400

    return jsonify(process(text, phone))

if __name__ == "__main__":
    app.run(debug=True, port=5000)
