import pygame
import random
import sys
import numpy as np

# ── Init ──────────────────────────────────────────────────────────────────────
pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

CELL  = 24
COLS  = 30
ROWS  = 24
W     = COLS * CELL          # 720
H     = ROWS * CELL + 60     # 636  (60px HUD at top)
FPS   = 60

screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("🐍 SNAKE")
clock  = pygame.time.Clock()

# ── Colours ───────────────────────────────────────────────────────────────────
BG      = (13,  13,  13)
GRID    = (25,  25,  25)
HUD_BG  = (10,  10,  28)
S_HEAD  = (0,   220, 120)
S_BODY  = (0,   160, 80)
S_TAIL  = (0,   100, 50)
FOOD_C  = (255, 80,  80)
FOOD_G  = (80,  220, 80)   # bonus food
FOOD_B  = (80,  150, 255)  # speed food
WHT     = (245, 245, 247)
GRY     = (130, 130, 140)
ACC     = (255, 107, 53)
CYAN    = (0,   212, 255)
YELLOW  = (255, 214, 10)
RED     = (255, 69,  58)
GREEN   = (48,  209, 88)
PURPLE  = (180, 80,  255)

# ── Fonts ─────────────────────────────────────────────────────────────────────
F_LG = pygame.font.SysFont("Arial", 52, bold=True)
F_MD = pygame.font.SysFont("Arial", 28, bold=True)
F_SM = pygame.font.SysFont("Arial", 18, bold=True)
F_XS = pygame.font.SysFont("Arial", 14)

# ══════════════════════════════════════════════════════════════════════════════
#  SOUND  (generated — no files needed)
# ══════════════════════════════════════════════════════════════════════════════
SR = 44100

def _stereo(mono):
    return pygame.sndarray.make_sound(
        np.ascontiguousarray(np.column_stack([mono, mono])))

def _tone(freq, dur, vol=0.4, fade=True):
    t = np.linspace(0, dur, int(SR*dur), False)
    w = np.sin(2*np.pi*freq*t)
    if fade: w *= np.linspace(1, 0, len(w))
    return (w * vol * 32767).astype(np.int16)

def _melody(notes, beat=0.08, vol=0.45):
    return _stereo(np.concatenate([_tone(f, beat*b, vol) for f,b in notes]))

SFX = {
    "eat":      _stereo(_tone(660, 0.06, 0.35)),
    "bonus":    _melody([(523,1),(784,1),(1047,1.5)], beat=0.07),
    "speedup":  _melody([(400,1),(600,1)],            beat=0.07),
    "die":      _melody([(300,1),(220,1),(160,2)],    beat=0.12, vol=0.55),
    "levelup":  _melody([(523,1),(659,1),(784,1),(1047,2)], beat=0.09),
    "start":    _melody([(262,1),(330,1),(392,1),(523,2)],  beat=0.08),
}
def sfx(n): SFX.get(n, SFX["eat"]).play()

# ══════════════════════════════════════════════════════════════════════════════
#  PARTICLES
# ══════════════════════════════════════════════════════════════════════════════
particles = []

def spawn_parts(x, y, col, n=14):
    import math
    for _ in range(n):
        a = random.uniform(0, 2*math.pi)
        s = random.uniform(1, 4)
        life = random.randint(12, 30)
        particles.append([x, y, math.cos(a)*s, math.sin(a)*s, life, life, col])

def tick_parts(surf):
    global particles
    alive = []
    for p in particles:
        p[0]+=p[2]; p[1]+=p[3]; p[4]-=1
        if p[4] > 0:
            a = int(255*p[4]/p[5])
            r = max(1, int(3*p[4]/p[5]))
            s = pygame.Surface((r*2,r*2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*p[6], a), (r,r), r)
            surf.blit(s, (int(p[0])-r, int(p[1])-r))
            alive.append(p)
    particles[:] = alive

# ══════════════════════════════════════════════════════════════════════════════
#  DRAW HELPERS
# ══════════════════════════════════════════════════════════════════════════════
def cell_rect(cx, cy):
    return pygame.Rect(cx*CELL+1, cy*CELL+61, CELL-2, CELL-2)

def draw_grid():
    for x in range(COLS):
        for y in range(ROWS):
            pygame.draw.rect(screen, GRID, cell_rect(x, y))

def draw_snake(snake, direction):
    n = len(snake)
    for i, (cx, cy) in enumerate(snake):
        r = cell_rect(cx, cy)
        if i == 0:          col = S_HEAD
        elif i == n-1:      col = S_TAIL
        else:
            t = i / max(n-1, 1)
            col = (
                int(S_BODY[0] + t*(S_TAIL[0]-S_BODY[0])),
                int(S_BODY[1] + t*(S_TAIL[1]-S_BODY[1])),
                int(S_BODY[2] + t*(S_TAIL[2]-S_BODY[2])),
            )
        pygame.draw.rect(screen, col, r, border_radius=5)

        # eyes on head
        if i == 0:
            dx, dy = direction
            ex = r.centerx + dx*5
            ey = r.centery + dy*5
            perp = (-dy, dx)
            for side in [-1, 1]:
                ex2 = ex + perp[0]*4*side
                ey2 = ey + perp[1]*4*side
                pygame.draw.circle(screen, WHT, (ex2, ey2), 3)
                pygame.draw.circle(screen, (0,0,0), (ex2+dx, ey2+dy), 1)

