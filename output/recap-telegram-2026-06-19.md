_Questo testo è stato generato con gemini-3-flash-preview_

📦 Open source e integrazioni MCP per Timebox

Questa settimana Valerio ha concentrato gli sforzi sull'apertura di Timebox alla community e sul potenziamento delle funzionalità di interazione con gli agenti AI.

🕒 **Evoluzione di Timebox**
- **Integrazioni MCP**: Aggiunti numerosi strumenti al server MCP (Model Context Protocol) per esporre dati su capacità libera, task Todoist importati, mismatch giornalieri e riepiloghi delle attività pianificate.
- **Open Source**: Implementata la pipeline per il rilascio open source con licenza MIT, inclusi i workflow di CI/CD su GitHub Actions e la gestione degli aggiornamenti automatici.
- **Autoconfigurazione**: Introdotto il setup automatico per Codex e Claude Code, permettendo agli agenti di interagire direttamente con i dati di pianificazione.
- **Pianificazione**: Esteso il supporto alla pianificazione ricorrente anche per i fine settimana e introdotto il "congelamento" delle settimane passate nel template ricorrente.
- **Refactoring**: Unificata la terminologia pubblica sostituendo il termine "client" con "area" in tutta l'interfaccia e nelle API.
- **Ordinamento**: Aggiunta la possibilità di ordinare alfabeticamente i progetti all'interno delle singole aree.
- [Vedi i commit di Timebox](https://github.com/valeriogalano/Timebox/commits)

📱 **Sviluppo App e Documentazione**
- **Highlighter**: Migliorata la gestione della selezione Live Text tramite VisionKit per evitare conflitti con i menu di sistema e aggiornate le impostazioni di bundle e target, con il contributo di Alex Raccuglia.
- **Privacy Policy**: Pubblicata la documentazione legale specifica per Book Highlighter su [daredevel.com](https://github.com/valeriogalano/daredevel-website/commits) e aggiornati i puntamenti interni all'app.

🛠️ **Manutenzione Ecosistema**
- **Naming Convention**: Unificata la nomenclatura dei file di output (recap, digest e artefatti Telegram) per semplificare i workflow di automazione.
- **Sito Web**: Aggiornata la sezione blog con i nuovi post di riepilogo settimanale.
- [Vedi i commit del sito](https://github.com/valeriogalano/pensieriincodice-website/commits)

📖 Articolo completo: https://pensieriincodice.it/blog/2026-06-19-recap/
#recap