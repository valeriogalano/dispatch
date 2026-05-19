_Questo testo è stato generato con gemini-3-flash-preview_

🛠️ **Migrazioni e automazioni più robuste**

Questa settimana Valerio si è concentrato sul consolidamento dei contenuti storici del blog e sul miglioramento della resilienza degli script di automazione che gestiscono la distribuzione sui social.

🌐 **Evoluzione del sito web e del blog**
Valerio ha lavorato per rendere l'archivio dei contenuti più solido e navigabile, intervenendo sia sulla struttura che sullo storico dei post.
- **Paginazione**: Corretto il layout della lista blog per gestire correttamente le pagine paginate, migliorando l'esperienza di navigazione tra i numerosi articoli.
- **Migrazione contenuti**: Importati i vecchi post provenienti dal blog "daredevel", centralizzando così tutta la produzione tecnica passata all'interno del portale attuale.
- **Ottimizzazione Recap**: Perfezionata la gestione dei post riassuntivi settimanali, correggendo i link alle immagini e aggiungendo metadati specifici come il tag "Generato".
- **Repository**: https://github.com/valeriogalano/pensieriincodice-website

🤖 **Automazione e Social publishing**
Sono stati risolti alcuni problemi tecnici negli strumenti che automatizzano la condivisione dei contenuti su Mastodon e YouTube.
- **Gestione errori GitHub**: Nello strumento *Podcast RSS to Mastodon*, è stata introdotta un'eccezione esplicita nel caso in cui l'aggiornamento delle variabili di ambiente su GitHub fallisca. Questo evita il rischio di pubblicazioni duplicate infinite dello stesso episodio in caso di token scaduti.
- **YouTube OAuth**: Aggiornato il *Podcast Audiogram Publisher* per gestire in autonomia i token YouTube scaduti. Il sistema ora prevede un fallback automatico per la ri-autenticazione, evitando il crash dello script dopo lunghi periodi di inattività dei token.
- **Repository**: https://github.com/valeriogalano/podcast-rss-to-mastodon e https://github.com/valeriogalano/podcast-audiogram-publisher

📖 Articolo completo: https://pensieriincodice.it/blog/2026-05-15-recap/
#recap