from flask import Flask, request, jsonify, render_template
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Carica variabili da .env
load_dotenv()

app = Flask(__name__)

GEMINI_API_KEY = os.environ.get("GOOGLE_API_KEY")
PROTOCOLLO_PRISM = os.environ.get("PROTOCOLLO_PRISM", "")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash-001")

# Dizionario per mantenere lo stato della conversazione per ogni sessione
chat_sessions = {}

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json() or {}
    user_input = data.get("userInput", "").strip()
    session_id = data.get("sessionId") # Recuperiamo l'ID dal frontend

    if not session_id:
        return jsonify({"reply": "Errore: Sessione non valida."}), 400

    # Inizializza la sessione se non esiste
    if session_id not in chat_sessions:
        chat_sessions[session_id] = model.start_chat(history=[
            {"role": "user", "parts": [f"Segui rigorosamente questo protocollo: {PROTOCOLLO_PRISM}"]}
        ])

    try:
        # Invia il messaggio alla sessione specifica mantenendo la memoria
        response = chat_sessions[session_id].send_message(user_input)
        return jsonify({"reply": response.text})
    except Exception as e:
        print("Errore:", e)
        return jsonify({"reply": "Si è verificato un errore tecnico. Riprova."}), 500

if __name__ == "__main__":
    app.run(debug=True)