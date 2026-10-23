🛠️ Archivi ripuliti, podcast in prosa e fasce orarie

Valerio ha dedicato la settimana a una profonda bonifica dello storico del sito, mentre ha predisposto la pipeline per convertire le puntate del podcast in articoli e ha perfezionato la gestione del tempo in Timebox.

🎙️ Articoli e bot per il podcast
- **Script in articoli**: in [Dispatch](https://github.com/valeriogalano/dispatch) ha introdotto un comando per adattare i copioni del podcast in articoli per il blog, rimuovendo le formule pensate solo per l'ascolto e validando testi, citazioni e fonti prima di aprire la relativa pull request. Ha inoltre gestito le interruzioni delle risposte causate dai limiti di token del modello.
- **Pulsante episodio nei quiz**: in [Podcast Quiz to Telegram](https://github.com/valeriogalano/podcast-quiz-to-telegram) ha inserito un pulsante inline che rimanda direttamente alla puntata sul sito all'interno del sondaggio, evitando un secondo messaggio di risposta.
- **Riprova per i ban falliti**: in Botcaster ha corretto la gestione dei blocchi respinti dalle API di Telegram, conservando i dati per ritentare l'espulsione al tick successivo invece di lasciare l'utente silenziato.

🧹 Ristrutturazione dello storico web
- **Note degli episodi in Markdown**: nel repository di [Pensieri in codice](https://github.com/valeriogalano/pensieriincodice-website) ha convertito l'HTML grezzo delle note dei primi 124 episodi in Markdown pulito, eliminando tag di interruzione riga, collegamenti annidati errati e identificativi residui.
- **Fonti e attrezzatura nei metadati**: ha isolato i riferimenti reali dai link promozionali e trasferito l'attrezzatura di registrazione nel frontmatter, alleggerendo il corpo dell'episodio e correggendo le discrepanze tra le versioni di Hugo.
- **Diario di Engram**: ha rinominato i recap del blog e spostato l'indicazione del modello generativo nel frontmatter, delegandone la resa visiva al template del sito.

⏱️ Controllo degli slot in Timebox
- **Fasce orarie modificabili**: ha rilasciato la versione 0.12.0 di [Timebox](https://github.com/valeriogalano/Timebox), rendendo le fasce orarie dati espliciti e riassegnabili da Registro e Giorno per accorpare correttamente le ore lavorate.
- **Confronto tra piano ed effettivo**: ha esposto le fasce orarie via API e MCP, permettendo di verificare in quali momenti del giorno sono state svolte le attività pianificate.

📖 Articolo completo: https://pensieriincodice.it/blog/2026-10-23-recap/
#recap

_Generato con gemini-3.8-flash_
