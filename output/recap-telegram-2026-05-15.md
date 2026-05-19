_Questo testo è stato generato con gemini-3-flash-preview_

🛠️ Settimana di "pulizie di primavera" e bug hunting

Questa settimana mi sono concentrato sul rendere l'intera infrastruttura che ruota attorno al podcast un po' più solida e resiliente. Tra una registrazione e l'altra, ho messo mano ad alcuni automatismi che stavano facendo i capricci e ho iniziato a recuperare un pezzo della mia storia digitale che non volevo assolutamente andasse perduta, perché alla fine il codice è anche memoria.

🌐 **Evoluzione del sito e un tuffo nel passato**
Il sito di Pensieri in Codice sta crescendo e, con l'aumentare dei contenuti, la gestione della lista dei post stava diventando un po' caotica. Ho deciso di intervenire sulla struttura per garantire una navigazione migliore e per fare spazio a vecchi ricordi.

*   **Paginazione del Blog**: Ho aggiornato il layout della lista degli articoli per utilizzare le pagine paginate. Era un passaggio necessario per evitare di avere un "muro" di contenuti infinito e per migliorare le performance di caricamento.
*   **Importazione Storica**: Ho completato l'importazione dei vecchi post dal mio storico blog "daredevel". È stato un lavoro di recupero importante per centralizzare tutta la mia produzione tecnica in un unico posto.
*   **Recap Settimanali**: Ho rifinito il sistema dei recap (proprio come quello che stai leggendo!), correggendo alcuni path delle immagini e aggiungendo i tag corretti per distinguerli dai contenuti originali.
*   **Repository**: https://github.com/valeriogalano/pensieriincodice-website

🤖 **Automatismi più robusti (Mastodon e YouTube)**
Non c'è niente di peggio di un bot che fallisce silenziosamente. Mi sono accorto che alcuni dei miei script di automazione avevano dei punti deboli nella gestione degli errori e nei permessi, quindi ho deciso di blindarli.

*   **Gestione Errori Mastodon**: Nel tool che pubblica gli aggiornamenti RSS su Mastodon, ho corretto un bug subdolo. Prima, se l'aggiornamento della variabile `LAST_PUBLISHED_URLS` su GitHub falliva (magari per un token scaduto), il job segnalava comunque successo. Risultato? Al giro dopo ripubblicava lo stesso post all'infinito. Ora lo script solleva un'eccezione esplicita e interrompe il processo se qualcosa va storto.
*   **Fallback OAuth YouTube**: Per quanto riguarda il publisher degli audiogrammi, ho migliorato la gestione dei token YouTube. Se il refresh token scade (cosa che succede dopo circa 6 mesi di inattività), il sistema ora gestisce il fallback in modo più intelligente invece di crashare, permettendomi di ri-autorizzare il flusso senza perdere dati.
*   **Repository Mastodon**: https://github.com/valeriogalano/podcast-rss-to-mastodon
*   **Repository Audiogram**: https://github.com/valeriogalano/podcast-audiogram-publisher

Sistemare questi "debiti tecnici" è sempre una bella soddisfazione, specialmente quando sai che renderanno la tua vita più semplice nei mesi a venire. Buona programmazione!

#recap