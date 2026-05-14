_Questo recap è stato generato con gemini-3-flash-preview_

🚀 Un player tutto nuovo e automazioni a prova di futuro

Questa settimana è stata una vera maratona di codice, una di quelle in cui ti perdi tra le righe e ne esci con qualcosa di cui essere davvero orgoglioso. Ho praticamente rivoluzionato l'esperienza d'ascolto sul sito e dato una rinfrescata totale a tutto l'ecosistema di bot che gestisce i social del podcast. C’è tantissima carne al fuoco, quindi bando alle ciance e andiamo a vedere cosa è cambiato!

🎙️ **Il nuovo player di Pensieri in codice**
Il sito del podcast ha fatto un salto in avanti enorme. Non è solo un restyling, ma un ripensamento totale della fruizione mobile e desktop.
- **Player Espanso**: Su mobile ora abbiamo un player a tutto schermo con una UX fluida, gesti touch (swipe e double tap per lo skip) e una gestione dei capitoli molto più visiva.
- **Power User Tools**: Ho aggiunto scorciatoie da tastiera (per i veri pro), la ricerca testuale nelle trascrizioni e i segnalibri personalizzati per salvare i momenti preferiti.
- **PWA e Offline**: Ora il sito è una Progressive Web App a tutti gli effetti, con Service Worker e gestione della cache per permettervi di portarvi i contenuti ovunque.
- **Privacy e Performance**: Ho eliminato ogni dipendenza esterna (Google Fonts, CDN varie), ora tutto è self-hosted per garantire velocità e rispetto della privacy.
https://github.com/valeriogalano/pensieriincodice-website

🤖 **Bot Social: addio PHP, benvenuto Python**
Ho deciso di uniformare tutti i miei strumenti di automazione. È stata una settimana di migrazioni intense per rendere tutto più manutenibile e moderno.
- **Migrazione Python**: Tutti i bot (RSS-to-Telegram, Mastodon, X, LinkedIn) sono stati migrati da PHP a Python 3.11.
- **GitHub Environments**: Ho eliminato i file di stato locali che "sporcavano" i commit. Ora lo stato (come l'ultimo URL pubblicato) viene gestito direttamente tramite variabili di ambiente GitHub tramite API.
- **Quiz Bot**: Ho lanciato un nuovo bot che genera quiz intelligenti sugli episodi usando l'AI di Anthropic (Claude), con logica di protezione dallo spam per non disturbare le conversazioni calde nel gruppo.
https://github.com/valeriogalano/podcast-quiz-to-telegram

🎬 **Audiogrammi e Video Content**
Anche il generatore di audiogrammi ha ricevuto un bel pacchetto di novità per rendere la creazione di clip social più veloce.
- **Parallelismo**: Ora il rendering dei diversi formati video avviene in parallelo sfruttando il multi-threading, dimezzando i tempi di attesa.
- **Full Episode**: Aggiunta la possibilità di generare audiogrammi per l'intero episodio, non solo per i singoli soundbite.
- **Multi-Platform**: Il publisher ora supporta nativamente Mastodon e LinkedIn, con gestione dei caricamenti a pezzi (chunked upload) per i file più pesanti.
https://github.com/valeriogalano/podcast-audiogram-generator

🧹 **Manutenzione e Open Source**
Infine, un po' di sana pulizia per rendere i progetti pronti per la community.
- **Licenza GPLv3**: Ho ufficialmente adottato la licenza GPLv3 su quasi tutti i repository per proteggere la natura aperta del progetto.
- **Documentazione**: Ho aggiunto file `ARCHITECTURE.md` e `PLAYER.md` per spiegare a chi volesse contribuire come sono strutturati i pezzi più complessi.

È stata una settimana densa, ma vedere il player che risponde ai gesti sul telefono come un'app nativa mi ripaga di ogni ora passata a debuggare Service Worker. Fatemi sapere cosa ne pensate delle nuove funzioni!

#recap