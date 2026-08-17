🛠️ Sottotitoli, Instagram senza Facebook e il rilascio di Book Highlighter 1.2.0

Questa settimana Valerio ha concentrato gli sforzi sul completamento di Book Highlighter 1.2.0 e su una profonda ristrutturazione delle automazioni del podcast, semplificando la pubblicazione su Instagram.

🎙️ **Automazione Podcast e Instagram**

*   **Instagram Login:** [Podcast Audiogram Publisher](https://github.com/valeriogalano/podcast-audiogram-publisher) e [Automation](https://github.com/valeriogalano/podcast-audiogram-automation) passano alla nuova API di Instagram, eliminando l'obbligo di una pagina Facebook associata e riducendo l'attrito nella gestione dei token.
*   **Sottotitoli e layout:** Abilitati i sottotitoli impressi nei video, posizionati nella fascia bassa per non sovrapporsi alle interfacce social, insieme alla chiamata all'azione per il link in bio.
*   **Sonda dei token:** Aggiunta una verifica oraria dello stato del token Instagram per registrare subito nei log eventuali errori di autenticazione di Meta.
*   **Routing Telegram:** Divisi i canali di destinazione in base alla durata del video: le storie brevi vanno su più chat, i messaggi video lunghi solo sul canale principale.

📚 **Book Highlighter 1.2.0**

*   **Copertine offline:** Salvataggio delle immagini di copertina direttamente nel database locale, supportato da una cache più robusta per evitare continui download.
*   **Condivisione personalizzabile:** Nuove opzioni per escludere i dettagli del libro o della pagina sia dalle immagini generate che dalle esportazioni di testo.
*   **Firme e configurazione:** Spostata l'identità di firma nei file di configurazione locali per consentire build su dispositivi fisici senza esporre chiavi private nel repository. Risolto anche un blocco sulle richieste a Google Books inviando l'identificativo corretto dell'applicazione.

🧠 **AudioPills e Manutenzione**

*   **Modelli e Keychain:** In AudioPills, le chiavi API passano nel Keychain di sistema. Il fornitore Claude ora usa Sonnet 5 di default per tagliare i costi del 40% rispetto a Opus, e impara a ignorare i blocchi di "pensiero" prima di estrarre i segmenti consigliati.
*   **Runtime CI:** Aggiornate le pipeline di build di tutti i progetti per abbandonare il runtime Node 20 deprecato a favore di Node 24.

📖 Articolo completo: https://pensieriincodice.it/blog/2026-08-14-recap/
#recap

_Questo testo è stato generato con gemini-3.5-flash_
