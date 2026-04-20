import os
import random
import sys
import threading
import time

# ── Windows ANSI support ────────────────────────────────────────────────────
os.system('')                     # enables ANSI in Windows 10+ console
try:
    import colorama
    colorama.init()
except ImportError:
    pass

from termcolor import cprint

# ── Sound ───────────────────────────────────────────────────────────────────
try:
    import numpy as np
    import pygame
    SOUND_AVAILABLE = True
except ImportError:
    SOUND_AVAILABLE = False


class SoundManager:
    """Generates and plays all game sounds using pygame + numpy (no audio files needed)."""

    def __init__(self):
        self.enabled = False
        if not SOUND_AVAILABLE:
            return
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            self._sounds = self._build_all()
            self.enabled = True
        except Exception as e:
            cprint(f'  (Sound unavailable: {e})', 'yellow')

    # ── internal helpers ────────────────────────────────────────────────────

    def _tone(self, freq, duration, volume=0.5, fade=True):
        sr  = 44100
        t   = np.linspace(0, duration, int(sr * duration), False)
        wav = np.sin(2 * np.pi * freq * t)
        if fade:
            wav *= np.linspace(1.0, 0.0, len(wav))
        wav = (wav * volume * 32767).astype(np.int16)
        return pygame.sndarray.make_sound(np.ascontiguousarray(np.column_stack([wav, wav])))

    def _melody(self, notes, beat=0.13, volume=0.55):
        """notes: list of (freq, beats) tuples."""
        sr      = 44100
        chunks  = []
        for freq, beats in notes:
            dur = beat * beats
            t   = np.linspace(0, dur, int(sr * dur), False)
            wav = np.sin(2 * np.pi * freq * t)
            wav *= np.linspace(1.0, 0.0, len(wav))   # fade each note
            chunks.append(wav)
        full = np.concatenate(chunks)
        full = (full * volume * 32767).astype(np.int16)
        return pygame.sndarray.make_sound(np.ascontiguousarray(np.column_stack([full, full])))

    def _build_all(self):
        return {
            # countdown ticks
            'tick':          self._tone(750,  0.07, 0.25),
            'tick_warn':     self._tone(1050, 0.07, 0.45),   # last 5 s — higher pitch

            # answer feedback
            'correct': self._melody([(523, 1), (659, 1), (784, 1.5)], beat=0.11, volume=0.6),
            'wrong':   self._melody([(350, 1), (220, 2)],              beat=0.14, volume=0.6),

            # timeout alarm
            'timeout': self._melody([(440, 1), (330, 1), (220, 2)],   beat=0.13, volume=0.7),

            # navigation / milestones
            'intro':   self._melody(
                [(262, 1), (330, 1), (392, 1), (523, 1), (659, 1), (784, 2)],
                beat=0.10, volume=0.55
            ),
            'round_end': self._melody(
                [(523, 1), (659, 1), (784, 1), (1047, 2)],
                beat=0.13, volume=0.6
            ),
            'game_over': self._melody(
                [(392, 1), (523, 1), (659, 1), (784, 1), (1047, 1), (1319, 3)],
                beat=0.12, volume=0.65
            ),
        }

    # ── public API ──────────────────────────────────────────────────────────

    def play(self, name):
        """Fire-and-forget."""
        if self.enabled and name in self._sounds:
            self._sounds[name].play()

    def play_wait(self, name):
        """Play and block until the sound finishes."""
        if self.enabled and name in self._sounds:
            s = self._sounds[name]
            s.play()
            pygame.time.wait(int(s.get_length() * 1000) + 60)


# ── Quiz data ────────────────────────────────────────────────────────────────
QUESTION = 'question'
OPTIONS  = 'options'
ANSWER   = 'answer'

