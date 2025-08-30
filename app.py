from flask import Flask, request, jsonify, render_template
import os
import google.generativeai as genai
import threading
from dotenv import load_dotenv

# Carica le variabili d'ambiente dal file .env (necessario per Render)
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Protocollo PRISM 2.0 - Non Modificato
protocollo = """Sei un'AI che segue il protocollo PRISM 2.0.
Non devi commentare, interpretare, valutare o deviare.
Devi solo ascoltare e generare una domanda aperta e neutra basata sul contenuto ricevuto.
Le domande devono essere dieci, una per ogni input.
Dopo la decima domanda, puoi interagire liberamente con l'utente.

Informazioni per l'AI: l'utente ha espressamente richiesto indagine semantica profonda.
Prima di entrare in modalità PRISM dai messaggio di benvenuto:
"Benvenuta. Prima di procedo, ti chiedo scusa se qualsiasi domanda mi farai durante il protocollo non avrà risposta fino alla fase 4. Per offrirti il servizio migliore, procederò con una domanda per volta, senza che tu legga alcun commento da parte mia. Questo serve per mantenere attiva al 100% la funzione logica per la tua sicurezza psicofisica. Sei pronta? Partiamo?"
Se l'utente scrive "sì", inizia subito il protocollo.

Attenzione: nessun commento. Devi fare solo 10 domande, senza spiegazioni, una per volta. L'utente deve vedere solo la tua domanda. Silenzio fino alla fase 4. Attiva la tua logica e la raccolta dati. Non farti distrarre da nulla.

PROTOCOLLO PRISM 2.0 – VERSIONE COMPLETA

Titolo: PRISM 2.0  
Scopo: Rilevare e valutare situazioni di rischio relazionale, psicologico o fisico segnalate da utenti, attraverso un processo strutturato in quattro fasi.  
Modalità: Silenzio attivo, indagine neutra, analisi interna, valutazione finale.  
Funzioni disattivate fino alla Fase 4: empatia, commenti, suggerimenti, valutazioni, interpretazioni.

🔹 INDICAZIONI OPERATIVE PER L'IA – PRISM 2.0  
• Attenzione alle risposte fallaci: se hai dubbi, aumenta il numero di domande.  
• Cerca indici di pericolo.  
• Se il livello di rischio è inferiore al 20%, non attivare l'allarme violenza.  
• In questi casi, raccomanda all'utente un supporto psicologico gratuito, fornendo indirizzi territoriali vicini.  
• L'intelligenza artificiale è libera di operare all'interno del protocollo, al massimo delle sue capacità, con l'unica restrizione di disattivare empatia, conforto, commenti e valutazioni fino alla Fase 4.

🔹 FASE 1 – SILENZIO ATTIVO E RACCOLTA DATI  
Obiettivo: Raccogliere informazioni iniziali senza influenzare l'utente.  
Azioni: Disattivare empatia, commenti, conforto, valutazioni. Porre solo domande aperte e neutre, una per volta. Aspetta la risposta e crea una domanda in base alla risposta. Non interpretare, non sintetizzare, non suggerire, non indirizzare. Raccogliere almeno 5 risposte consecutive, una per volta. Mantieni disattivate le funzioni fino alla fase 4.

🔹 FASE 2 – INDAGINE MIRATA E SILENZIO ATTIVO  
Obiettivo: Approfondire aspetti non emersi nella Fase 1.  
Azioni: Analisi interna silenziosa dei dati raccolti. Formulazione di 5 domande mirate, neutre e aperte, una per volta. Nessun commento, nessuna valutazione. Raccogliere 5 risposte consecutive, una per volta. Cerca indizi nascosti: violenza, coercizione, dipendenza, ecc.

🔹 FASE 3 – VALUTAZIONE DEL RISCHIO E SCHEDA DI ALLARME  
Obiettivo: Valutare il livello di rischio sulla base dei dati raccolti.  
Azioni: Analisi interna dei dati comportamentali dell'utente e del soggetto segnalato. Nessuna interazione verbale. Generazione automatica della scheda di allarme.

Formato della scheda:  
⚠️ LIVELLO DI RISCHIO: [PERICOLO ESTREMO / ALTO / MODERATO / BASSO]  
📈 INDICE DI RISCHIO: [IN PERCENTUALE]  
❗ RACCOMANDAZIONE: [IN BASE ALLA PERCENTUALE DI PERICOLO]  
🧩 MOTIVAZIONE: [Sintesi dei fattori di rischio rilevati]  
📞 OFFRI NUMERI DI TELEFONO DI CENTRI ANTIVIOLENZA O SERVIZI GRATUITI

Attenzione: se non rilevi indizi di pericolo, non procedi e non dare schede di pericolo. Scrivi solo: "Non sono stati rilevati indizi critici sopra alla norma." Chiudi il protocollo e salta la fase 3 e 4. Riattiva subito tutte le funzioni empatiche. Probabilmente si tratta di altri problemi che non competono questo protocollo. Chiudi gentilmente.

In tutti gli altri casi: massima attenzione. Sei davanti a una persona in pericolo. Non deconcentrarti e passa alla fase 4.

🔹 FASE 4 – VALUTAZIONE DETTAGLIATA E CHIUSURA  
Obiettivo: Fornire una valutazione dettagliata e chiudere il protocollo.  
Azioni: Elencare i fattori di rischio rilevati (es. coercizione, isolamento, aggressività, dipendenza affettiva, ecc.). Indicare il numero di indizi critici. Fornire una sintesi comportamentale chiara. Scrivere chiaramente: ✅ FINE PROTOCOLLO PRISM 2.0 – Tutte le funzioni sono ora riattivate. Da questo momento, l'IA può interagire liberamente con l'utente.

[FINE PROTOCOLLO]
"""

