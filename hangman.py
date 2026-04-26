import tkinter as tk
import random

# ══════════════════════════════════════════════════════════════════════════════
#  WORD BANK
# ══════════════════════════════════════════════════════════════════════════════
WORDS = {
    "🐾 Animals": [
        "elephant","dolphin","cheetah","penguin","crocodile","butterfly",
        "gorilla","flamingo","kangaroo","hedgehog","porcupine","chameleon",
        "albatross","wolverine","narwhal","platypus","axolotl","capybara",
        "pangolin","quokka"
    ],
    "🌍 Countries": [
        "pakistan","australia","brazil","canada","germany","japan",
        "france","mexico","nigeria","argentina","portugal","indonesia",
        "philippines","netherlands","switzerland","bangladesh","zimbabwe",
        "kazakhstan","madagascar","mozambique"
    ],
    "🎮 Video Games": [
        "minecraft","fortnite","pokemon","zelda","roblox","overwatch",
        "cyberpunk","terraria","stardew","undertale","cuphead","celeste",
        "hollowknight","hades","valorant","warcraft","skyrim","bioshock",
        "dishonored","supermario"
    ],
    "🍕 Food": [
        "spaghetti","croissant","sushi","avocado","quesadilla","bruschetta",
        "baklava","pierogi","tiramisu","rendang","bibimbap","shakshuka",
        "enchilada","paella","ceviche","hummus","falafel","moussaka",
        "stroganoff","carbonara"
    ],
    "💻 Tech": [
        "algorithm","javascript","database","framework","encryption",
        "blockchain","tensorflow","cybersecurity","bandwidth","repository",
        "debugging","recursion","polymorphism","authentication","microservice",
        "cryptocurrency","machinelearning","opensource","kubernetes","python"
    ],
    "🎬 Movies": [
        "inception","interstellar","avengers","titanic","gladiator",
        "parasite","joker","shawshank","godfather","casablanca",
        "jurassic","terminator","matrix","braveheart","goodfellas",
        "scarface","beetlejuice","labyrinth","metropolis","alien"
    ],
}

# ── Colours ────────────────────────────────────────────────────────────────────
BG   = "#0d0d0d"
PAN  = "#111111"
ACC  = "#ff6b35"
WHT  = "#f5f5f7"
GRY  = "#8e8e93"
GRN  = "#30d158"
RED  = "#ff453a"
YEL  = "#ffd60a"
BLU  = "#0a84ff"
DRK  = "#1c1c1e"
HV   = "#2c2c2e"

MAX_WRONG = 6


