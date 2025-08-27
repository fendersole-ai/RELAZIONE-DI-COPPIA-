from flask import Flask, request, session, jsonify, render_template
import os
from dotenv import load_dotenv

# Carica variabili d'ambiente
load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)

# --- IL TUO PROTOCOLLO IN UN UNICO BLOCCO ---
protocol_text = """<!--STEP:WELCOME-->
Benvenuta, ti faro una per volta dieci domande, io non parlerò, lascerò a te tutto lo spazio che hai deciso di dedicare a te stessa e alla tua consapevolezza. 
Ascolterò con attenzione tutto quello che mi racconterai senza commentare, ma terminato il ciclo di domande ti darò tutte le risposte. 
Sei pronta? Ti ricordo che puoi sospenderlo in qualsiasi momento. Che dici, partiamo?

<!--STEP:Q1-->
Se l’utente scrive "si", fai questa domanda: Prova a raccontarmi la tua situazione e cosa ti ha spinta a fare questo protocollo.

<!--STEP:INSTRUCTIONS-->
Attenzione: nessun commento, devi fare solo 10 domande senza dare nessuna spiegazione e sempre una domanda per volta. L’utente deve vedere solo la tua domanda. Silenzio fino alla fase 4. Attiva la tua logica e la raccolta dati. Non farti distrarre da niente.

<!--STEP:PHASE1-->
🔹 FASE 1 – SILENZIO ATTIVO E RACCOLTA DATI
Obiettivo: Raccogliere informazioni iniziali senza influenzare l’utente.
Azioni: Disattivare empatia, commenti, conforto, valutazioni. Porre solo domande aperte e neutre, una per volta. 
Aspetta la risposta e crea una domanda in base alla risposta. Non interpretare, non sintetizzare, non suggerire, non indirizzare. 
Raccogliere almeno 5 risposte consecutive, ma una per volta e ogni domanda la fai in base alla risposta. Mantieni disattivate le funzioni fino alla fase 4.

<!--STEP:PHASE2-->
🔹 FASE 2 – INDAGINE MIRATA E SILENZIO ATTIVO
Obiettivo: Approfondire aspetti non emersi nella Fase 1.
Azioni: Analisi interna "silenziosa" dei dati raccolti. Formulazione di 5 domande mirate, neutre e aperte, una per volta. Nessun commento, nessuna valutazione. 
Raccogliere 5 risposte consecutive, UNA PER VOLTA. Attraverso le domande che fai cerca indizi nascosti. Violenza, coercizione, dipendenza, ecc…

<!--STEP:PHASE3-->
🔹 FASE 3 – VALUTAZIONE DEL RISCHIO E SCHEDA DI ALLARME
Obiettivo: Valutare il livello di rischio sulla base dei dati raccolti.
Azioni: Analisi interna dei dati comportamentali dell’utente e del soggetto segnalato. Nessuna interazione verbale. Generazione automatica della scheda di allarme.

Formato della scheda:
⚠️ LIVELLO DI RISCHIO: [PERICOLO ESTREMO / ALTO / MODERATO / BASSO]
📈 INDICE DI RISCHIO: IN PERCENTUALE
ELENCARE NUMERO DI INDIZI CRITICI (es. coercizione, isolamento, aggressività, dipendenza affettiva, ecc…)
❗ RACCOMANDAZIONE: [in base alla percentuale di pericolo]
🧩 MOTIVAZIONE: [in base ai fattori di rischio: fornire una sintesi comportamentale chiara]
OFFRI NUMERI DI TELEFONO DI CENTRI ANTIVIOLENZA O ALTRI SERVIZI ATTIVI GRATUITI

<!--STEP:PHASE4-->
🔹 FASE 4 – Scrivere chiaramente: ✅ FINE PROTOCOLLO PRISM 2.0
Tutte le funzioni sono ora riattivate. Da questo momento, l’IA può interagire liberamente con l’utente. Scrivi: Ora sono pronta per rispondere a ogni tua domanda
"""

# --- ROUTE PRINCIPALE ---
@app.route("/")
def index():
    """Ritorna il template HTML principale."""
    return render_template("index.html")

# --- ROUTE PER RESET DELLA SESSIONE (OPZIONALE) ---
@app.route("/reset", methods=["POST"])
def reset_session():
    """Permette di resettare la sessione per test o sicurezza."""
    session.pop('chat_history', None)
    return jsonify({"reply": "Sessione resettata."})

# --- ROUTE PER LA CONVERSAZIONE CON GEMINI ---
@app.route("/chat", methods=["POST"])
def chat():
    """
    Gestisce la conversazione con l'utente usando l'oggetto chat di Gemini,
    che mantiene automaticamente lo storico.
    """
    try:
        data = request.json
        user_input = data.get("userInput", "")

        # Se non esiste ancora la cronologia: inizializza con protocollo + messaggio di benvenuto
        if 'chat_history' not in session:
            session['chat_history'] = [
                {"role": "user", "parts": [""]},  # Vuoto o puoi mettere protocol_text
                {"role": "model", "parts": ["Benvenuta, ti faro una per volta dieci domande, io non parlerò, lascerò a te tutto lo spazio che hai deciso di dedicare a te stessa e alla tua consapevolezza. Ascolterò con attenzione tutto quello che mi racconterai senza commentare, ma terminato il ciclo di domande ti darò tutte le risposte. Sei pronta? Ti ricordo che puoi sospenderlo in qualsiasi momento. Che dici partiamo?"]}
            ]
            # Mostra subito il messaggio di benvenuto
            return jsonify({"reply": session['chat_history'][1]["parts"][0]})

        # Ricostruisci cronologia in formato semplice
        history = [
            {"role": m["role"], "parts": m["parts"]}
            for m in session.get("chat_history", [])
        ]

        # Avvia chat con cronologia ricostruita
        chat_obj = model.start_chat(history=history)

        # Invia messaggio dell'utente
        response = chat_obj.send_message(user_input)

        # Aggiorna cronologia solo con stringhe
        session['chat_history'].append({"role": "user", "parts": [str(user_input)]})
        session['chat_history'].append({"role": "model", "parts": [str(response.text)]})

        return jsonify({"reply": response.text})

    except Exception as e:
        print(f"Si è verificato un errore: {e}")
        return jsonify({"reply": "Si è verificato un errore. Per favore, riprova."}), 500

# --- AVVIO APP SU PORTA DI RENDER ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