def draw_food(food_list):
    for fx, fy, ftype in food_list:
        r = cell_rect(fx, fy)
        if ftype == "normal":
            pygame.draw.rect(screen, FOOD_C, r, border_radius=6)
            # shine
            shine = pygame.Rect(r.x+3, r.y+3, 5, 5)
            pygame.draw.rect(screen, (255,160,160), shine, border_radius=3)
        elif ftype == "bonus":
            pygame.draw.rect(screen, FOOD_G, r, border_radius=6)
            lbl = F_XS.render("★", True, YELLOW)
            screen.blit(lbl, (r.x+3, r.y+2))
        elif ftype == "speed":
            pygame.draw.rect(screen, FOOD_B, r, border_radius=6)
            lbl = F_XS.render("⚡", True, WHT)
            screen.blit(lbl, (r.x+2, r.y+2))

def draw_hud(score, high_score, level, length, speed_boost):
    pygame.draw.rect(screen, HUD_BG, (0, 0, W, 60))
    pygame.draw.line(screen, CYAN, (0, 60), (W, 60), 2)

    screen.blit(F_SM.render(f"SCORE  {score:,}", True, WHT),  (14, 8))
    screen.blit(F_SM.render(f"BEST  {high_score:,}", True, YELLOW), (14, 32))

    lv = F_SM.render(f"LEVEL {level}", True, CYAN)
    screen.blit(lv, (W//2 - lv.get_width()//2, 20))

    ln = F_SM.render(f"LENGTH  {length}", True, GREEN)
    screen.blit(ln, (W - ln.get_width() - 14, 8))

    if speed_boost > 0:
        sb = F_SM.render(f"⚡ SPEED  {speed_boost:.0f}", True, FOOD_B)
        screen.blit(sb, (W - sb.get_width() - 14, 32))

# ══════════════════════════════════════════════════════════════════════════════
#  SCREENS
# ══════════════════════════════════════════════════════════════════════════════
def title_screen(high_score):
    sfx("start")
    while True:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN: return
                if event.key == pygame.K_ESCAPE: pygame.quit(); sys.exit()

        screen.fill(BG)
        draw_grid()

        for off, col in [(5,(0,60,40)),(2,(0,120,70)),(0,S_HEAD)]:
            t = F_LG.render("SNAKE", True, col)
            screen.blit(t, (W//2-t.get_width()//2+off, 160+off))

        lines = [
            (F_MD, "Arrow Keys / WASD  —  Move",  WHT,  250),
            (F_SM, "Eat 🔴 red food to grow",      GRY,  295),
            (F_SM, "🟢 Bonus food = +5 pts",       GREEN, 320),
            (F_SM, "⚡ Speed food = turbo boost",  FOOD_B, 345),
            (F_SM, f"High Score:  {high_score:,}", YELLOW, 385),
            (F_MD, "Press ENTER to play",          ACC,   435),
            (F_XS, "ESC to quit",                  GRY,   475),
        ]
        for fnt, txt, col, y in lines:
            s = fnt.render(txt, True, col)
            screen.blit(s, (W//2-s.get_width()//2, y))

        pygame.display.flip()


def game_over_screen(score, high_score, new_best):
    sfx("die")
    while True:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN: return True
                if event.key == pygame.K_ESCAPE: return False

        screen.fill(BG)
        draw_grid()

        ov = pygame.Surface((W, H), pygame.SRCALPHA)
        ov.fill((0,0,0,180))
        screen.blit(ov, (0,0))

        for off, col in [(4,(80,0,0)),(2,RED),(0,(255,120,120))]:
            t = F_LG.render("GAME OVER", True, col)
            screen.blit(t, (W//2-t.get_width()//2+off, 160+off))

        s = F_MD.render(f"Score:  {score:,}", True, WHT)
        screen.blit(s, (W//2-s.get_width()//2, 260))

        if new_best:
            nb = F_MD.render("🏆  NEW HIGH SCORE!", True, YELLOW)
            screen.blit(nb, (W//2-nb.get_width()//2, 310))
        else:
            hs = F_MD.render(f"Best:  {high_score:,}", True, YELLOW)
            screen.blit(hs, (W//2-hs.get_width()//2, 310))

        r = F_MD.render("ENTER = play again    ESC = quit", True, GREEN)
        screen.blit(r, (W//2-r.get_width()//2, 390))

        pygame.display.flip()


def pause_screen():
    ov = pygame.Surface((W, H), pygame.SRCALPHA)
    ov.fill((0,0,0,160))
    screen.blit(ov, (0,0))
    t = F_LG.render("PAUSED", True, CYAN)
    screen.blit(t, (W//2-t.get_width()//2, H//2-50))
    r = F_SM.render("Press P to resume", True, WHT)
    screen.blit(r, (W//2-r.get_width()//2, H//2+20))
    pygame.display.flip()

# ══════════════════════════════════════════════════════════════════════════════
#  GAME
# ══════════════════════════════════════════════════════════════════════════════
def place_food(snake, food_list, ftype="normal"):
    snake_set = set(snake)
    food_set  = {(f[0],f[1]) for f in food_list}
    while True:
        pos = (random.randint(0,COLS-1), random.randint(0,ROWS-1))
        if pos not in snake_set and pos not in food_set:
            return [pos[0], pos[1], ftype]


def run_game(high_score):
    # initial snake (centre)
    sx, sy    = COLS//2, ROWS//2
    snake      = [(sx, sy), (sx-1, sy), (sx-2, sy)]
    direction  = (1, 0)
    next_dir   = (1, 0)

    food_list  = [place_food(snake, [])]
    score      = 0
    level      = 1
    move_timer = 0
    base_speed = 140      # ms per move
    move_delay = base_speed
    bonus_timer  = 0      # frames until bonus food spawns
    speed_boost  = 0.0    # seconds of speed boost remaining
    paused       = False

    # schedule special foods
    bonus_cd   = random.randint(200, 400)
    speed_cd   = random.randint(300, 500)

    particles.clear()

    running = True
    while running:
        dt = clock.tick(FPS)

        # ── events ────────────────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    paused = not paused
                if paused: continue
                if event.key in (pygame.K_UP,    pygame.K_w) and direction != (0,1):
                    next_dir = (0,-1)
                if event.key in (pygame.K_DOWN,  pygame.K_s) and direction != (0,-1):
                    next_dir = (0,1)
                if event.key in (pygame.K_LEFT,  pygame.K_a) and direction != (1,0):
                    next_dir = (-1,0)
                if event.key in (pygame.K_RIGHT, pygame.K_d) and direction != (-1,0):
                    next_dir = (1,0)

        if paused:
            pause_screen(); continue

        # ── move timer ────────────────────────────────────────────────────────
        effective_delay = move_delay // 2 if speed_boost > 0 else move_delay
        move_timer += dt
        if speed_boost > 0:
            speed_boost -= dt / 1000

        # special food countdown
        bonus_cd -= 1
        speed_cd -= 1
        if bonus_cd <= 0:
            food_list.append(place_food(snake, food_list, "bonus"))
            bonus_cd = random.randint(250, 500)
        if speed_cd <= 0:
            food_list.append(place_food(snake, food_list, "speed"))
            speed_cd = random.randint(300, 600)

        if move_timer < effective_delay:
            # just draw
            screen.fill(BG)
            draw_grid()
            draw_food(food_list)
            draw_snake(snake, direction)
            tick_parts(screen)
            draw_hud(score, high_score, level, len(snake), speed_boost)
            pygame.display.flip()
            continue

        move_timer = 0
        direction  = next_dir

        # ── move snake ────────────────────────────────────────────────────────
        hx, hy = snake[0]
        nx, ny = hx + direction[0], hy + direction[1]

        # wall collision
        if nx < 0 or nx >= COLS or ny < 0 or ny >= ROWS:
            new_best = score > high_score
            if new_best: high_score = score
            return high_score, game_over_screen(score, high_score, new_best)

        # self collision
        if (nx, ny) in snake[:-1]:
            new_best = score > high_score
            if new_best: high_score = score
            return high_score, game_over_screen(score, high_score, new_best)

        snake.insert(0, (nx, ny))

        # ── food collision ─────────────────────────────────────────────────────
        ate = None
        for f in food_list:
            if f[0] == nx and f[1] == ny:
                ate = f; break

        if ate:
            food_list.remove(ate)
            cx = nx*CELL + CELL//2
            cy = ny*CELL + CELL//2 + 60

            if ate[2] == "normal":
                score += 1
                sfx("eat")
                spawn_parts(cx, cy, FOOD_C, 10)
                food_list.append(place_food(snake, food_list, "normal"))

            elif ate[2] == "bonus":
                score += 5
                sfx("bonus")
                spawn_parts(cx, cy, FOOD_G, 20)

            elif ate[2] == "speed":
                speed_boost += 5.0
                sfx("speedup")
                spawn_parts(cx, cy, FOOD_B, 15)
                snake.append(snake[-1])  # also grow

            # level up every 10 points
            new_level = 1 + score // 10
            if new_level > level:
                level = new_level
                move_delay = max(60, base_speed - level * 10)
                sfx("levelup")

            high_score = max(high_score, score)

        else:
            snake.pop()   # no food eaten — remove tail

        # ── draw ──────────────────────────────────────────────────────────────
        screen.fill(BG)
        draw_grid()
        draw_food(food_list)
        draw_snake(snake, direction)
        tick_parts(screen)
        draw_hud(score, high_score, level, len(snake), speed_boost)
        pygame.display.flip()

    return high_score, False


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════════════════════
def main():
    high_score = 0
    title_screen(high_score)

    while True:
        high_score, play_again = run_game(high_score)
        if not play_again:
            pygame.quit(); sys.exit()
        title_screen(high_score)


if __name__ == "__main__":
    main()