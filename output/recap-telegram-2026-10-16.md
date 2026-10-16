⚡ Prestazioni web, tariffe a forfait e nuovi flussi per gli agenti

Valerio ha concentrato il lavoro su alleggerire il caricamento del sito, espandere la gestione economica in Timebox e rifinire permessi e automazioni per gli agenti locali.

🌐 [Pensieri in codice](https://github.com/valeriogalano/pensieriincodice-website)
- **Miniature WebP e cache**: ha introdotto miniature a 800px in formato WebP per copertine degli episodi, player audio e schede di ricerca, evitando il download dei file originali ad alta risoluzione a ogni visita; la pipeline di distribuzione ora conserva le risorse elaborate per non rigenerarle a ogni build.
- **Gestione risorse grafiche**: ha corretto il template delle anteprime per limitare il ridimensionamento alle sole immagini raster, evitando errori in fase di compilazione su file SVG o pagine di errore.

⏱️ [Timebox](https://github.com/valeriogalano/Timebox)
- **Prezzo fisso e tariffa effettiva**: ha aggiunto il supporto ai progetti venduti a importo forfettario, calcolando la tariffa oraria effettiva in base al tempo registrato.
- **Pianificazione su iPhone**: ha portato la visualizzazione del piano giornaliero sulla schermata mobile, mostrando ore previste e già coperte sopra i contatori, e ha distanziato l'intestazione per evitare la sfocatura della barra di stato.
- **Uniformità e pulizia**: ha centralizzato i nomi delle fasce orarie (Mattina, Pomeriggio, Sera) in un'unica definizione ed eliminato le rettifiche di stima che arrotondate al quarto d'ora non producevano variazioni.

🤖 Agent Skills
- **Accesso al NAS e gestione posta**: ha predisposto script per montare la condivisione multimediale di rete con credenziali protette e configurato un flusso per consultare le caselle email con regole rigide di sola lettura e stesura bozze.
- **Permessi e strumenti**: ha limitato i comandi eseguibili senza conferma sul gestore di password, collegato il salvataggio dei link di lettura a GoodLinks tramite interfaccia locale e allineato gli agenti alla versione corrente di Haiku.

📖 Articolo completo: https://pensieriincodice.it/blog/2026-10-16-recap/
#recap

_Generato con gemini-3.8-flash_
