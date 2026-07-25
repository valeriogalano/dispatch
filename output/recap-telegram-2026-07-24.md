_Questo testo è stato generato con claude:claude-haiku-4-5-20251001_

# 🔄 GoodLinks in Obsidian e nuovi orizzonti per Timebox

Valerio ha completato una trasformazione importante del flusso di pubblicazione e introdotto numerosi miglioramenti all'app di time tracking.

## 📚 Pipeline GoodLinks: archiviazione e automazione completa
[**GoodLinks Publisher**](https://github.com/valeriogalano/goodlinks-publisher) è passato da prototipo a sistema robusto di fan-out verso tre canali (Mastodon, Telegram, blog Hugo). La novità principale è l'**archiviazione automatica nel vault Obsidian**: un nuovo job replica la funzione del plugin Readwise creando/aggiornando note con metadata, highlights e contenuto full-text estratto via trafilatura. L'archivio usa il vault come source of truth con matching idempotente su URL normalizzati.

Accanto: **backup automatico dello stato** su Codeberg (published_ids.json versionato in git), **notifiche macOS su errori** eseguiti da launchd, **finestra di 7 giorni** sugli articoli e **schedulazione diurna** (8:20–20:20, ogni ora). L'output Hugo ora scrive direttamente su GitHub API nel repo del blog, garantendo il trigger della CI. Il placeholder `{notes}` estrae il primo highlight anziché il summary.

## ⏱️ Timebox: navigation rifatta e proiezioni settimanali
[**Timebox**](https://github.com/valeriogalano/Timebox) arriva a v0.9.6 con UX più coerente con Todoist: tasti nudi e combinati (Q per QuickLog, Shift+frecce per settimana) ora mantengono la muscle memory degli utenti. La **barra laterale collassa a larghezza zero** (pulsante riposizionato nella topbar), e il nuovo schermo **Giorno** (rinominato da Oggi) accetta navigazione con offset, perfetto per consultare passato e futuro.

In Andamento, il carico settimanale ora proietta fino a fine settimana su due assi: "a piano" (consuntivo + ore pianificate restanti) e "a ritmo" (consuntivo/giorni trascorsi × 7), entrambi con delta vs capacità. Le override ricorrenti si raggruppano e ordinano per giorno (details/summary collassabile). Bug fix: Todoist API v1 accetta `due.date` con orario ISO8601 anziché `due.datetime`, e il tooltip attivo persiste sui blocchi parzialmente loggati.

📖 Articolo completo: https://pensieriincodice.it/blog/2026-07-24-recap/ #recap