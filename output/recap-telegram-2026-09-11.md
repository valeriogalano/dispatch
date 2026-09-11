🛠️ **Interfacce mobili e regole per gli assistenti**

Questa settimana il lavoro di Valerio si è concentrato sull'esperienza d'uso da mobile e sulla sicurezza delle automazioni, con un'importante riorganizzazione del modo in cui gli assistenti digitali gestiscono dati e comunicazioni.

🌐 [Pensieri in codice - Website](https://github.com/valeriogalano/pensieriincodice-website)
* **Player ottimizzato:** ha risolto un problema di visualizzazione su Safari e Firefox mobile impostando l'altezza del player espanso a `100dvh`, recuperando spazio verticale utile per i controlli e la trascrizione su schermi piccoli.
* **Copertina dinamica:** ha fatto in modo che la locandina dell'episodio collassi quando si scorrono i capitoli, raddoppiando l'area visibile per la lettura ed evitando che la lista si riposizioni da sola.

🤖 **Botcaster e Agent Skills**
* **Sicurezza delle chiavi:** ha protetto i token di GitHub e Obsidian nei server MCP passandoli tramite variabili d'ambiente anziché riga di comando, impedendo che rimangano visibili nei processi di sistema.
* **Antispam più severo:** in Botcaster ha corretto un bug che permetteva di aggirare la verifica uscendo e rientrando dal gruppo, e ripristinato il corretto sblocco dei permessi per chi supera il controllo.
* **Istruzioni centralizzate:** ha unificato le regole operative per Claude e Codex, inserito una competenza specifica per mappare le responsabilità dei progetti dei clienti e stabilito l'obbligo di mostrare un'anteprima di ogni testo prima di pubblicarlo su tracker esterni.

⏱️ [Timebox](https://github.com/valeriogalano/Timebox)
* **Filtro archiviati:** ha rimosso i progetti archiviati dai budget dell'andamento e dalla selezione per l'importazione da Todoist.
* **Quicklog preciso:** ha corretto la ricerca rapida per fare in modo che rispetti la soglia di ore e minuti configurata, evitando che inserimenti rapidi vengano interpretati male.
* **Infrastruttura:** ha aggiornato le GitHub Actions alla versione 5 per superare la deprecazione di Node 20 e ripristinato la misurazione dei test di copertura per i componenti React.

📖 Articolo completo: https://pensieriincodice.it/blog/2026-09-11-recap/
#recap

_Questo testo è stato generato con gemini-3.5-flash_
