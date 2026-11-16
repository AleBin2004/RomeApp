#!/usr/bin/env python3
"""Monitor Titoli in locale: aggiorna i dati ogni giorno feriale alle 23:00 e serve l'app sulla tua rete."""
import datetime as dt, functools, http.server, json, os, socket, sys, threading, time
ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import update
PORT, SLOT_HOUR = 8080, 23   # 23:00 ora locale: Wall Street ha già chiuso (22:00 in Italia)

def last_slot(now):
    s = now.replace(hour=SLOT_HOUR, minute=0, second=0, microsecond=0)
    if s > now: s -= dt.timedelta(days=1)
    while s.weekday() > 4: s -= dt.timedelta(days=1)   # solo lun-ven
    return s

def due():
    now = dt.datetime.now().astimezone()
    try: u = dt.datetime.fromisoformat(json.load(open(update.OUT, encoding="utf-8"))["updated"])
    except Exception: return True
    return u < last_slot(now)   # recupera automaticamente se il computer era spento

def loop():
    while True:
        if due():
            try: update.main()
            except Exception as e: print("Aggiornamento non riuscito, riprovo tra 10 minuti:", e)
        time.sleep(600)

class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass

def lan_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM); s.connect(("10.255.255.255", 1)); return s.getsockname()[0]
    except Exception: return "IP-del-computer"

if __name__ == "__main__":
    if "--aggiorna" in sys.argv:        # un solo aggiornamento, poi esce (utile per provare)
        update.main(); sys.exit()
    threading.Thread(target=loop, daemon=True).start()
    h = functools.partial(Quiet, directory=os.path.join(ROOT, "docs"))
    print(f"Monitor Titoli attivo.\n  Su questo computer: http://localhost:{PORT}\n  Dal telefono (stessa Wi-Fi): http://{lan_ip()}:{PORT}\nLascia questa finestra aperta (Ctrl+C per fermare).")
    http.server.ThreadingHTTPServer(("0.0.0.0", PORT), h).serve_forever()
