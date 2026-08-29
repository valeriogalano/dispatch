📱 **Un player mobile più snello e l'ottimizzazione delle risorse**

Valerio ha concentrato gli sforzi di questa settimana sulla rifinitura del player per il sito di [Pensieri in codice](https://github.com/valeriogalano/pensieriincodice-website) e su una drastica riduzione dei consumi di calcolo sulle pipeline di CI.

📱 **Interfaccia e accessibilità sul web**
*   **Player a due stati:** Ha ridotto il player mobile a due soli stati (mini ed espanso), eliminando la visualizzazione intermedia per rimuovere codice morto e uniformare l'esperienza d'uso a quella delle principali piattaforme di streaming.
*   **Condivisione e timer:** Ha integrato lo sleep timer anche nell'espanso su mobile e riscritto la logica di condivisione. Ora è possibile scegliere se condividere l'episodio intero o il timestamp esatto dell'ascolto corrente.
*   **Ricerca e accessibilità:** Ha aggiunto la ricerca nelle trascrizioni dal player espanso e reso la copertina attivabile da tastiera per chi naviga senza puntatore.

⚙️ **Tagli ai consumi e notifiche intelligenti**
*   **Cron ottimizzati:** Ha ridotto la frequenza dei controlli sui feed per [Mastodon](https://github.com/valeriogalano/podcast-rss-to-mastodon) e [Telegram](https://github.com/valeriogalano/podcast-rss-to-telegram) da oraria a ogni sei ore, dimezzando l'uso delle Actions di GitHub.
*   **AudioPills:** Ha disattivato temporaneamente la costosa CI su macOS a favore di verifiche locali obbligatorie prima di ogni merge, isolando e coprendo con test la logica di framing LSP del bridge MCP.
*   **Notifiche via issue:** Ha modificato [l'automazione degli audiogrammi](https://github.com/valeriogalano/podcast-audiogram-automation) e [il relativo publisher](https://github.com/valeriogalano/podcast-audiogram-publisher) affinché pubblichino i report di esecuzione direttamente come commenti a una issue di GitHub, sfruttando le notifiche email native della piattaforma senza appoggiarsi a SMTP esterni.

🤖 **Integrazioni e istruzioni per agenti**
*   **Instagram MCP:** Ha creato un server MCP privato per monitorare commenti e dati statistici del profilo, configurando la rotazione automatica delle credenziali direttamente da codice.
*   **Competenze per IA:** Ha centralizzato le istruzioni per gli agenti in un unico file, imponendo l'uso della prima persona singolare per i compiti legati a Todoist e Trello e documentando l'uso sicuro dell'archivio Proton Drive.

📖 Articolo completo: https://pensieriincodice.it/blog/2026-08-29-recap/
#recap

_Questo testo è stato generato con gemini-3.5-flash_