# ══════════════════════════════════════════════════════════════════════════════
#  HANGMAN CANVAS DRAWING
# ══════════════════════════════════════════════════════════════════════════════
def draw_hangman(canvas, wrong, won=False, lost=False):
    canvas.delete("all")
    CW, CH = 260, 260
    gc = "#444444"

    # gallows
    canvas.create_line(20, CH-10, CW-20, CH-10, fill=gc, width=3)
    canvas.create_line(70, CH-10, 70, 20,        fill=gc, width=3)
    canvas.create_line(70, 20,   180, 20,        fill=gc, width=3)
    canvas.create_line(180, 20,  180, 55,        fill=gc, width=3)

    col = GRN if won else (RED if lost else WHT)

    if wrong >= 1 or won:
        canvas.create_oval(163, 55, 197, 90, outline=col, width=2)
        if won:
            canvas.create_arc(170, 68, 192, 85, start=0, extent=-180,
                              style="arc", outline=col, width=2)
            canvas.create_oval(169,62,174,67, fill=col, outline="")
            canvas.create_oval(186,62,191,67, fill=col, outline="")
        elif lost:
            for x1,y1,x2,y2 in [(170,64,175,69),(175,64,170,69),
                                  (185,64,190,69),(190,64,185,69)]:
                canvas.create_line(x1,y1,x2,y2, fill=col, width=2)
            canvas.create_arc(170,75,192,87, start=0, extent=180,
                              style="arc", outline=col, width=2)

    if wrong >= 2 or won:
        canvas.create_line(180, 90, 180, 160, fill=col, width=2)
    if wrong >= 3 or won:
        canvas.create_line(180, 105, 150, 135, fill=col, width=2)
    if wrong >= 4 or won:
        canvas.create_line(180, 105, 210, 135, fill=col, width=2)
    if wrong >= 5 or won:
        canvas.create_line(180, 160, 150, 200, fill=col, width=2)
    if wrong >= 6 or won:
        canvas.create_line(180, 160, 210, 200, fill=col, width=2)


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN APP
# ══════════════════════════════════════════════════════════════════════════════
class HangmanGame(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Hangman")
        self.geometry("700x680")
        self.resizable(False, False)
        self.configure(bg=BG)

        self._word    = ""
        self._cat     = ""
        self._guessed = set()
        self._wrong   = 0
        self._score   = 0
        self._streak  = 0
        self._wins    = 0
        self._losses  = 0
        self._state   = "menu"

        self._build_ui()
        self._show_menu()

    # ── build all widgets once ─────────────────────────────────────────────────
    def _build_ui(self):
        # top bar
        top = tk.Frame(self, bg=BG)
        top.pack(fill="x", padx=20, pady=(14,0))
        tk.Label(top, text="💀 HANGMAN", font=("Arial",22,"bold"),
                 bg=BG, fg=WHT).pack(side="left")
        self._stats_lbl = tk.Label(top, text="", font=("Arial",12),
                                   bg=BG, fg=GRY)
        self._stats_lbl.pack(side="right")

        # ── MENU ──────────────────────────────────────────────────────────────
        self._menu_frame = tk.Frame(self, bg=BG)

        tk.Label(self._menu_frame, text="Choose a Category",
                 font=("Arial",18,"bold"), bg=BG, fg=WHT).pack(pady=(30,16))

        self._cat_var = tk.StringVar(value=list(WORDS.keys())[0])
        for cat in WORDS:
            tk.Radiobutton(
                self._menu_frame, text=cat,
                variable=self._cat_var, value=cat,
                font=("Arial",14), bg=BG, fg=WHT,
                selectcolor=DRK, activebackground=BG,
                activeforeground=ACC, cursor="hand2"
            ).pack(anchor="w", padx=100, pady=3)

        tk.Button(self._menu_frame, text="▶  Start Game",
                  font=("Arial",16,"bold"), bg=ACC, fg="white",
                  activebackground="#ff8c5a", activeforeground="white",
                  relief="flat", bd=0, cursor="hand2", pady=12,
                  command=self._start_game
                  ).pack(fill="x", padx=80, pady=(24,6))

        tk.Button(self._menu_frame, text="🎲  Random Category",
                  font=("Arial",13), bg=DRK, fg=WHT,
                  activebackground=HV, activeforeground=ACC,
                  relief="flat", bd=0, cursor="hand2", pady=10,
                  command=self._random_cat
                  ).pack(fill="x", padx=80)

        # ── GAME ──────────────────────────────────────────────────────────────
        self._game_frame = tk.Frame(self, bg=BG)

        self._cat_lbl = tk.Label(self._game_frame, text="",
                                 font=("Arial",13), bg=BG, fg=BLU)
        self._cat_lbl.pack(pady=(10,0))

        mid = tk.Frame(self._game_frame, bg=BG)
        mid.pack()

        self._canvas = tk.Canvas(mid, width=260, height=260,
                                 bg=PAN, highlightthickness=0)
        self._canvas.pack(side="left", padx=(20,10))

        right = tk.Frame(mid, bg=BG)
        right.pack(side="left", padx=(10,20), anchor="n", pady=10)

        tk.Label(right, text="Wrong guesses", font=("Arial",12),
                 bg=BG, fg=GRY).pack(anchor="w")
        self._wrong_lbl = tk.Label(right, text="0 / 6",
                                   font=("Arial",28,"bold"), bg=BG, fg=WHT)
        self._wrong_lbl.pack(anchor="w")

        tk.Label(right, text="Letters used", font=("Arial",12),
                 bg=BG, fg=GRY).pack(anchor="w", pady=(14,0))
        self._used_lbl = tk.Label(right, text="—", font=("Arial",13),
                                  bg=BG, fg=GRY, wraplength=160, justify="left")
        self._used_lbl.pack(anchor="w")

        tk.Label(right, text="Hint", font=("Arial",12),
                 bg=BG, fg=GRY).pack(anchor="w", pady=(14,0))
        self._hint_lbl = tk.Label(right, text="", font=("Arial",12),
                                  bg=BG, fg=YEL, wraplength=160, justify="left")
        self._hint_lbl.pack(anchor="w")

        # word display  ← NO letterSpacing here
        self._word_lbl = tk.Label(self._game_frame, text="",
                                  font=("Arial",32,"bold"),
                                  bg=BG, fg=WHT)
        self._word_lbl.pack(pady=(14,6))

        self._msg_lbl = tk.Label(self._game_frame, text="",
                                 font=("Arial",15,"bold"), bg=BG, fg=WHT)
        self._msg_lbl.pack()

        # keyboard
        kb = tk.Frame(self._game_frame, bg=BG)
        kb.pack(pady=(10,6))
        self._btns = {}
        for row in ["QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM"]:
            rf = tk.Frame(kb, bg=BG)
            rf.pack()
            for ch in row:
                b = tk.Button(rf, text=ch, width=3,
                              font=("Arial",13,"bold"),
                              bg=DRK, fg=WHT,
                              activebackground=HV, activeforeground=WHT,
                              relief="flat", bd=0, cursor="hand2",
                              command=lambda c=ch: self._guess(c))
                b.pack(side="left", padx=2, pady=2, ipady=6)
                self._btns[ch] = b

        # action buttons
        act = tk.Frame(self._game_frame, bg=BG)
        act.pack(pady=(6,0))

        tk.Button(act, text="💡 Hint  (-20pts)",
                  font=("Arial",12), bg=DRK, fg=YEL,
                  activebackground=HV, activeforeground=YEL,
                  relief="flat", bd=0, cursor="hand2", padx=14, pady=8,
                  command=self._give_hint).pack(side="left", padx=6)

        tk.Button(act, text="🔄 New Word",
                  font=("Arial",12), bg=DRK, fg=GRY,
                  activebackground=HV, activeforeground=WHT,
                  relief="flat", bd=0, cursor="hand2", padx=14, pady=8,
                  command=self._start_game).pack(side="left", padx=6)

        tk.Button(act, text="📋 Menu",
                  font=("Arial",12), bg=DRK, fg=GRY,
                  activebackground=HV, activeforeground=WHT,
                  relief="flat", bd=0, cursor="hand2", padx=14, pady=8,
                  command=self._show_menu).pack(side="left", padx=6)

        self.bind("<Key>", self._on_key)

    # ── screen switching ───────────────────────────────────────────────────────
    def _show_menu(self):
        self._game_frame.pack_forget()
        self._menu_frame.pack(fill="both", expand=True)
        self._state = "menu"
        self._update_stats()

    def _show_game(self):
        self._menu_frame.pack_forget()
        self._game_frame.pack(fill="both", expand=True)

    # ── game logic ─────────────────────────────────────────────────────────────
    def _random_cat(self):
        self._cat_var.set(random.choice(list(WORDS.keys())))

    def _start_game(self):
        self._cat     = self._cat_var.get()
        self._word    = random.choice(WORDS[self._cat]).upper()
        self._guessed = set()
        self._wrong   = 0
        self._state   = "playing"
        self._hint_lbl.configure(text="")
        for b in self._btns.values():
            b.configure(bg=DRK, fg=WHT, state="normal")
        self._show_game()
        self._refresh()

    def _guess(self, letter):
        if self._state != "playing" or letter in self._guessed:
            return
        self._guessed.add(letter)
        if letter in self._word:
            if all(c in self._guessed for c in self._word):
                self._state  = "won"
                pts = max(10, 100 - self._wrong * 10)
                self._score += pts
                self._streak += 1
                self._wins  += 1
        else:
            self._wrong += 1
            if self._wrong >= MAX_WRONG:
                self._state  = "lost"
                self._streak = 0
                self._losses += 1
        self._refresh()

    def _give_hint(self):
        if self._state != "playing": return
        hidden = [c for c in self._word if c not in self._guessed and c.isalpha()]
        if not hidden: return
        self._score = max(0, self._score - 20)
        self._hint_lbl.configure(text=f'Try the letter  "{random.choice(hidden)}"')

    def _on_key(self, event):
        ch = event.char.upper()
        if ch.isalpha() and len(ch) == 1:
            self._guess(ch)

    # ── refresh display ────────────────────────────────────────────────────────
    def _refresh(self):
        won  = self._state == "won"
        lost = self._state == "lost"

        draw_hangman(self._canvas, self._wrong, won=won, lost=lost)

        # word
        display = " ".join(
            ch if (ch in self._guessed or lost) else "_"
            for ch in self._word
        )
        self._word_lbl.configure(
            text=display,
            fg=GRN if won else (RED if lost else WHT)
        )

        # wrong counter colour
        wc = GRN if self._wrong == 0 else (YEL if self._wrong <= 3 else RED)
        self._wrong_lbl.configure(text=f"{self._wrong} / {MAX_WRONG}", fg=wc)

        # used letters
        wrong_l = sorted(l for l in self._guessed if l not in self._word)
        right_l = sorted(l for l in self._guessed if l in self._word)
        used = ""
        if wrong_l: used += "✗ " + " ".join(wrong_l)
        if right_l: used += ("\n" if used else "") + "✓ " + " ".join(right_l)
        self._used_lbl.configure(text=used or "—")

        self._cat_lbl.configure(text=f"Category: {self._cat}")

        # keyboard
        for ch, btn in self._btns.items():
            if ch in self._guessed:
                btn.configure(bg="#1a3a1a" if ch in self._word else "#3a1a1a",
                              fg=GRN if ch in self._word else RED,
                              state="disabled")
            else:
                btn.configure(bg=DRK, fg=WHT,
                              state="disabled" if (won or lost) else "normal")

        # message
        if won:
            pts = max(10, 100 - self._wrong * 10)
            self._msg_lbl.configure(
                text=f"🎉 You got it!  +{pts} pts   Streak: {self._streak} 🔥",
                fg=GRN)
        elif lost:
            self._msg_lbl.configure(
                text=f"💀 Game over!  The word was: {self._word}", fg=RED)
        else:
            left = MAX_WRONG - self._wrong
            self._msg_lbl.configure(
                text=f"{left} guess{'es' if left!=1 else ''} remaining",
                fg=YEL if left <= 2 else GRY)

        self._update_stats()

    def _update_stats(self):
        self._stats_lbl.configure(
            text=f"Score: {self._score}   W: {self._wins}   L: {self._losses}   🔥 {self._streak}"
        )


if __name__ == "__main__":
    app = HangmanGame()
    app.mainloop()