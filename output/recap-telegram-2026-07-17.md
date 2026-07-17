_Questo testo è stato generato con gemini:gemini-3.5-flash_

🛠️ Settimana di grandi refactoring: dal design di Timebox a GoodLinks Publisher!

Questa settimana Valerio ha lavorato intensamente su diversi fronti, concentrandosi sul redesign visivo di Timebox, sul lancio di un nuovo tool per GoodLinks e su importanti ottimizzazioni di automazione.

📦 **Timebox** (https://github.com/valeriogalano/Timebox)
- **Nuovo sistema di segnali**: Sostituiti i colori di stato (verde/arancio/rosso) con icone e tratteggi neutri; ora il colore identifica unicamente le aree di attività.
- **Interfaccia e feature**: Introdotte tre lenti per la sezione "Andamento", un "gauge" live del carico giornaliero nella vista "Oggi" con stepper a 15 minuti e drill-down per gli override ripetuti.
- **Storicizzazione**: La vista "Nel tempo" ora legge il pianificato reale storicizzato invece del template corrente.
- **Test automatizzati**: Introdotti i test di unità e componenti nel renderer con Vitest e React Testing Library.

🔖 **GoodLinks Publisher** (https://codeberg.org/valeriogalano/goodlinks-publisher)
- **Nuova pipeline**: Creato un tool per pubblicare link da GoodLinks verso Mastodon, Telegram e blog Hugo tramite API GitHub.
- **Funzionalità extra**: Aggiunto il backup automatico dello stato su Codeberg, notifiche macOS in caso di errore, filtri temporali e gestione degli highlight.

📱 **Highlighter**
- **Scanner ISBN**: Migliorata l'affidabilità grazie alla cattura manuale, al supporto per la fotocamera macro e ad ottimizzazioni dell'autofocus.
- **Google Books**: Aggiunto il retry automatico in caso di errori temporanei (5xx) delle API.
- **Contributi**: Aggiornate le impostazioni di code signing con il contributo di Alex Raccuglia.

⚙️ **Automazioni e CI**
- **Dev Updates** (https://github.com/valeriogalano/dev-updates): Supportati i repository Codeberg e integrato il supporto multi-provider AI (Gemini e Anthropic) per la generazione dei recap.
- **Podcast RSS to Mastodon** (https://github.com/valeriogalano/podcast-rss-to-mastodon): Allineata l'architettura e risolto un bug sul contesto in GitHub Actions.
- **Audiogram Automation** (https://github.com/valeriogalano/podcast-audiogram-automation): Risolto un bug nella pipeline CI sostituendo il contesto del runner con il workspace di GitHub.

📖 Articolo completo: https://pensieriincodice.it/blog/2026-07-17-recap/
#recap