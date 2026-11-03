"""Market Monitor scan: counts of US stocks by move size. Runs daily via GitHub Actions."""
import io, json, datetime as dt
import pandas as pd, requests, yfinance as yf

MIN_PRICE = 3        # ignore stocks below this close
MIN_VOLUME = 100_000 # ignore stocks trading less than this many shares on the day
BATCH = 400

def universe():
    urls = ["https://www.nasdaqtrader.com/dynamic/symdir/nasdaqlisted.txt",
            "https://www.nasdaqtrader.com/dynamic/symdir/otherlisted.txt"]
    syms = []
    for u in urls:
        df = pd.read_csv(io.StringIO(requests.get(u, timeout=60).text), sep="|")
        df = df[df.iloc[:, 0].notna() & ~df.iloc[:, 0].astype(str).str.startswith("File Creation")]
        if "Test Issue" in df: df = df[df["Test Issue"] == "N"]
        if "ETF" in df: df = df[df["ETF"] == "N"]
        col = "Symbol" if "Symbol" in df else "ACT Symbol"
        syms += df[col].astype(str).tolist()
    return sorted({s for s in syms if s.isalpha() and len(s) <= 5})

def run():
    close, vol = [], []
    syms = universe()
    for i in range(0, len(syms), BATCH):
        part = syms[i:i + BATCH]
        try:
            d = yf.download(part, period="4mo", interval="1d", auto_adjust=False,
                            progress=False, threads=True, group_by="column")
            close.append(d["Close"]); vol.append(d["Volume"])
        except Exception as e:
            print("batch failed", i, e)
    C = pd.concat(close, axis=1).dropna(axis=1, how="all")
    V = pd.concat(vol, axis=1).reindex(columns=C.columns)
    C = C.dropna(how="all"); V = V.loc[C.index]
    last = C.index[-1]
    c = C.iloc[-1]; v = V.iloc[-1]
    ok = (c >= MIN_PRICE) & (v >= MIN_VOLUME)

    def chg(n):  # % change over n trading days
        return (c / C.iloc[-1 - n] - 1) * 100
    cut = last - pd.Timedelta(days=34)
    c34 = C[C.index <= cut].iloc[-1]
    ch34 = (c / c34 - 1) * 100
    d1, q, m = chg(1), chg(65), chg(20)

    def cnt(s, up, thr):
        return int((((s >= thr) if up else (s <= -thr)) & ok).sum())

    row = {"date": last.strftime("%Y-%m-%d"),
           "up4": cnt(d1, 1, 4), "down4": cnt(d1, 0, 4),
           "up25q": cnt(q, 1, 25), "down25q": cnt(q, 0, 25),
           "up25m": cnt(m, 1, 25), "down25m": cnt(m, 0, 25),
           "up50m": cnt(m, 1, 50), "down50m": cnt(m, 0, 50),
           "up13_34": cnt(ch34, 1, 13), "down13_34": cnt(ch34, 0, 13),
           "universe": int(ok.sum())}
    try: data = json.load(open("data.json"))
    except Exception: data = {"history": []}
    hist = [h for h in data["history"] if h["date"] != row["date"]] + [row]
    hist.sort(key=lambda h: h["date"])
    json.dump({"updated": dt.datetime.utcnow().isoformat() + "Z", "history": hist[-250:]},
              open("data.json", "w"), indent=1)
    print(row)

if __name__ == "__main__":
    run()
