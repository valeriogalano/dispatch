🤖 Tracciamento, moderazione e pulizia dell'interfaccia

Questa settimana Valerio ha integrato Botcaster nel flusso di monitoraggio e ha rifinito l'organizzazione visiva dei progetti in Timebox.

🤖 Botcaster
*   **Verifica d'ingresso**: ha introdotto un test matematico per i nuovi membri dei gruppi Telegram, utile a frenare gli account automatizzati. Il sistema offre tre tentativi con quesiti diversi prima di procedere all'espulsione, coprendo sia l'accesso diretto sia le richieste di adesione.
*   **Avvisi per gli amministratori**: il bot ora notifica il gruppo dei moderatori in caso di silenziamento antispam o espulsione per verifica scaduta. La notifica è strutturata per non interrompere le operazioni di moderazione in caso di mancata consegna.
*   **Osservabilità**: ha abilitato la persistenza dei log sulla piattaforma Cloudflare Workers per analizzare il comportamento dell'applicazione a posteriori, superando la necessità di sessioni di debug in tempo reale.

📦 [Timebox](https://github.com/valeriogalano/Timebox)
*   **Filtro progetti archiviati**: ha aggiunto un controllo per mostrare o nascondere i progetti archiviati all'interno delle Aree. Il riordino degli elementi tramite trascinamento ora si limita ai soli progetti visibili. Sviluppato con il contributo di Claude.

⚙️ [Dispatch](https://github.com/valeriogalano/dispatch)
*   **Inclusione repository**: ha inserito Botcaster tra le sorgenti monitorate dal generatore dei digest. Trattandosi di un modulo privato, la configurazione esclude i riferimenti pubblici ma assicura che le attività non vadano perse nei resoconti settimanali.

📖 Articolo completo: https://pensieriincodice.it/blog/2026-09-04-recap/
#recap

_Questo testo è stato generato con gemini-3.5-flash_
