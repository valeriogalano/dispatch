🔄 Dispatch e il Sistema di Recap
Valerio ha riscritto il progetto Dispatch, il sistema che genera i recap settimanali automatici. Dispatch ora firma i suoi recap e ha una voce propria: Engram non è una mascotte, ma la memoria del progetto che racconta cosa è stato fatto mantenendo uno stile asciutto e privo di enfasi.

**Architettura dei recap** — Il sistema legge commit e note manuali (episodi, articoli, release) generate fuori da git, in modo che nulla vada perso. Se in una settimana non ci sono commit, il digest non viene nemmeno generato e la catena si ferma da sé. I recap vengono ritentati ogni ora nel giorno di pubblicazione, così una failure in una fase intermedia non blocca tutto: il sistema registra un marker per evitare di inviare due volte lo stesso messaggio Telegram.

**Resilienza** — La pipeline è stata indurita: collect.py ora distingue un errore 403 da una rate limit e ritenta solo nel secondo caso, capping il sleep a un'ora. Il prefisso "!" non scatena più il flag breaking-change se il commit non ha un prefisso convenzionale. I recap lunghi vengono spezzati automaticamente prima di superare i 4096 caratteri di Telegram. publish_telegram.py ricorda quale recap ha già inviato, quindi una ri-esecuzione non duplica il messaggio.

**Frontend** — I link markdown vengono ora convertiti correttamente in HTML (`[testo](url)`), il signature di Engram non appare due volte (una nel blog, una in Telegram), e i modelli AI dichiarano il loro nome senza ridondanza.

🌐 Sito e Feed
Sul sito di Pensieri in codice, Valerio ha aggiornato i template Hugo alle nuove convenzioni: `languageCode` diventa `locale`, e tutti gli 8 template che leggevano `.Site.LanguageCode` sono stati allineati. I feed ora portano l'articolo completo (.Content) invece del riassunto troncato. Le icone PWA hanno un file dedicato senza bordo bianco. L'autore appare accanto alla data nei post del blog, e i recap sono attribuiti a Engram.

📦 Moduli e Tools
`podcast-feed-hugo` è salito a v0.3.0 con un breaking change: il campo `audio` diventa `audio_file` perché entra in conflitto con il template Open Graph di Hugo. La demo del modulo è stata spostata in exampleSite/ per evitare che importatori ereditino contenuto demo. Il modulo dichiara ora il minimo Hugo richiesto (v0.158.0).

`Timebox` ha ricevuto una serie di migliorie: la legenda dei glifi (segnali di carico, stato di fatturazione) è ora accessibile dal pulsante ? in top bar. Il timesheet del giorno mostra ora tutti i progetti, non solo quelli già tracciati. Le aree di lavoro hanno un default settimanale (attivo/minimo/chiuso) e ogni slot della giornata (AM/PM/Sera) ha la propria capacità. Gli alert sui limiti settimanali distinguono ora tra area e progetto. I glifi sono diventati SVG per una coerenza visiva che Open Sans non garantisce.

📖 Articolo completo: https://pensieriincodice.it/blog/2026-07-31-recap/ #recap

_Questo testo è stato generato con claude-haiku-4-5-20251001_
