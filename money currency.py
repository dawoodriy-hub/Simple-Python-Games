import tkinter as tk
from tkinter import ttk
import urllib.request
import json
import threading

# ── Colours ────────────────────────────────────────────────────────────────────
BG      = "#0d0d0d"
DISP_BG = "#111111"
BTN_BG  = "#1c1c1e"
ACC     = "#ff6b35"
WHT     = "#f5f5f7"
GRY     = "#8e8e93"
GRN     = "#30d158"
RED     = "#ff453a"
HOVER   = "#2c2c2e"

# ── Offline fallback list (used if no internet on startup) ─────────────────────
FALLBACK = {
    "AUD":"Australian Dollar","BGN":"Bulgarian Lev","BRL":"Brazilian Real",
    "CAD":"Canadian Dollar","CHF":"Swiss Franc","CNY":"Chinese Renminbi Yuan",
    "CZK":"Czech Koruna","DKK":"Danish Krone","EUR":"Euro",
    "GBP":"British Pound","HKD":"Hong Kong Dollar","HUF":"Hungarian Forint",
    "IDR":"Indonesian Rupiah","ILS":"Israeli New Sheqel","INR":"Indian Rupee",
    "ISK":"Icelandic Króna","JPY":"Japanese Yen","KRW":"South Korean Won",
    "MXN":"Mexican Peso","MYR":"Malaysian Ringgit","NOK":"Norwegian Krone",
    "NZD":"New Zealand Dollar","PHP":"Philippine Peso","PLN":"Polish Zloty",
    "RON":"Romanian Leu","SEK":"Swedish Krona","SGD":"Singapore Dollar",
    "THB":"Thai Baht","TRY":"Turkish Lira","USD":"US Dollar",
    "ZAR":"South African Rand",
}

OFFLINE_RATES_VS_EUR = {
    "AUD":1.64,"BGN":1.96,"BRL":5.41,"CAD":1.46,"CHF":0.97,"CNY":7.74,
    "CZK":25.2,"DKK":7.46,"EUR":1.0,"GBP":0.85,"HKD":8.31,"HUF":395.0,
    "IDR":17200.0,"ILS":3.91,"INR":89.5,"ISK":148.0,"JPY":160.0,"KRW":1430.0,
    "MXN":18.2,"MYR":5.0,"NOK":11.5,"NZD":1.78,"PHP":61.0,"PLN":4.25,
    "RON":4.97,"SEK":11.2,"SGD":1.44,"THB":38.5,"TRY":34.5,"USD":1.08,
    "ZAR":20.2,
}


