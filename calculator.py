import tkinter as tk
from tkinter import ttk
import re, math, pyperclip

# ══════════════════════════════════════════════════════════════════════════════
#  THEMES
# ══════════════════════════════════════════════════════════════════════════════
THEMES = {
    "dark": {
        "bg":       "#0d0d0d",
        "disp_bg":  "#111111",
        "btn_num":  "#1c1c1e",
        "btn_op":   "#2a2a2e",
        "btn_eq":   "#ff6b35",
        "btn_clr":  "#3a3a3c",
        "btn_sci":  "#1a2a3a",
        "txt_wht":  "#f5f5f7",
        "txt_org":  "#ff6b35",
        "txt_gry":  "#8e8e93",
        "txt_sci":  "#4fc3f7",
        "hv_num":   "#2c2c2e",
        "hv_op":    "#3c3c3e",
        "hv_eq":    "#ff8c5a",
        "hv_clr":   "#4a4a4c",
        "hv_sci":   "#2a3a4a",
        "hist_bg":  "#0a0a0a",
        "hist_fg":  "#cccccc",
        "hist_sel": "#1e1e2e",
        "copy_bg":  "#1a3a1a",
        "copy_fg":  "#66ff66",
    },
    "light": {
        "bg":       "#f2f2f7",
        "disp_bg":  "#ffffff",
        "btn_num":  "#ffffff",
        "btn_op":   "#e8e8ed",
        "btn_eq":   "#ff6b35",
        "btn_clr":  "#d1d1d6",
        "btn_sci":  "#e0f0ff",
        "txt_wht":  "#1c1c1e",
        "txt_org":  "#ff6b35",
        "txt_gry":  "#6e6e73",
        "txt_sci":  "#007aff",
        "hv_num":   "#e5e5ea",
        "hv_op":    "#d8d8dd",
        "hv_eq":    "#ff8c5a",
        "hv_clr":   "#c0c0c5",
        "hv_sci":   "#c8e0f8",
        "hist_bg":  "#f9f9f9",
        "hist_fg":  "#333333",
        "hist_sel": "#e0e0ff",
        "copy_bg":  "#e0ffe0",
        "copy_fg":  "#006600",
    }
}

# ══════════════════════════════════════════════════════════════════════════════
#  TOOLTIP
# ══════════════════════════════════════════════════════════════════════════════
class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text   = text
        self.tip    = None
        widget.bind("<Enter>", self._show)
        widget.bind("<Leave>", self._hide)

    def _show(self, event=None):
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 4
        self.tip = tk.Toplevel(self.widget)
        self.tip.wm_overrideredirect(True)
        self.tip.wm_geometry(f"+{x}+{y}")
        lbl = tk.Label(self.tip, text=self.text,
                       font=("Arial", 11), bg="#333333", fg="#ffffff",
                       relief="flat", padx=8, pady=4)
        lbl.pack()

    def _hide(self, event=None):
        if self.tip:
            self.tip.destroy()
            self.tip = None


