🤖 Più controllo per gli agenti e precisione in Timebox

Questa settimana Valerio si è concentrato sulla standardizzazione delle istruzioni per le IA tra i vari progetti e ha introdotto affinamenti all'integrazione di Timebox con Todoist.

⚙️ Istruzioni per Claude e nuove barriere per gli agenti
* **Allineamento CLAUDE.md**: ha configurato l'importazione diretta delle regole di sviluppo nei file di configurazione di Claude Code su [Dispatch](https://github.com/valeriogalano/dispatch), sul [sito di Pensieri in codice](https://github.com/valeriogalano/pensieriincodice-website) e sui repository di [Podcast Quiz](https://github.com/valeriogalano/podcast-quiz-to-telegram), [GoodLinks Publisher](https://github.com/valeriogalano/goodlinks-publisher), [Audiogram Generator](https://github.com/valeriogalano/podcast-audiogram-generator) e [Audiogram Publisher](https://github.com/valeriogalano/podcast-audiogram-publisher).
* **Agent Skills**: ha aggiunto una verifica all'avvio che segnala i repository fuori convenzione e ha introdotto script di controllo (*hook*) per impedire commit diretti sui rami protetti o l'invio accidentale di credenziali.

⏱️ Sincronizzazione e correzioni in [Timebox](https://github.com/valeriogalano/Timebox)
* **Integrazione Todoist**: ora il sistema avvisa se un progetto non esiste più su Todoist, associa i nuovi progetti basandosi sul colore dell'area e mostra le attività senza un progetto corrispondente invece di ignorarle.
* **Miglioramenti visivi**: ha reso l'altezza dei blocchi ricorrenti proporzionale alle ore reali per non schiacciare i blocchi brevi e ha migliorato il contrasto dei caratteri per facilitare la lettura.
* **Calcolo divergenze**: ha corretto un bug che considerava le domeniche come giorni di inizio settimana creando false deviazioni e ha perfezionato la formula per calcolare la media delle discrepanze sull'intero storico.

💬 Notifiche più chiare in Botcaster
* **Nomi al posto di ID**: la notifica di espulsione inviata agli amministratori per mancata verifica ora mostra i nomi utente e i titoli dei gruppi anziché i soli identificativi numerici.

📖 Articolo completo: https://pensieriincodice.it/blog/2026-09-18-recap/
#recap

_Questo testo è stato generato con gemini-3.5-flash_