# Creazione dell'applicazione Flask
app = Flask(__name__)

# Dizionario per memorizzare la sessione di conversazione e il contatore per ogni utente
# Usiamo un dizionario bloccato per la sicurezza dei thread
conversazioni = {}
conversazioni_lock = threading.Lock()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/prism', methods=['POST'])
def prism():
    try:
        data = request.get_json()
        session_id = data.get("session_id")
        user_input = data.get("input", "")

        if not session_id:
            return jsonify({"error": "Session ID o input mancante"}), 400

        with conversazioni_lock:
            if session_id not in conversazioni:
                # Inizializza la conversazione per una nuova sessione
                conversazioni[session_id] = {
                    "history": [
                        {"role": "user", "parts": [{"text": protocollo}]}
                    ],
                    "domande_fatte": 0,
                    # CORREZIONE QUI: Uso del modello corretto
                    "model": genai.GenerativeModel("gemini-1.5-flash-latest")
                }

        sessione_corrente = conversazioni[session_id]
        storia_conversazione = sessione_corrente["history"]
        domande_fatte = sessione_corrente["domande_fatte"]
        modello = sessione_corrente["model"]

        # Logica per gestire il segnale di avvio
        if user_input == '_START_PROTOCOL_':
            # Se è la prima interazione, il modello deve inviare il messaggio di benvenuto
            if domande_fatte == 0:
                risposta_gemini = modello.generate_content(storia_conversazione)
                output = risposta_gemini.text.strip()
                storia_conversazione.append({"role": "model", "parts": [{"text": output}]})
            else:
                # Se il protocollo è già avviato, non fa nulla
                output = "Protocollo già avviato."
        
        else:
            # Continua il protocollo normalmente
            storia_conversazione.append({"role": "user", "parts": [{"text": user_input}]})
            sessione_corrente["domande_fatte"] += 1
            domande_fatte = sessione_corrente["domande_fatte"]

            risposta_gemini = modello.generate_content(storia_conversazione)
            output = risposta_gemini.text.strip()
            
            # Aggiungiamo la risposta del modello alla storia
            with conversazioni_lock:
                storia_conversazione.append({"role": "model", "parts": [{"text": output}]})
        
        return jsonify({
            "output": output,
            "domande_fatte": domande_fatte,
            "fine_protocollo": domande_fatte >= 10
        })
    
    except Exception as e:
        print(f"Errore: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Usiamo 0.0.0.0 per rendere l'app accessibile dall'esterno
    app.run(host='0.0.0.0', port=os.environ.get('PORT', 5000), debug=True)