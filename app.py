from flask import Flask, request, jsonify, render_template
import os
from google import genai

app = Flask(__name__)

GEMINI_API_KEY = os.environ.get("GOOGLE_API_KEY")
PROTOCOLLO_PRISM = os.environ.get("PROTOCOLLO_PRISM", "")

client = genai.Client(api_key=GEMINI_API_KEY)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json() or {}
    user_input = data.get("userInput", "").strip()
    prompt = f"{PROTOCOLLO_PRISM}\n\n{user_input}"

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return jsonify({"reply": response.text})
    except Exception as e:
        print("Errore:", e)
        return jsonify({"reply": "Si è verificato un errore. Riprova più tardi."}), 500

if __name__ == "__main__":
    app.run(debug=True)