QUIZ_DATA = {
    'easy': [
        {QUESTION: 'What is the capital of France?',
         OPTIONS: ['A. Berlin', 'B. Madrid', 'C. Paris', 'D. Rome'], ANSWER: 'C'},
        {QUESTION: 'Which planet is known as the Red Planet?',
         OPTIONS: ['A. Earth', 'B. Mars', 'C. Jupiter', 'D. Saturn'], ANSWER: 'B'},
        {QUESTION: 'What is the largest ocean on Earth?',
         OPTIONS: ['A. Atlantic', 'B. Indian', 'C. Arctic', 'D. Pacific'], ANSWER: 'D'},
        {QUESTION: 'What is the only food that never goes bad?',
         OPTIONS: ['A. Orange', 'B. Chicken', 'C. Honey', 'D. Yogurt'], ANSWER: 'C'},
        {QUESTION: 'How many sides does a triangle have?',
         OPTIONS: ['A. 2', 'B. 3', 'C. 4', 'D. 5'], ANSWER: 'B'},
        {QUESTION: 'What colour is the sky on a clear day?',
         OPTIONS: ['A. Green', 'B. Red', 'C. Blue', 'D. Yellow'], ANSWER: 'C'},
        {QUESTION: 'How many days are in a week?',
         OPTIONS: ['A. 5', 'B. 6', 'C. 8', 'D. 7'], ANSWER: 'D'},
        {QUESTION: "What animal is known as man's best friend?",
         OPTIONS: ['A. Cat', 'B. Dog', 'C. Rabbit', 'D. Horse'], ANSWER: 'B'},
        {QUESTION: 'What do bees produce?',
         OPTIONS: ['A. Milk', 'B. Silk', 'C. Honey', 'D. Wax only'], ANSWER: 'C'},
        {QUESTION: 'Which season comes after summer?',
         OPTIONS: ['A. Spring', 'B. Winter', 'C. Autumn', 'D. Monsoon'], ANSWER: 'C'},
        {QUESTION: 'How many months are in a year?',
         OPTIONS: ['A. 10', 'B. 11', 'C. 12', 'D. 13'], ANSWER: 'C'},
        {QUESTION: 'What colour do you get when mixing red and white?',
         OPTIONS: ['A. Orange', 'B. Purple', 'C. Pink', 'D. Maroon'], ANSWER: 'C'},
        {QUESTION: 'Which continent is Egypt in?',
         OPTIONS: ['A. Asia', 'B. Europe', 'C. South America', 'D. Africa'], ANSWER: 'D'},
        {QUESTION: 'What is 8 x 7?',
         OPTIONS: ['A. 54', 'B. 56', 'C. 58', 'D. 64'], ANSWER: 'B'},
        {QUESTION: 'How many legs does a spider have?',
         OPTIONS: ['A. 6', 'B. 10', 'C. 8', 'D. 12'], ANSWER: 'C'},
        {QUESTION: 'What language do people speak in Brazil?',
         OPTIONS: ['A. Spanish', 'B. French', 'C. English', 'D. Portuguese'], ANSWER: 'D'},
        {QUESTION: 'Which fruit is known as the king of fruits?',
         OPTIONS: ['A. Mango', 'B. Apple', 'C. Banana', 'D. Pineapple'], ANSWER: 'A'},
        {QUESTION: 'What is the opposite of hot?',
         OPTIONS: ['A. Warm', 'B. Cool', 'C. Cold', 'D. Freezing'], ANSWER: 'C'},
        {QUESTION: 'Which animal is the tallest in the world?',
         OPTIONS: ['A. Elephant', 'B. Giraffe', 'C. Horse', 'D. Camel'], ANSWER: 'B'},
        {QUESTION: 'How many hours are in a day?',
         OPTIONS: ['A. 12', 'B. 20', 'C. 24', 'D. 48'], ANSWER: 'C'},
    ],
    'medium': [
        {QUESTION: 'What is the chemical symbol for gold?',
         OPTIONS: ['A. Go', 'B. Gd', 'C. Au', 'D. Ag'], ANSWER: 'C'},
        {QUESTION: 'How many bones are in the adult human body?',
         OPTIONS: ['A. 196', 'B. 206', 'C. 216', 'D. 226'], ANSWER: 'B'},
        {QUESTION: 'Which country invented pizza?',
         OPTIONS: ['A. Greece', 'B. Spain', 'C. France', 'D. Italy'], ANSWER: 'D'},
        {QUESTION: 'What is the approximate speed of light in km/s?',
         OPTIONS: ['A. 100,000', 'B. 200,000', 'C. 300,000', 'D. 400,000'], ANSWER: 'C'},
        {QUESTION: 'Which element has the atomic number 1?',
         OPTIONS: ['A. Helium', 'B. Oxygen', 'C. Carbon', 'D. Hydrogen'], ANSWER: 'D'},
        {QUESTION: 'In what year did World War II end?',
         OPTIONS: ['A. 1943', 'B. 1944', 'C. 1945', 'D. 1946'], ANSWER: 'C'},
        {QUESTION: 'What is the largest continent by area?',
         OPTIONS: ['A. Africa', 'B. Asia', 'C. Europe', 'D. Americas'], ANSWER: 'B'},
        {QUESTION: 'Which gas do plants absorb from the atmosphere?',
         OPTIONS: ['A. Oxygen', 'B. Nitrogen', 'C. Carbon Dioxide', 'D. Hydrogen'], ANSWER: 'C'},
        {QUESTION: 'How many strings does a standard guitar have?',
         OPTIONS: ['A. 4', 'B. 5', 'C. 6', 'D. 7'], ANSWER: 'C'},
        {QUESTION: 'What is the largest organ in the human body?',
         OPTIONS: ['A. Heart', 'B. Liver', 'C. Lung', 'D. Skin'], ANSWER: 'D'},
        {QUESTION: 'What is the currency of Japan?',
         OPTIONS: ['A. Yuan', 'B. Won', 'C. Yen', 'D. Baht'], ANSWER: 'C'},
        {QUESTION: 'Which planet has the most moons?',
         OPTIONS: ['A. Jupiter', 'B. Saturn', 'C. Uranus', 'D. Neptune'], ANSWER: 'B'},
        {QUESTION: 'What is the hardest natural substance on Earth?',
         OPTIONS: ['A. Gold', 'B. Iron', 'C. Diamond', 'D. Quartz'], ANSWER: 'C'},
        {QUESTION: 'Who painted the Mona Lisa?',
         OPTIONS: ['A. Michelangelo', 'B. Raphael', 'C. Da Vinci', 'D. Picasso'], ANSWER: 'C'},
        {QUESTION: 'What is the capital of Australia?',
         OPTIONS: ['A. Sydney', 'B. Melbourne', 'C. Brisbane', 'D. Canberra'], ANSWER: 'D'},
        {QUESTION: 'How many players are on a standard football (soccer) team?',
         OPTIONS: ['A. 9', 'B. 10', 'C. 11', 'D. 12'], ANSWER: 'C'},
        {QUESTION: 'Which organ pumps blood around the body?',
         OPTIONS: ['A. Lungs', 'B. Liver', 'C. Kidney', 'D. Heart'], ANSWER: 'D'},
        {QUESTION: 'What does HTTP stand for?',
         OPTIONS: ['A. HyperText Transfer Protocol', 'B. HyperText Transmission Process',
                   'C. High Transfer Text Protocol', 'D. Hyper Transfer Text Procedure'], ANSWER: 'A'},
        {QUESTION: 'Which country has the largest population?',
         OPTIONS: ['A. USA', 'B. India', 'C. China', 'D. Russia'], ANSWER: 'B'},
        {QUESTION: 'What is the boiling point of water in Celsius?',
         OPTIONS: ['A. 90', 'B. 95', 'C. 100', 'D. 110'], ANSWER: 'C'},
    ],
    'hard': [
        {QUESTION: 'What is the Heisenberg Uncertainty Principle about?',
         OPTIONS: ['A. Speed of light', 'B. Position & momentum of a particle',
                   'C. Energy conservation', 'D. Wave-particle duality'], ANSWER: 'B'},
        {QUESTION: 'Which mathematician first described non-Euclidean geometry?',
         OPTIONS: ['A. Gauss', 'B. Euler', 'C. Newton', 'D. Leibniz'], ANSWER: 'A'},
        {QUESTION: 'What is the half-life of Carbon-14?',
         OPTIONS: ['A. 1,730 years', 'B. 5,730 years', 'C. 10,730 years', 'D. 15,730 years'], ANSWER: 'B'},
        {QUESTION: 'Which programming paradigm does Haskell primarily follow?',
         OPTIONS: ['A. Object-Oriented', 'B. Procedural', 'C. Functional', 'D. Logic'], ANSWER: 'C'},
        {QUESTION: 'What does DNA stand for?',
         OPTIONS: ['A. Deoxyribonucleic Acid', 'B. Dioxyribonucleic Acid',
                   'C. Deoxyribonuclear Acid', 'D. Diribonucleic Acid'], ANSWER: 'A'},
        {QUESTION: 'In which year was the Turing Test proposed?',
         OPTIONS: ['A. 1945', 'B. 1948', 'C. 1950', 'D. 1956'], ANSWER: 'C'},
        {QUESTION: 'What is the time complexity of binary search?',
         OPTIONS: ['A. O(n)', 'B. O(n squared)', 'C. O(log n)', 'D. O(n log n)'], ANSWER: 'C'},
        {QUESTION: 'Which country was the first to use paper money?',
         OPTIONS: ['A. India', 'B. Egypt', 'C. China', 'D. Rome'], ANSWER: 'C'},
        {QUESTION: 'What is the powerhouse of the cell?',
         OPTIONS: ['A. Nucleus', 'B. Ribosome', 'C. Mitochondria', 'D. Golgi Apparatus'], ANSWER: 'C'},
        {QUESTION: 'Which philosopher wrote "Critique of Pure Reason"?',
         OPTIONS: ['A. Hegel', 'B. Kant', 'C. Nietzsche', 'D. Descartes'], ANSWER: 'B'},
        {QUESTION: 'What is the Pythagorean theorem?',
         OPTIONS: ['A. a2 - b2 = c2', 'B. a + b = c', 'C. a2 + b2 = c2', 'D. a3 + b3 = c3'], ANSWER: 'C'},
        {QUESTION: 'Which particle has no electric charge?',
         OPTIONS: ['A. Proton', 'B. Electron', 'C. Neutron', 'D. Positron'], ANSWER: 'C'},
        {QUESTION: 'In Big-O notation, what is the worst-case of bubble sort?',
         OPTIONS: ['A. O(n)', 'B. O(n log n)', 'C. O(n squared)', 'D. O(2 to the n)'], ANSWER: 'C'},
        {QUESTION: 'What does the acronym RAM stand for?',
         OPTIONS: ['A. Random Access Memory', 'B. Rapid Access Module',
                   'C. Read Access Memory', 'D. Random Allocated Memory'], ANSWER: 'A'},
        {QUESTION: 'Which acid is found in the human stomach?',
         OPTIONS: ['A. Sulphuric acid', 'B. Nitric acid', 'C. Acetic acid', 'D. Hydrochloric acid'], ANSWER: 'D'},
        {QUESTION: 'What is the rarest blood type?',
         OPTIONS: ['A. O-', 'B. AB-', 'C. B-', 'D. A-'], ANSWER: 'B'},
        {QUESTION: 'Which treaty ended World War I?',
         OPTIONS: ['A. Treaty of Paris', 'B. Treaty of Vienna',
                   'C. Treaty of Versailles', 'D. Treaty of Berlin'], ANSWER: 'C'},
        {QUESTION: 'What is the process by which plants make food?',
         OPTIONS: ['A. Respiration', 'B. Photosynthesis', 'C. Transpiration', 'D. Osmosis'], ANSWER: 'B'},
        {QUESTION: 'How many zeros are in one billion?',
         OPTIONS: ['A. 7', 'B. 8', 'C. 9', 'D. 10'], ANSWER: 'C'},
        {QUESTION: 'Which data structure operates on a LIFO principle?',
         OPTIONS: ['A. Queue', 'B. Array', 'C. Linked List', 'D. Stack'], ANSWER: 'D'},
    ]
}

