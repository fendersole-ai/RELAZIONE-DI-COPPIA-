from flask import Flask, request, jsonify, render_template
import os
import google.generativeai as genai

app = Flask(__name__)

GEMINI_API_KEY = os.environ.get("GOOGLE_API_KEY")
PROTOCOLLO_PRISM = os.environ.get("PROTOCOLLO_PRISM", "")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash-001")  # ← modello corretto

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json() or {}
    user_input = data.get("userInput", "").strip()
    prompt = f"{PROTOCOLLO_PRISM}\n\n{user_input}"

    try:
        risposta = model.generate_content(prompt)
        return jsonify({"reply": risposta.text})
    except Exception:
        return jsonify({"reply": "Si è verificato un errore. Riprova più tardi."}), 500

if __name__ == "__main__":
    app.run(debug=True)

