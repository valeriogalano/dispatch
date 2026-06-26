_Questo testo è stato generato con gemini-3-flash-preview_

📦 **Packaging macOS e ottimizzazioni per gli store**

Questa settimana Valerio si è concentrato sul perfezionamento dei processi di build e distribuzione delle sue applicazioni, risolvendo diverse criticità tecniche legate alla firma del codice e alla documentazione per gli utenti.

🍎 **Timebox: Distribuzione e firma su macOS**
Il lavoro principale ha riguardato l'applicazione Timebox, con l'obiettivo di superare le restrizioni di sicurezza di macOS per le versioni distribuite indipendentemente.
- **Configurazione Electron Builder**: Sono stati aggiunti gli entitlements necessari per il packaging corretto dell'applicazione su sistemi Apple ([commit](https://github.com/valeriogalano/Timebox/commit/8d1763d5d2b4aa968a2fab539523d61a07012dfc)).
- **Firma Ad-hoc**: Valerio ha implementato un hook `afterPack` per applicare una firma ad-hoc completa al bundle macOS, disabilitando l'auto-signing di default per garantire la stabilità del pacchetto ([commit](https://github.com/valeriogalano/Timebox/commit/39d51dcc6ceaa15af9f1c8d6c851f8481bcfe7f1)).
- **Guida all'installazione**: È stata aggiornata la documentazione per spiegare come gestire i blocchi di macOS Gatekeeper, includendo istruzioni sull'uso del comando `xattr` per rimuovere manualmente gli attributi di quarantena dalle build non notarizzate ([dettagli](https://github.com/valeriogalano/Timebox/commit/59ca7cf722dbb5cf572f107ade533734dfc059d9)).
- **Release Management**: Il progetto è stato portato alla versione 0.5.2, ripulendo contestualmente i vecchi asset delle release precedenti su GitHub per mantenere il repository ordinato.

📱 **Highlighter: Gestione Store**
- **Asset grafici**: È stata eseguita una riorganizzazione degli screenshot destinati all'App Store per migliorare la presentazione dell'applicazione e ottimizzare la gestione dei materiali per lo store mobile.

📖 Articolo completo: https://pensieriincodice.it/blog/2026-06-26-recap/
#recap