TIME_LIMIT = 15
DIFFICULTY_COLORS = {'easy': 'green', 'medium': 'yellow', 'hard': 'red'}
MODES = ['easy', 'medium', 'hard']

# ANSI helpers
_G  = '\033[92m'   # green
_Y  = '\033[93m'   # yellow
_R  = '\033[91m'   # red
_B  = '\033[96m'   # cyan
_W  = '\033[1m'    # bold
_X  = '\033[0m'    # reset
UP1 = '\033[1A'
CLR = '\033[2K'


def _cnum(n):
    """Colour a countdown number by urgency."""
    if n <= 5:  return f'{_R}{n:2d}{_X}'
    if n <= 10: return f'{_Y}{n:2d}{_X}'
    return f'{_G}{n:2d}{_X}'


# ── Question / timer ─────────────────────────────────────────────────────────

def ask_question(index, total, question, options, color, sfx):
    cprint(f'\nQuestion {index}/{total}: {question}', color, attrs=['bold'])
    for opt in options:
        print(f'  {opt}')
    print()

    stop      = threading.Event()
    answer    = ['']
    timed_out = [False]

    # Initial display: [timer line]  then  [input prompt]
    nums_str = '  '.join(str(n) for n in range(TIME_LIMIT - 1, 0, -1))
    sys.stdout.write(f'  \u23f1  {_G}{TIME_LIMIT:2d}{_X}  {nums_str}\n  Your answer: ')
    sys.stdout.flush()

    def countdown():
        remaining_list = list(range(TIME_LIMIT - 1, -1, -1))
        for tick in range(TIME_LIMIT):
            # play tick sound
            if remaining_list[tick] <= 5:
                sfx.play('tick_warn')
            else:
                sfx.play('tick')

            if stop.wait(1.0):
                return                          # answered early — stop ticking

            nums_left = remaining_list[tick + 1:]

            if not nums_left:
                timed_out[0] = True
                sys.stdout.write(
                    f'\n{UP1}{CLR}\r'           # clear input line
                    f'{UP1}{CLR}\r'             # clear timer line
                    f'  {_R}\u231b  Time\'s up!{_X}\n\n'
                )
                sys.stdout.flush()
                sfx.play('timeout')
                stop.set()
                return

            cur  = nums_left[0]
            rest = '  '.join(str(n) for n in nums_left[1:])
            sys.stdout.write(f'{UP1}{CLR}\r  \u23f1  {_cnum(cur)}  {rest}\n')
            sys.stdout.flush()

    def get_input():
        raw = sys.stdin.readline()
        if not timed_out[0]:
            answer[0] = raw.strip().upper()
            stop.set()

    threading.Thread(target=get_input,  daemon=True).start()
    threading.Thread(target=countdown,  daemon=True).start()

    stop.wait()
    time.sleep(0.15)   # tiny gap so sound starts before result text
    return answer[0], timed_out[0]


