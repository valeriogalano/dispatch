_Questo testo è stato generato con gemini-3-flash-preview_

🚀 Automazione, MCP e una nuova App

Valerio ha dedicato la settimana al perfezionamento della pipeline di pubblicazione e al debutto di Highlighter, espandendo contemporaneamente le capacità di integrazione AI di AudioPills.

⚙️ **Automazione e Workflow**
- **Pipeline completa**: Automatizzato il flusso di lavoro settimanale che collega la generazione del digest, la pubblicazione sul blog e la creazione del post Telegram.
- **Resilienza API**: Introdotta una logica di retry per le chiamate a Gemini per gestire gli errori 503 temporanei.
- **Digest flessibili**: Aggiunto il supporto a range di date personalizzati e alla modalità append per la creazione dei recap.
- https://github.com/valeriogalano/dev-updates

🎙️ **AudioPills e Integrazione AI**
- **Server MCP**: Implementato un server Model Context Protocol embedded con 31 tool che permettono a client AI (Claude, Cursor, etc.) di controllare direttamente l'app.
- **AudioPillsMCPBridge**: Sviluppato un helper nativo in Swift per interfacciare Claude Desktop con il server MCP tramite stdio.
- **Trascrizioni granulari**: Aggiunto il supporto ai timestamp a livello di singola parola con visualizzazione dedicata e "Snap to Word" nella precision view.
- **Ottimizzazioni**: Migliorata la gestione della cache e la navigazione tra gli episodi, con il contributo di Alex Raccuglia.
- https://github.com/valeriogalano/AudioPills

📱 **Ecosistema App iOS/macOS**
- **Highlighter**: Nuova app per digitalizzare citazioni. Include OCR con VisionKit (foto-cattura e drag-to-select), persistenza CoreData ed export configurabile verso Obsidian o file Markdown.
- **KeepInTouch**: Unificato il target "Designed for iPad" per semplificare il codice. Aggiunti avatar, badge di urgenza basati su soglie temporali e DatePicker integrato.
- **PrompterCam**: Introdotte le cartelle per categorizzare gli script e il salvataggio delle registrazioni video direttamente nel filesystem dell'app.
- **Localizzazione**: Completata la traduzione in inglese e l'integrazione di termini di servizio e privacy policy per tutte le applicazioni.
- https://github.com/valeriogalano/Highlighter
- https://github.com/valeriogalano/KeepInTouch
- https://github.com/valeriogalano/PrompterCam

📖 Articolo completo: https://pensieriincodice.it/blog/2026-05-22-recap/
#recap