class MoneyConverter(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Money Converter")
        self.geometry("500x660")
        self.resizable(False, False)
        self.configure(bg=BG)

        self._rate       = None
        self._currencies = {}   # code -> name  (filled from API or fallback)
        self._codes      = []

        self._build_ui()
        # load currency list then rates
        threading.Thread(target=self._load_currencies, daemon=True).start()

    # ══════════════════════════════════════════════════════════════════════════
    #  BUILD UI
    # ══════════════════════════════════════════════════════════════════════════
    def _build_ui(self):
        # title
        tk.Label(self, text="💱  Money Converter",
                 font=("Arial", 22, "bold"), bg=BG, fg=WHT
                 ).pack(pady=(22, 2))
        tk.Label(self, text="All world currencies  •  Live rates via Frankfurter API",
                 font=("Arial", 11), bg=BG, fg=GRY
                 ).pack()

        # amount
        af = tk.Frame(self, bg=DISP_BG)
        af.pack(fill="x", padx=24, pady=(18, 6))
        tk.Label(af, text="Amount", font=("Arial", 12),
                 bg=DISP_BG, fg=GRY, anchor="w").pack(fill="x", padx=16, pady=(10,0))
        self._amount_var = tk.StringVar(value="1")
        self._amount_entry = tk.Entry(
            af, textvariable=self._amount_var,
            font=("Arial", 32, "bold"), bg=DISP_BG, fg=WHT,
            insertbackground=ACC, relief="flat", justify="right", bd=0)
        self._amount_entry.pack(fill="x", padx=16, pady=(0,12))
        self._amount_var.trace_add("write", lambda *_: self._on_type())

        # FROM
        tk.Label(self, text="From", font=("Arial", 12, "bold"),
                 bg=BG, fg=GRY, anchor="w").pack(fill="x", padx=24, pady=(8,2))
        self._from_var = tk.StringVar(value="USD — US Dollar")
        self._from_box = ttk.Combobox(self, textvariable=self._from_var,
                                      font=("Arial", 13), state="readonly", height=16)
        self._from_box.pack(fill="x", padx=24)
        self._from_box.bind("<<ComboboxSelected>>", lambda e: self._fetch_rate())

        # search FROM
        self._from_search = tk.Entry(self, font=("Arial", 12), bg=BTN_BG, fg=WHT,
                                     insertbackground=ACC, relief="flat",
                                     bd=0)
        self._from_search.pack(fill="x", padx=24, pady=(2,0))
        self._from_search.insert(0, "🔍 Search from currency...")
        self._from_search.bind("<FocusIn>",  lambda e: self._clear_hint(self._from_search))
        self._from_search.bind("<FocusOut>", lambda e: self._add_hint(self._from_search, "🔍 Search from currency..."))
        self._from_search.bind("<KeyRelease>", lambda e: self._filter("from"))

        # swap
        tk.Button(self, text="⇅  Swap",
                  font=("Arial", 13), bg=BTN_BG, fg=ACC,
                  activebackground=HOVER, activeforeground=ACC,
                  relief="flat", bd=0, cursor="hand2",
                  command=self._swap, pady=8
                  ).pack(fill="x", padx=24, pady=8)

        # TO
        tk.Label(self, text="To", font=("Arial", 12, "bold"),
                 bg=BG, fg=GRY, anchor="w").pack(fill="x", padx=24, pady=(0,2))
        self._to_var = tk.StringVar(value="EUR — Euro")
        self._to_box = ttk.Combobox(self, textvariable=self._to_var,
                                    font=("Arial", 13), state="readonly", height=16)
        self._to_box.pack(fill="x", padx=24)
        self._to_box.bind("<<ComboboxSelected>>", lambda e: self._fetch_rate())

        # search TO
        self._to_search = tk.Entry(self, font=("Arial", 12), bg=BTN_BG, fg=WHT,
                                   insertbackground=ACC, relief="flat", bd=0)
        self._to_search.pack(fill="x", padx=24, pady=(2,0))
        self._to_search.insert(0, "🔍 Search to currency...")
        self._to_search.bind("<FocusIn>",  lambda e: self._clear_hint(self._to_search))
        self._to_search.bind("<FocusOut>", lambda e: self._add_hint(self._to_search, "🔍 Search to currency..."))
        self._to_search.bind("<KeyRelease>", lambda e: self._filter("to"))

        # result
        rf = tk.Frame(self, bg=DISP_BG)
        rf.pack(fill="x", padx=24, pady=(16,4))
        self._result_lbl = tk.Label(rf, text="—",
                                    font=("Arial", 36, "bold"),
                                    bg=DISP_BG, fg=GRN, anchor="e")
        self._result_lbl.pack(fill="x", padx=16, pady=(12,2))
        self._rate_lbl = tk.Label(rf, text="",
                                  font=("Arial", 12),
                                  bg=DISP_BG, fg=GRY, anchor="e")
        self._rate_lbl.pack(fill="x", padx=16, pady=(0,10))

        # status
        self._status = tk.Label(self, text="⏳ Loading currencies...",
                                font=("Arial", 11), bg=BG, fg=GRY)
        self._status.pack(pady=(4,0))

        # convert button
        tk.Button(self, text="Convert  →",
                  font=("Arial", 16, "bold"), bg=ACC, fg="white",
                  activebackground="#ff8c5a", activeforeground="white",
                  relief="flat", bd=0, cursor="hand2",
                  command=self._convert, pady=13
                  ).pack(fill="x", padx=24, pady=(10,18))

        self.bind("<Return>", lambda e: self._convert())
        self._style_combo()

    def _style_combo(self):
        s = ttk.Style()
        s.theme_use("default")
        s.configure("TCombobox",
                    fieldbackground=DISP_BG, background=DISP_BG,
                    foreground=WHT, selectbackground=BTN_BG,
                    selectforeground=WHT, arrowcolor=ACC,
                    borderwidth=0, relief="flat")
        s.map("TCombobox",
              fieldbackground=[("readonly", DISP_BG)],
              foreground=[("readonly", WHT)],
              background=[("readonly", BTN_BG)])
        self.option_add("*TCombobox*Listbox.background", DISP_BG)
        self.option_add("*TCombobox*Listbox.foreground", WHT)
        self.option_add("*TCombobox*Listbox.selectBackground", BTN_BG)
        self.option_add("*TCombobox*Listbox.font", "Arial 13")

    # ══════════════════════════════════════════════════════════════════════════
    #  CURRENCY LOADING
    # ══════════════════════════════════════════════════════════════════════════
    def _load_currencies(self):
        try:
            url = "https://api.frankfurter.dev/v2/currencies"
            with urllib.request.urlopen(url, timeout=6) as r:
                data = json.loads(r.read())
            self.after(0, lambda: self._on_currencies(data, live=True))
        except Exception:
            self.after(0, lambda: self._on_currencies(FALLBACK, live=False))

    def _on_currencies(self, data, live):
        self._currencies = dict(sorted(data.items()))
        self._codes      = list(self._currencies.keys())
        entries = [f"{code} — {name}" for code, name in self._currencies.items()]

        self._from_box["values"] = entries
        self._to_box["values"]   = entries

        # set defaults
        self._from_var.set("USD — US Dollar" if "USD" in self._currencies
                           else entries[0])
        self._to_var.set("EUR — Euro" if "EUR" in self._currencies
                         else entries[1])

        n = len(self._currencies)
        src = "live" if live else "offline fallback"
        self._status.configure(
            text=f"✓  {n} currencies loaded ({src})",
            fg=GRN if live else "#ffcc00"
        )
        self._fetch_rate()

    # ══════════════════════════════════════════════════════════════════════════
    #  SEARCH / FILTER
    # ══════════════════════════════════════════════════════════════════════════
    def _clear_hint(self, entry):
        if entry.get().startswith("🔍"):
            entry.delete(0, tk.END)
            entry.configure(fg=WHT)

    def _add_hint(self, entry, hint):
        if not entry.get().strip():
            entry.insert(0, hint)
            entry.configure(fg=GRY)

    def _filter(self, which):
        box    = self._from_box  if which == "from" else self._to_box
        search = self._from_search if which == "from" else self._to_search
        query  = search.get().lower().replace("🔍 search from currency...","").replace("🔍 search to currency...","").strip()

        all_entries = [f"{code} — {name}" for code, name in self._currencies.items()]
        if query:
            filtered = [e for e in all_entries
                        if query in e.lower()]
        else:
            filtered = all_entries

        box["values"] = filtered
        if filtered:
            box.event_generate("<Button-1>")

    # ══════════════════════════════════════════════════════════════════════════
    #  RATE FETCHING
    # ══════════════════════════════════════════════════════════════════════════
    def _get_code(self, var):
        return var.get().split(" — ")[0].strip()

    def _swap(self):
        f, t = self._from_var.get(), self._to_var.get()
        self._from_var.set(t)
        self._to_var.set(f)
        self._fetch_rate()

    def _on_type(self):
        if self._rate is not None:
            self._convert()

    def _fetch_rate(self):
        self._rate = None
        self._status.configure(text="⏳ Fetching live rate...", fg=GRY)
        self._result_lbl.configure(text="—", fg=GRY)
        self._rate_lbl.configure(text="")
        threading.Thread(target=self._fetch_thread, daemon=True).start()

    def _fetch_thread(self):
        fc = self._get_code(self._from_var)
        tc = self._get_code(self._to_var)
        if fc == tc:
            self.after(0, self._same_currency); return
        try:
            url = f"https://api.frankfurter.dev/v2/latest?base={fc}&symbols={tc}"
            with urllib.request.urlopen(url, timeout=6) as r:
                data = json.loads(r.read())
            rate = data["rates"][tc]
            self.after(0, lambda: self._on_rate(rate, fc, tc, live=True))
        except Exception:
            # offline fallback
            try:
                rate = OFFLINE_RATES_VS_EUR.get(tc, 1) / OFFLINE_RATES_VS_EUR.get(fc, 1)
                self.after(0, lambda: self._on_rate(rate, fc, tc, live=False))
            except Exception:
                self.after(0, lambda: self._status.configure(
                    text="⚠  Could not fetch rate", fg=RED))

    def _on_rate(self, rate, fc, tc, live):
        self._rate = rate
        tag = "live" if live else "offline estimate"
        self._status.configure(
            text=f"✓  Rate fetched ({tag})", fg=GRN if live else "#ffcc00")
        self._rate_lbl.configure(text=f"1 {fc}  =  {rate:,.6f} {tc}")
        self._convert()

    def _same_currency(self):
        self._rate = 1.0
        self._status.configure(text="Same currency selected", fg=GRY)
        self._convert()

    # ══════════════════════════════════════════════════════════════════════════
    #  CONVERT
    # ══════════════════════════════════════════════════════════════════════════
    def _convert(self):
        try:
            amount = float(self._amount_var.get().replace(",", ""))
        except ValueError:
            self._result_lbl.configure(text="Invalid amount", fg=RED); return
        if self._rate is None: return

        result  = amount * self._rate
        to_code = self._get_code(self._to_var)

        if result >= 1_000_000:    fmt = f"{result:,.2f}"
        elif result >= 1:          fmt = f"{result:,.4f}"
        else:                      fmt = f"{result:,.8f}"

        self._result_lbl.configure(text=f"{fmt}  {to_code}", fg=GRN)


if __name__ == "__main__":
    app = MoneyConverter()
    app.mainloop()