def grade(answer, timed_out, correct, sfx):
    if timed_out:
        time.sleep(0.35)   # let timeout sound breathe
        cprint(f"  \u2717  Time's up!  The correct answer was {correct}.", 'red')
        return 0
    if answer == correct:
        sfx.play_wait('correct')
        cprint('  \u2713  Correct!', 'green')
        return 1
    sfx.play_wait('wrong')
    cprint(f'  \u2717  Wrong!  The correct answer was {correct}.', 'red')
    return 0


# ── Round / game flow ────────────────────────────────────────────────────────

def run_mode(difficulty, mode_number, sfx):
    questions = QUIZ_DATA[difficulty][:]
    random.shuffle(questions)

    color = DIFFICULTY_COLORS[difficulty]
    score = 0

    cprint(f'\n{"=" * 48}', color)
    cprint(f'  ROUND {mode_number}/3  \u2014  {difficulty.upper()}', color, attrs=['bold'])
    cprint(f'  20 questions  \u2022  {TIME_LIMIT} seconds per question', color)
    cprint(f'{"=" * 48}', color)
    input('  Press ENTER to start...\n')

    for idx, item in enumerate(questions, 1):
        ans, timeout = ask_question(idx, 20, item[QUESTION], item[OPTIONS], color, sfx)
        score += grade(ans, timeout, item[ANSWER], sfx)
        time.sleep(0.4)

    sfx.play_wait('round_end')
    pct = (score / 20) * 100
    print()
    cprint(f'  {difficulty.upper()} round complete!', color, attrs=['bold'])
    cprint(f'  Score: {score}/20  ({pct:.0f}%)', color)

    if mode_number < 3:
        input('\n  Press ENTER for the next round...\n')
    return score


