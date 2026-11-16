# Monitor Titoli (locale e privato)

Gira solo sul tuo computer: non viene pubblicato su Internet e non serve nessun account. Ogni giorno feriale alle 23:00 (dopo la chiusura di Wall Street) scarica quote e news, aggiorna la tabella del mercoledì, i grafici, i bilanci e le allerte (perdita oltre il 10%). Se il computer era spento, recupera l’aggiornamento appena lo riaccendi.

## Avvio
1. Installa Python 3 da python.org (Windows: spunta "Add python.exe to PATH"). Su Mac di solito c’è già.
2. Windows: doppio clic su `avvia.bat`. Mac: doppio clic su `avvia.command` (se non parte: `python3 server.py` da Terminale).
3. Alla prima apertura l’app mostra solo la riga base: per avere subito dati e grafici, da un terminale nella cartella esegui `python server.py --aggiorna` (qualche minuto), poi avvia come sopra.
4. Lascia la finestra aperta. Per farlo partire da solo: Windows, metti un collegamento ad `avvia.bat` nella cartella Esecuzione automatica (Win+R → `shell:startup`); Mac, Impostazioni → Generali → Elementi di login.

## Sul telefono
- **A casa (stessa Wi-Fi):** apri l’indirizzo "Dal telefono" mostrato nella finestra (tipo `http://192.168.1.20:8080`). Poi aggiungilo alla Home: iPhone Condividi → Aggiungi a Home; Android menu ⋮ → Aggiungi a schermata Home. Il computer deve essere acceso.
- **Fuori casa, sempre in privato:** installa Tailscale (gratuito) su computer e telefono, con lo stesso account. Poi apri `http://nome-del-computer:8080`. Nessuno oltre ai tuoi dispositivi può raggiungerlo.

## Notifiche sul telefono (facoltative)
Installa l’app gratuita **ntfy**, iscriviti a un nome lungo e casuale (es. `titoli-k7x93qz-2026`) e scrivilo in `config.json` alla voce `ntfy_topic`. Nota: il messaggio di allerta passa dal server pubblico ntfy.sh (contiene solo nome del titolo e percentuali). Senza questa voce non parte nessuna notifica, resta il banner nell’app.

## Personalizzare
`config.json`: titoli (simboli di Yahoo Finance), `base` (prima settimana di riferimento, un mercoledì) e `threshold` (0.10 = 10%).

## Note
- Prezzi e bilanci vengono da Yahoo Finance, le news da Google News: possono avere ritardi o errori. Non è consulenza finanziaria.
- Gli split (es. SanDisk 8 per 1 del 20/11/2026) sono corretti automaticamente.
- Le notizie mostrano solo titolo, fonte e link all’originale.
- L’app è raggiungibile da chiunque sia sulla tua stessa rete Wi-Fi: usa una rete di cui ti fidi.
