🛠️ **Consolidamento, performance e sicurezza locale**

Questa settimana Valerio si è concentrato sulla stabilità e sulla sicurezza degli strumenti di lavoro personali, affrontando riscritture profonde e risolvendo vulnerabilità silenziose.

🎙️ **AudioPills e PrompterCam**
* **AudioPills**: ha ottimizzato l'analisi dei file audio passando a una singola scansione in streaming, abbattendo la memoria di picco da oltre 1 GB a meno di 20 MB su tracce lunghe. Ha messo in sicurezza il server MCP integrato, limitando il binding all'indirizzo di loopback e disattivando l'accesso cross-origin (CORS). Ha inoltre introdotto il supporto nativo ai file `.audiopills` e la conferma di chiusura per i progetti con modifiche non salvate.
* **PrompterCam**: ha corretto un bug che capovolgeva l'anteprima video in modalità orizzontale a causa di un'incongruenza tra enum di rotazione. Ha sostituito il timer di scorrimento del testo con `CADisplayLink`, rendendo il movimento fluido sugli schermi ProMotion a 120 Hz e impedendo al testo di bloccarsi durante il tocco.

🤖 **Infrastruttura e pubblicazione**
* **[Dispatch](https://github.com/valeriogalano/dispatch)**: ha implementato il tracciamento nel registro degli ID dei messaggi inviati su Telegram, un passaggio necessario per consentire future correzioni automatiche via API.
* **[Sito web](https://github.com/valeriogalano/pensieriincodice-website)**: ha isolato gli stili CSS del player audio per evitare ridimensionamenti indesiderati dell'artwork al passaggio del cursore sulla barra laterale.
* **[Timebox](https://github.com/valeriogalano/Timebox)**: ha corretto un comportamento della CLI che ignorava lo stato di default di un'area in assenza di un override settimanale.

🧠 **Agent Skills**
* **Proton Pass**: ha unificato le istruzioni e le regole per l'uso di `pass-cli` in un'unica skill condivisa per gli agenti locali.
* **Obsidian**: ha dovuto revocare l'integrazione della ricerca semantica tramite Basic Memory. Le restrizioni di iCloud su macOS impedivano l'accesso diretto ai file da parte del server MCP, causando un errore di lettura che veniva interpretato dall'indice come una rimozione di massa delle note.

📖 Articolo completo: https://pensieriincodice.it/blog/2026-08-21-recap/
#recap

_Questo testo è stato generato con gemini-3.5-flash_