def show_results(scores, sfx):
    total    = sum(scores.values())
    possible = 60

    sfx.play_wait('game_over')
    print()
    cprint('=' * 48, 'cyan')
    cprint('             \U0001f4ca  FINAL RESULTS  \U0001f4ca', 'cyan', attrs=['bold'])
    cprint('=' * 48, 'cyan')

    for mode in MODES:
        color = DIFFICULTY_COLORS[mode]
        s     = scores[mode]
        pct   = (s / 20) * 100
        bar   = '\u2588' * s + '\u2591' * (20 - s)
        cprint(f'  {mode.capitalize():<8} {bar}  {s}/20  ({pct:.0f}%)', color)

    cprint('-' * 48, 'cyan')

    pct  = (total / possible) * 100
    fbar = '\u2588' * total + '\u2591' * (possible - total)
    cprint(f'  TOTAL    {fbar}', 'cyan')
    cprint(f'           {total} / {possible}  ({pct:.0f}%)', 'cyan', attrs=['bold'])
    print()

    if pct == 100:
        cprint('  \U0001f3c6 PERFECT SCORE! Absolutely incredible!', 'yellow', attrs=['bold'])
    elif pct >= 80:
        cprint('  \U0001f525 Excellent! You really know your stuff!', 'green', attrs=['bold'])
    elif pct >= 60:
        cprint('  \U0001f44d Good effort! Keep it up!', 'green')
    elif pct >= 40:
        cprint("  \U0001f4da Not bad \u2014 a bit more studying and you'll nail it!", 'yellow')
    else:
        cprint("  \U0001f4aa Keep practising \u2014 you'll get there!", 'red')

    cprint('=' * 48, 'cyan')


def print_banner(sfx):
    cprint('=' * 48, 'cyan')
    cprint('               \U0001f9e0  QUIZ GAME  \U0001f9e0', 'cyan', attrs=['bold'])
    cprint('=' * 48, 'cyan')
    cprint('  3 rounds  \u2022  20 questions each  \u2022  15s timer', 'cyan')
    cprint('  Easy  \u2192  Medium  \u2192  Hard', 'cyan')
    cprint('=' * 48, 'cyan')
    print()
    sfx.play_wait('intro')


def main():
    sfx = SoundManager()
    print_banner(sfx)
    input('  Press ENTER to begin...\n')

    while True:
        scores = {}
        for i, mode in enumerate(MODES, 1):
            scores[mode] = run_mode(mode, i, sfx)

        show_results(scores, sfx)

        print()
        if input('Play again? (y/n): ').lower().strip() != 'y':
            cprint('\nThanks for playing! Goodbye \U0001f44b\n', 'cyan')
            break


if __name__ == '__main__':
    main()