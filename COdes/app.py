# app.py
import os
import hmac
from flask import Flask, request, jsonify
import openai

# Load OpenAI API key from environment variable
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not set in environment!")

openai.api_key = OPENAI_API_KEY

app = Flask(__name__)

# In-memory dummy user (for demo purposes)
USERS = {
    "user@example.com": "supersecretpassword"
}

def verify_password(stored_password, provided_password):
    """Securely compare passwords"""
    return hmac.compare_digest(stored_password, provided_password)

@app.route("/health", methods=["GET"])
def health():
    return "OK", 200

@app.route("/", methods=["GET"])
def home():
    return "AI Chatbot API is running. Use /health, /login endpoints.", 200

@app.route("/v1/chat", methods=["POST"])
def chat():
    """
    Expected JSON:
    {
        "conversation_id": "conv-01",
        "message": "Hello AI"
    }
    """
    data = request.get_json()
    if not data or "message" not in data:
        return jsonify({"error": "Invalid request"}), 400

    user_message = data["message"]

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_message}]
        )
        ai_reply = response.choices[0].message.content.strip()
        return jsonify({"reply": ai_reply})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/login", methods=["POST"])
def login():
    """
    Expected JSON:
    {
        "email": "user@example.com",
        "password": "password"
    }
    """
    data = request.get_json()
    if not data or "email" not in data or "password" not in data:
        return jsonify({"error": "Invalid request"}), 400

    email = data["email"]
    password = data["password"]

    if email in USERS and verify_password(USERS[email], password):
        return jsonify({"message": "Login successful"}), 200
    else:
        return jsonify({"error": "Invalid email or password"}), 401

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
