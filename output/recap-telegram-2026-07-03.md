_Questo testo è stato generato con gemini-3-flash-preview_

🤖 **Automazione e produttività al centro della settimana**

Valerio ha concentrato gli sforzi sull'evoluzione dell'ecosistema di automazione per il podcast e sul potenziamento di Timebox, con importanti aggiornamenti anche per le app mobile.

🎙️ **Automazione Podcast (Audiogrammi & Quiz)**
- **Pipeline GitHub**: L'orchestratore in [Podcast Audiogram Automation](https://github.com/valeriogalano/podcast-audiogram-automation/commits) è ora basato su runner GitHub-hosted con supporto multi-podcast e archiviazione su GitHub Releases.
- **Gestione Telegram**: In [Podcast Audiogram Publisher](https://github.com/valeriogalano/podcast-audiogram-publisher/commits), implementata la pubblicazione di video lunghi (>60s) come messaggi standard con caption HTML e link cliccabili.
- **Personalizzazione**: [Podcast Audiogram Generator](https://github.com/valeriogalano/podcast-audiogram-generator/commits) permette ora di spostare la trascrizione in fondo ai file di testo, mentre [Podcast Quiz to Telegram](https://github.com/valeriogalano/podcast-quiz-to-telegram/commits) invia un riferimento cliccabile all'episodio dopo ogni quiz.
- **Affidabilità**: Migliorata la persistenza dello stato per evitare caricamenti duplicati in caso di errori parziali durante la pubblicazione.

⏱️ **Timebox**
- **Aggiornamenti**: Nuovo sistema di notifica cross-platform per build non firmate e prompt di conferma per il download su Windows e Linux, con il contributo di Simone.
- **Integrazione Todoist**: Introdotta la funzione per importare i task completati direttamente nel timesheet settimanale.
- **AI & MCP**: Aggiunti nuovi strumenti MCP per consentire ad agenti AI come Claude di gestire pianificazione, template ricorrenti e override settimanali.
- **Fix & UX**: Corretti bug nel database relativi ai progetti orfani e migliorata la precisione dell'arrotondamento dei minuti.
- [Vedi tutti i commit di Timebox](https://github.com/valeriogalano/Timebox/commits)

📱 **App Mobile (KeepInTouch & AudioPills)**
- **KeepInTouch**: Introdotto il widget "Da contattare" per la Home Screen e risolto un bug che impediva la visualizzazione delle foto dei contatti nel widget stesso.
- **AudioPills**: Affinato l'algoritmo AI per il ritaglio delle soundbite, che ora rispetta i confini naturali delle parole nella trascrizione per evitare tagli netti a metà frase.

🌐 **Sito Web**
- **Recap**: Aggiunto il post di riepilogo settimanale per la sezione blog.
- [Vedi i commit del sito](https://github.com/valeriogalano/pensieriincodice-website/commits)

📖 Articolo completo: https://pensieriincodice.it/blog/2026-07-03-recap/
#recap