# ══════════════════════════════════════════════════════════════════════════════
#  CALCULATOR
# ══════════════════════════════════════════════════════════════════════════════
class Calculator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Calculator")
        self.resizable(False, False)

        self._expr      = ""
        self._prev      = ""
        self._just_eq   = False
        self._sci_mode  = False
        self._theme_nm  = "dark"
        self._T         = THEMES["dark"]
        self._history   = []          # list of "expr = result" strings
        self._copy_after = None

        self._build_ui()
        self._apply_theme()
        self._refresh()

    # ══════════════════════════════════════════════════════════════════════════
    #  BUILD UI
    # ══════════════════════════════════════════════════════════════════════════
    def _build_ui(self):
        T = self._T

        # ── top bar ───────────────────────────────────────────────────────────
        self._top = tk.Frame(self, bg=T["bg"])
        self._top.pack(fill="x", padx=14, pady=(12, 0))

        self._theme_btn = tk.Button(
            self._top, text="☀  Light", font=("Arial", 11), relief="flat",
            bg=T["btn_clr"], fg=T["txt_gry"], cursor="hand2", bd=0,
            command=self._toggle_theme, padx=8, pady=4
        )
        self._theme_btn.pack(side="right")
        Tooltip(self._theme_btn, "Toggle light / dark mode")

        self._sci_btn = tk.Button(
            self._top, text="𝑓(𝑥)  Scientific", font=("Arial", 11), relief="flat",
            bg=T["btn_clr"], fg=T["txt_gry"], cursor="hand2", bd=0,
            command=self._toggle_sci, padx=8, pady=4
        )
        self._sci_btn.pack(side="left")
        Tooltip(self._sci_btn, "Toggle scientific mode  [Tab]")

        # ── display ───────────────────────────────────────────────────────────
        self._disp_frame = tk.Frame(self, bg=T["disp_bg"], bd=0)
        self._disp_frame.pack(fill="x", padx=14, pady=(8, 6))

        self._hist_var = tk.StringVar(value="")
        self._main_var = tk.StringVar(value="0")

        self._hist_lbl = tk.Label(
            self._disp_frame, textvariable=self._hist_var,
            font=("Arial", 13), bg=T["disp_bg"], fg=T["txt_gry"],
            anchor="e", justify="right"
        )
        self._hist_lbl.pack(fill="x", padx=16, pady=(10, 0))

        self._main_lbl = tk.Label(
            self._disp_frame, textvariable=self._main_var,
            font=("Arial", 56, "bold"), bg=T["disp_bg"], fg=T["txt_wht"],
            anchor="e", justify="right", cursor="hand2"
        )
        self._main_lbl.pack(fill="x", padx=16, pady=(0, 4))
        self._main_lbl.bind("<Button-1>", self._copy_result)
        Tooltip(self._main_lbl, "Click to copy result")

        self._copy_lbl = tk.Label(
            self._disp_frame, text="", font=("Arial", 11),
            bg=T["disp_bg"], fg=T["copy_fg"], anchor="e"
        )
        self._copy_lbl.pack(fill="x", padx=16, pady=(0, 8))

        # ── scientific panel (hidden by default) ──────────────────────────────
        self._sci_frame = tk.Frame(self, bg=T["bg"])
        # not packed yet — shown on toggle

        sci_buttons = [
            ("sin",  "sin(x)  →  sine",              "sin({})"),
            ("cos",  "cos(x)  →  cosine",             "cos({})"),
            ("tan",  "tan(x)  →  tangent",            "tan({})"),
            ("√",    "√x  →  square root",            "sqrt({})"),
            ("x²",   "x²  →  square",                 "sq({})"),
            ("xʸ",   "xʸ  →  power  (use ^ key too)", "pow"),
            ("log",  "log(x)  →  log base 10",        "log({})"),
            ("ln",   "ln(x)  →  natural log",         "ln({})"),
            ("π",    "π  →  3.14159…",                "pi"),
            ("e",    "e  →  2.71828…",                "eu"),
            ("(",    "Open bracket",                  "("),
            (")",    "Close bracket",                 ")"),
        ]
        self._sci_btns = []
        for i, (lbl, tip, cmd) in enumerate(sci_buttons):
            r, c = divmod(i, 6)
            btn = tk.Button(
                self._sci_frame, text=lbl,
                font=("Arial", 14, "bold"),
                bg=T["btn_sci"], fg=T["txt_sci"],
                activebackground=T["hv_sci"], activeforeground=T["txt_sci"],
                relief="flat", bd=0, cursor="hand2",
                command=lambda k=cmd: self._sci_press(k),
                padx=0, pady=8
            )
            btn.grid(row=r, column=c, padx=4, pady=3, sticky="nsew")
            btn.bind("<Enter>", lambda e, b=btn: b.configure(bg=self._T["hv_sci"]))
            btn.bind("<Leave>", lambda e, b=btn: b.configure(bg=self._T["btn_sci"]))
            Tooltip(btn, tip)
            self._sci_btns.append(btn)

        for c in range(6):
            self._sci_frame.grid_columnconfigure(c, weight=1)
        for r in range(2):
            self._sci_frame.grid_rowconfigure(r, weight=1)

        # ── main button grid ──────────────────────────────────────────────────
        self._grid_frame = tk.Frame(self, bg=T["bg"])
        self._grid_frame.pack(fill="both", expand=True, padx=14, pady=(0, 4))

        layout = [
            [("AC",  "btn_clr","hv_clr","txt_wht",1,"Clear all  [Esc]"),
             ("+/-", "btn_clr","hv_clr","txt_wht",1,"Negate"),
             ("%",   "btn_clr","hv_clr","txt_wht",1,"Percentage  [%]"),
             ("/",   "btn_op", "hv_op", "txt_org",1,"Divide  [/]")],

            [("7",   "btn_num","hv_num","txt_wht",1,"7"),
             ("8",   "btn_num","hv_num","txt_wht",1,"8"),
             ("9",   "btn_num","hv_num","txt_wht",1,"9"),
             ("*",   "btn_op", "hv_op", "txt_org",1,"Multiply  [*]")],

            [("4",   "btn_num","hv_num","txt_wht",1,"4"),
             ("5",   "btn_num","hv_num","txt_wht",1,"5"),
             ("6",   "btn_num","hv_num","txt_wht",1,"6"),
             ("-",   "btn_op", "hv_op", "txt_org",1,"Subtract  [-]")],

            [("1",   "btn_num","hv_num","txt_wht",1,"1"),
             ("2",   "btn_num","hv_num","txt_wht",1,"2"),
             ("3",   "btn_num","hv_num","txt_wht",1,"3"),
             ("+",   "btn_op", "hv_op", "txt_org",1,"Add  [+]")],

            [("0",   "btn_num","hv_num","txt_wht",2,"0"),
             (".",   "btn_num","hv_num","txt_wht",1,"Decimal point  [.]"),
             ("=",   "btn_eq", "hv_eq", "txt_wht",1,"Calculate  [Enter]")],
        ]

        self._main_btns = []
        for r, row in enumerate(layout):
            c = 0
            for lbl, bg_k, hv_k, fg_k, span, tip in row:
                btn = tk.Button(
                    self._grid_frame, text=lbl,
                    font=("Arial", 22, "bold"),
                    bg=T[bg_k], fg=T[fg_k],
                    activebackground=T[hv_k], activeforeground=T[fg_k],
                    relief="flat", bd=0, cursor="hand2",
                    command=lambda k=lbl: self._press(k),
                    pady=10
                )
                btn.grid(row=r, column=c, columnspan=span,
                         padx=4, pady=4, sticky="nsew")
                btn.bind("<Enter>", lambda e, b=btn, h=hv_k: b.configure(bg=self._T[h]))
                btn.bind("<Leave>", lambda e, b=btn, o=bg_k: b.configure(bg=self._T[o]))
                Tooltip(btn, tip)
                self._main_btns.append((btn, bg_k, hv_k, fg_k))
                c += span
            self._grid_frame.grid_rowconfigure(r, weight=1)

        for col in range(4):
            self._grid_frame.grid_columnconfigure(col, weight=1)

        # ── history panel ─────────────────────────────────────────────────────
        self._hist_frame = tk.Frame(self, bg=T["bg"])
        self._hist_frame.pack(fill="x", padx=14, pady=(0, 10))

        hist_top = tk.Frame(self._hist_frame, bg=T["bg"])
        hist_top.pack(fill="x")

        tk.Label(hist_top, text="History", font=("Arial", 11, "bold"),
                 bg=T["bg"], fg=T["txt_gry"]).pack(side="left", padx=4)

        self._clr_hist_btn = tk.Button(
            hist_top, text="Clear history", font=("Arial", 10),
            bg=T["bg"], fg=T["txt_gry"], relief="flat", bd=0,
            cursor="hand2", command=self._clear_history
        )
        self._clr_hist_btn.pack(side="right", padx=4)
        Tooltip(self._clr_hist_btn, "Clear all history")

        self._hist_box = tk.Listbox(
            self._hist_frame,
            font=("Arial", 12), height=4,
            bg=T["hist_bg"], fg=T["hist_fg"],
            selectbackground=T["hist_sel"],
            relief="flat", bd=0,
            activestyle="none",
            cursor="hand2"
        )
        self._hist_box.pack(fill="x", padx=0, pady=(2, 0))
        self._hist_box.bind("<<ListboxSelect>>", self._recall_history)
        Tooltip(self._hist_box, "Click any entry to restore it")

        # ── keyboard bindings ─────────────────────────────────────────────────
        self.bind("<Key>",       self._on_key)
        self.bind("<Return>",    lambda e: self._press("="))
        self.bind("<BackSpace>", lambda e: self._backspace())
        self.bind("<Escape>",    lambda e: self._press("AC"))
        self.bind("<Tab>",       lambda e: self._toggle_sci())

    # ══════════════════════════════════════════════════════════════════════════
    #  THEME
    # ══════════════════════════════════════════════════════════════════════════
    def _toggle_theme(self):
        self._theme_nm = "light" if self._theme_nm == "dark" else "dark"
        self._T = THEMES[self._theme_nm]
        self._apply_theme()

    def _apply_theme(self):
        T = self._T
        is_dark = self._theme_nm == "dark"

        self.configure(bg=T["bg"])
        self._theme_btn.configure(
            bg=T["btn_clr"], fg=T["txt_gry"],
            text="☀  Light" if is_dark else "🌙  Dark"
        )
        self._sci_btn.configure(bg=T["btn_clr"], fg=T["txt_gry"])
        self._top.configure(bg=T["bg"])
        self._disp_frame.configure(bg=T["disp_bg"])
        self._hist_lbl.configure(bg=T["disp_bg"], fg=T["txt_gry"])
        self._main_lbl.configure(bg=T["disp_bg"], fg=T["txt_wht"])
        self._copy_lbl.configure(bg=T["disp_bg"], fg=T["copy_fg"])
        self._sci_frame.configure(bg=T["bg"])
        self._grid_frame.configure(bg=T["bg"])
        self._hist_frame.configure(bg=T["bg"])
        self._hist_box.configure(
            bg=T["hist_bg"], fg=T["hist_fg"],
            selectbackground=T["hist_sel"]
        )
        self._clr_hist_btn.configure(bg=T["bg"], fg=T["txt_gry"])
        for w in self._hist_frame.winfo_children():
            if isinstance(w, tk.Frame):
                w.configure(bg=T["bg"])
                for c in w.winfo_children():
                    if isinstance(c, tk.Label):
                        c.configure(bg=T["bg"], fg=T["txt_gry"])

        for btn, bg_k, hv_k, fg_k in self._main_btns:
            btn.configure(bg=T[bg_k], fg=T[fg_k],
                          activebackground=T[hv_k], activeforeground=T[fg_k])

        for btn in self._sci_btns:
            btn.configure(bg=T["btn_sci"], fg=T["txt_sci"],
                          activebackground=T["hv_sci"], activeforeground=T["txt_sci"])

    # ══════════════════════════════════════════════════════════════════════════
    #  SCIENTIFIC TOGGLE
    # ══════════════════════════════════════════════════════════════════════════
    def _toggle_sci(self, event=None):
        self._sci_mode = not self._sci_mode
        if self._sci_mode:
            self._sci_frame.pack(fill="x", padx=14, pady=(4, 0),
                                 before=self._grid_frame)
            self._sci_btn.configure(text="𝑓(𝑥)  Basic")
            self.geometry("500x760")
        else:
            self._sci_frame.pack_forget()
            self._sci_btn.configure(text="𝑓(𝑥)  Scientific")
            self.geometry("500x680")

    def _sci_press(self, cmd):
        if cmd == "pi":
            self._expr += str(math.pi)
        elif cmd == "eu":
            self._expr += str(math.e)
        elif cmd == "pow":
            self._expr += "**"
        elif cmd in ("(", ")"):
            self._expr += cmd
        else:
            self._expr = cmd.format(self._expr) if self._expr else cmd.format("0")
        self._just_eq = False
        self._refresh()

    # ══════════════════════════════════════════════════════════════════════════
    #  CLIPBOARD
    # ══════════════════════════════════════════════════════════════════════════
    def _copy_result(self, event=None):
        val = self._main_var.get()
        if val and val != "Error":
            try:
                pyperclip.copy(val)
            except Exception:
                self.clipboard_clear()
                self.clipboard_append(val)
            self._copy_lbl.configure(text="✓ Copied!")
            if self._copy_after:
                self.after_cancel(self._copy_after)
            self._copy_after = self.after(1800, lambda: self._copy_lbl.configure(text=""))

    # ══════════════════════════════════════════════════════════════════════════
    #  HISTORY
    # ══════════════════════════════════════════════════════════════════════════
    def _add_history(self, entry):
        self._history.insert(0, entry)
        self._history = self._history[:50]
        self._hist_box.delete(0, tk.END)
        for h in self._history:
            self._hist_box.insert(tk.END, "  " + h)

    def _recall_history(self, event=None):
        sel = self._hist_box.curselection()
        if not sel: return
        entry = self._history[sel[0]]
        result = entry.split(" = ")[-1].strip()
        self._expr    = result
        self._prev    = ""
        self._just_eq = False
        self._refresh()

    def _clear_history(self):
        self._history.clear()
        self._hist_box.delete(0, tk.END)

    # ══════════════════════════════════════════════════════════════════════════
    #  INPUT
    # ══════════════════════════════════════════════════════════════════════════
    def _on_key(self, event):
        k = event.char
        if k in "0123456789.()": self._press(k)
        elif k == "+": self._press("+")
        elif k == "-": self._press("-")
        elif k == "*": self._press("*")
        elif k == "/": self._press("/")
        elif k == "%": self._press("%")
        elif k == "^": self._press("**")

    def _backspace(self):
        if self._just_eq: return
        self._expr = self._expr[:-1]
        self._refresh()

    def _press(self, key):
        ops = {"+", "-", "*", "/", "**"}

        if key == "AC":
            self._expr = self._prev = ""
            self._just_eq = False

        elif key == "=":
            if not self._expr: return
            display_expr = self._expr
            self._prev = self._expr + "  ="
            try:
                safe = (self._expr
                        .replace("sin(", "math.sin(math.radians(")
                        .replace("cos(", "math.cos(math.radians(")
                        .replace("tan(", "math.tan(math.radians(")
                        .replace("sqrt(", "math.sqrt(")
                        .replace("sq(", "(")
                        .replace("log(", "math.log10(")
                        .replace("ln(", "math.log(")
                        )
                # close any unclosed sin/cos/tan radians wrappers
                safe = re.sub(r'math\.(sin|cos|tan)\(math\.radians\(([^)]+)\)',
                              r'math.\1(math.radians(\2))', safe)
                result = eval(safe, {"__builtins__": {}}, {"math": math})
                if isinstance(result, float) and result.is_integer():
                    result = int(result)
                result = round(result, 10) if isinstance(result, float) else result
                self._expr = str(result)
                self._add_history(f"{display_expr} = {result}")
            except Exception:
                self._expr = "Error"
            self._just_eq = True

        elif key == "+/-":
            if self._expr and self._expr != "Error":
                try:
                    v = float(self._expr)
                    v = -v
                    self._expr = str(int(v) if float(v).is_integer() else v)
                    self._just_eq = False
                except Exception:
                    pass

        elif key == "%":
            if self._expr and self._expr != "Error":
                try:
                    v = float(self._expr)
                    r = v / 100
                    self._expr = str(int(r) if float(r).is_integer() else r)
                    self._just_eq = False
                except Exception:
                    pass

        else:
            if self._just_eq:
                if key in ops:
                    self._just_eq = False
                else:
                    self._expr = self._prev = ""
                    self._just_eq = False

            if self._expr and self._expr[-1] in "+-*/" and key in ops:
                self._expr = self._expr[:-1]

            if not self._expr and key in ("+", "*", "/"):
                return

            if key == ".":
                parts = re.split(r"[+\-*/]", self._expr)
                if parts and "." in parts[-1]:
                    return

            self._expr += key

        self._refresh()

    # ══════════════════════════════════════════════════════════════════════════
    #  DISPLAY
    # ══════════════════════════════════════════════════════════════════════════
    def _refresh(self):
        text = self._expr or "0"
        n = len(text)
        size = 56 if n <= 6 else 44 if n <= 10 else 30 if n <= 16 else 20
        self._main_var.set(text)
        self._main_lbl.configure(font=("Arial", size, "bold"))
        self._hist_var.set(self._prev)


# ══════════════════════════════════════════════════════════════════════════════
#  ENTRY
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    app = Calculator()
    app.geometry("500x680")
    app.mainloop()