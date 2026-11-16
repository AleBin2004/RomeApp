#!/usr/bin/env python3
"""Aggiorna docs/data/data.json: quote, tabella del mercoledì, grafici, bilanci, news, allerte."""
import bisect, datetime as dt, json, math, os, urllib.parse, urllib.request
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CFG = json.load(open(os.path.join(ROOT, "config.json"), encoding="utf-8"))
OUT = os.path.join(ROOT, "docs", "data", "data.json")
UA = {"User-Agent": "Mozilla/5.0 (monitor-titoli)"}
RANGES = {  # etichetta: parametri di yfinance
    "1G": dict(period="1d", interval="5m"), "1S": dict(period="5d", interval="30m"),
    "1M": dict(period="1mo", interval="1d"), "1A": dict(period="1y", interval="1d"),
    "5A": dict(period="5y", interval="1wk"), "10A": dict(period="10y", interval="1wk"),
    "2000": dict(start="2000-01-01", interval="1mo"),
}

def series(tk, intraday=False, **kw):
    """Chiusure corrette per gli split (auto_adjust=False: niente rettifica dei dividendi)."""
    h = tk.history(auto_adjust=False, **kw)["Close"].dropna()
    return [[ts.isoformat() if intraday else ts.strftime("%Y-%m-%d"), round(float(c), 4)] for ts, c in h.items()]

def weekly(daily, base):
    """Chiusura di ogni mercoledì da `base` in poi (se è festa, l'ultima chiusura precedente)."""
    days = [d for d, _ in daily]
    d, last, out = dt.date.fromisoformat(base), dt.date.fromisoformat(days[-1]), []
    while d <= last:
        i = bisect.bisect_right(days, d.isoformat()) - 1
        if i >= 0: out.append([d.isoformat(), daily[i][1]])
        d += dt.timedelta(days=7)
    return out

def check(w, last, last_date, thr):
    """Perdita rispetto alla base e rispetto al mercoledì precedente."""
    ref = w[-1] if w[-1][0] < last_date or len(w) < 2 else w[-2]
    vb, vw = last / w[0][1] - 1, last / ref[1] - 1
    return {"vs_base": round(vb, 4), "vs_week": round(vw, 4), "hit": vb <= -thr or vw <= -thr}

def num(x):
    try:
        x = float(x); return None if math.isnan(x) else x
    except Exception: return None

def fundamentals(tk):
    o = {}
    try:
        ed = tk.calendar.get("Earnings Date"); o["next_earnings"] = str(ed[0]) if ed else None
    except Exception: pass
    try:
        s = tk.quarterly_income_stmt
        o["quarters"] = [{"d": str(c.date()), "rev": num(s.loc["Total Revenue", c]) if "Total Revenue" in s.index else None,
                          "net": num(s.loc["Net Income", c]) if "Net Income" in s.index else None} for c in list(s.columns)[:4]]
    except Exception: pass
    try:
        i = tk.info; o.update(target=num(i.get("targetMeanPrice")), rating=i.get("recommendationKey"), mcap=num(i.get("marketCap")))
    except Exception: pass
    return o

def rss(q, n=8):
    url = "https://news.google.com/rss/search?q=" + urllib.parse.quote(q + " when:14d") + "&hl=it&gl=IT&ceid=IT:it"
    try:
        root = ET.fromstring(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=25).read())
        out = []
        for i in root.iter("item"):
            try: d = parsedate_to_datetime(i.findtext("pubDate")).isoformat()
            except Exception: d = None
            out.append({"t": i.findtext("title"), "u": i.findtext("link"), "d": d, "s": i.findtext("source")})
        return sorted(out, key=lambda x: x["d"] or "", reverse=True)[:n]
    except Exception as e:
        print("news non disponibili:", q, e); return []

def notify(title, msg):
    topic = os.environ.get("NTFY_TOPIC") or CFG.get("ntfy_topic")
    if not topic: return
    body = json.dumps({"topic": topic, "title": title, "message": msg, "priority": 4, "tags": ["warning"]}).encode()
    try: urllib.request.urlopen(urllib.request.Request("https://ntfy.sh/", data=body, headers={"Content-Type": "application/json"}), timeout=20)
    except Exception as e: print("notifica non inviata:", e)

def main():
    import yfinance as yf
    old = json.load(open(OUT, encoding="utf-8")) if os.path.exists(OUT) else {}
    olds = {x["t"]: x for x in old.get("tickers", [])}
    base, thr, res = CFG["base"], CFG["threshold"], []
    start = (dt.date.fromisoformat(base) - dt.timedelta(days=10)).isoformat()
    for c in CFG["tickers"]:
        t, name = c["t"], c["name"]
        try:
            tk = yf.Ticker(t)
            daily = series(tk, start=start, interval="1d")
            w = weekly(daily, base)
            last, ld = daily[-1][1], daily[-1][0]
            e = {**c, "last": last, "last_date": ld, "prev": daily[-2][1] if len(daily) > 1 else None,
                 "weekly": w, "alert": check(w, last, ld, thr), "fin": fundamentals(tk)}
            e["charts"] = {k: series(tk, intraday=p["interval"][-1] == "m", **p) for k, p in RANGES.items()}
        except Exception as ex:
            print("ERRORE quote", t, ex); e = olds.get(t, dict(c)); e["error"] = str(ex)
        e["news"] = {"news": rss(f"{name} stock"), "bilanci": rss(f"{name} earnings results guidance outlook"),
                     "decisioni": rss(f"{name} announces CEO OR acquisition OR buyback OR dividend OR split OR partnership")}
        res.append(e)
    if all("error" in x for x in res):
        raise RuntimeError("nessun dato scaricato (connessione assente o Yahoo Finance non raggiungibile)")
    hits = [x["t"] for x in res if x.get("alert", {}).get("hit")]
    for x in res:
        if x["t"] in hits and x["t"] not in old.get("alert_state", []):
            a = x["alert"]; notify(f"⚠️ {x['name']} in forte calo", f"{a['vs_base']*100:+.1f}% dalla base · {a['vs_week']*100:+.1f}% dal mercoledì precedente")
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump({"updated": dt.datetime.now(dt.timezone.utc).isoformat(), "base": base, "threshold": thr,
               "alert_state": hits, "tickers": res}, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    print("OK", len(res), "titoli; allerte:", hits)

if __name__ == "__main__":
    main()
