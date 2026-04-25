import pygame, random, sys, math
import numpy as np

# ── Init ──────────────────────────────────────────────────────────────────────
pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

W, H   = 900, 680
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("SPACE SHOOTER")
clock  = pygame.time.Clock()
FPS    = 60

# ── Colours ───────────────────────────────────────────────────────────────────
WHITE  = (255,255,255); RED    = (220, 50, 50);  GREEN  = ( 50,220, 50)
BLUE   = ( 50,130,255); CYAN   = (  0,220,255);  YELLOW = (255,220,  0)
ORANGE = (255,140,  0); PURPLE = (160, 50,255);  GREY   = (100,100,120)
DKBLUE = (  5,  5, 25); GOLD   = (255,200,  0);  PINK   = (255,100,200)
LIME   = ( 80,255,120); TEAL   = (  0,180,160);  BLACK  = (  0,  0,  0)
DKGREY = ( 20, 20, 45)

# ── Fonts ─────────────────────────────────────────────────────────────────────
FL = pygame.font.SysFont('consolas', 46, bold=True)
FM = pygame.font.SysFont('consolas', 25, bold=True)
FS = pygame.font.SysFont('consolas', 18)
FX = pygame.font.SysFont('consolas', 14)

# ══════════════════════════════════════════════════════════════════════════════
#  SOUND
# ══════════════════════════════════════════════════════════════════════════════
SR = 44100

def _stereo(mono):
    return pygame.sndarray.make_sound(
        np.ascontiguousarray(np.column_stack([mono, mono])))

def _tone(freq, dur, vol=0.45, fade=True):
    t = np.linspace(0, dur, int(SR*dur), False)
    w = np.sin(2*np.pi*freq*t)
    if fade: w *= np.linspace(1.0, 0.0, len(w))
    return (w * vol * 32767).astype(np.int16)

def _noise(dur, vol=0.6):
    t = np.linspace(0, dur, int(SR*dur), False)
    w = np.random.uniform(-1,1,len(t)) * np.exp(-t*10)
    return (w * vol * 32767).astype(np.int16)

def _melody(notes, beat=0.09, vol=0.5):
    return _stereo(np.concatenate([_tone(f, beat*b, vol) for f,b in notes]))

def _make_shoot():
    t = np.linspace(0, .12, int(SR*.12), False)
    w = np.sin(2*np.pi*(800-600*t/.12)*t) * np.linspace(1,0,int(SR*.12))
    return _stereo((w*0.4*32767).astype(np.int16))

def _make_shoot2():   # second-player colour
    t = np.linspace(0, .12, int(SR*.12), False)
    w = np.sin(2*np.pi*(600-400*t/.12)*t) * np.linspace(1,0,int(SR*.12))
    return _stereo((w*0.4*32767).astype(np.int16))

SFX = {
    'shoot'    : _make_shoot(),
    'shoot2'   : _make_shoot2(),
    'explosion': _stereo(_noise(0.35, 0.7)),
    'hit'      : _stereo(_noise(0.22, 0.6)),
    'buy'      : _melody([(523,1),(784,2)], beat=0.10),
    'cantbuy'  : _melody([(250,1),(200,2)], beat=0.10),
    'equip'    : _melody([(440,1),(550,1)], beat=0.10),
    'levelup'  : _melody([(523,1),(659,1),(784,1),(1047,2)], beat=0.10),
    'gameover' : _melody([(392,1),(330,1),(262,1),(196,3)],  beat=0.15),
    'start'    : _melody([(262,1),(330,1),(392,1),(523,1),(659,1),(784,2)], beat=0.09),
    'select'   : _stereo(_tone(600, 0.08, 0.3)),
    'coin'     : _stereo(_tone(880, 0.07, 0.35)),
}
def sfx(name): SFX.get(name, SFX['select']).play()

# ══════════════════════════════════════════════════════════════════════════════
#  STARS
# ══════════════════════════════════════════════════════════════════════════════
_stars = [(random.randint(0,W), random.randint(0,H),
           random.uniform(0.3,2.5), random.randint(1,2)) for _ in range(220)]

def draw_stars(surf):
    for x,y,sp,sz in _stars:
        b = int(100+sp*55)
        pygame.draw.circle(surf,(b,b,min(b+50,255)),(int(x),int(y)),sz)

def scroll_stars():
    global _stars
    _stars = [((x,(y+sp)%H,sp,sz)) for x,y,sp,sz in _stars]

# ══════════════════════════════════════════════════════════════════════════════
#  SHIP DRAW FUNCTIONS  (4 types)
# ══════════════════════════════════════════════════════════════════════════════
def _dim(col, factor=0.45):
    return tuple(int(c*factor) for c in col)

def draw_scout(surf, x, y, col, scale=1.0):
    w,h = int(46*scale), int(50*scale)
    cx  = x + w//2
    pygame.draw.polygon(surf, col,       [(cx,y),(cx-w//2+3,y+h-10),(cx,y+h-20),(cx+w//2-3,y+h-10)])
    pygame.draw.ellipse(surf, WHITE,     (cx-6,y+8,12,16))
    pygame.draw.ellipse(surf, BLUE,      (cx-4,y+10,8,11))
    pygame.draw.polygon(surf, _dim(col), [(cx-w//2+3,y+h-10),(cx-w//2-5,y+h),(cx-6,y+h-16)])
    pygame.draw.polygon(surf, _dim(col), [(cx+w//2-3,y+h-10),(cx+w//2+5,y+h),(cx+6,y+h-16)])
    pygame.draw.ellipse(surf, ORANGE,    (cx-6,y+h-12,12,8))

def draw_fighter(surf, x, y, col, scale=1.0):
    w,h = int(50*scale), int(50*scale)
    cx  = x + w//2
    pygame.draw.polygon(surf, col,       [(cx,y),(cx-22,y+40),(cx,y+28),(cx+22,y+40)])
    pygame.draw.polygon(surf, _dim(col), [(cx-22,y+40),(cx-38,y+18),(cx-12,y+26)])
    pygame.draw.polygon(surf, _dim(col), [(cx+22,y+40),(cx+38,y+18),(cx+12,y+26)])
    pygame.draw.circle(surf,  YELLOW,    (cx,y+16), 8)
    pygame.draw.circle(surf,  WHITE,     (cx,y+16), 5)
    pygame.draw.rect(surf,    ORANGE,    (cx-4,y+34,8,10))

def draw_tank(surf, x, y, col, scale=1.0):
    w,h = int(54*scale), int(50*scale)
    cx  = x + w//2
    pygame.draw.rect(surf,    col,       (cx-20,y+6,40,34), border_radius=5)
    pygame.draw.polygon(surf, col,       [(cx,y),(cx-15,y+14),(cx+15,y+14)])
    pygame.draw.polygon(surf, _dim(col), [(cx-20,y+28),(cx-36,y+48),(cx-18,y+40)])
    pygame.draw.polygon(surf, _dim(col), [(cx+20,y+28),(cx+36,y+48),(cx+18,y+40)])
    pygame.draw.rect(surf,    WHITE,     (cx-8,y+10,16,18), border_radius=3)
    pygame.draw.rect(surf,    BLUE,      (cx-5,y+13,10,12), border_radius=2)
    pygame.draw.ellipse(surf, ORANGE,    (cx-7,y+36,14,8))

def draw_stealth(surf, x, y, col, scale=1.0):
    w,h = int(52*scale), int(44*scale)
    cx  = x + w//2
    pygame.draw.polygon(surf, col,       [(cx,y+2),(cx-26,y+44),(cx,y+30),(cx+26,y+44)])
    pygame.draw.polygon(surf, _dim(col), [(cx-26,y+44),(cx-40,y+26),(cx-16,y+34)])
    pygame.draw.polygon(surf, _dim(col), [(cx+26,y+44),(cx+40,y+26),(cx+16,y+34)])
    pygame.draw.ellipse(surf, CYAN,      (cx-5,y+10,10,14))
    pygame.draw.ellipse(surf, WHITE,     (cx-3,y+12, 6,8))

SHIP_DRAWERS = [draw_scout, draw_fighter, draw_tank, draw_stealth]

def draw_ship(surf, idx, x, y, col, scale=1.0):
    SHIP_DRAWERS[idx](surf, x, y, col, scale=scale)

# ══════════════════════════════════════════════════════════════════════════════
#  SHIP & UPGRADE DATA
# ══════════════════════════════════════════════════════════════════════════════
#  (name,      spd,  fire_cd, lives, colour, price,  description)
SHIPS = [
    ("SCOUT",   5.0,  18,     3,     CYAN,    0,    "Balanced starter ship"),
    ("FIGHTER", 6.5,  13,     2,     ORANGE,  500,  "Fast with rapid fire"),
    ("TANK",    3.2,  24,     5,     GREEN,   800,  "Slow but 5 lives"),
    ("STEALTH", 7.8,  16,     2,     PURPLE,  1000, "Fastest, tiny target"),
]
SN,SS,SF,SL,SC,SP,SD = 0,1,2,3,4,5,6   # column indices

#  (key,          display name,   max_lvl, costs per level,          desc)
UPGRADES = [
    ("speed",      "SPEED",        3,       [150, 300, 500],          "+1.2 move speed"),
    ("firerate",   "RAPID FIRE",   3,       [150, 300, 500],          "Faster shooting"),
    ("doubleshot", "DOUBLE SHOT",  1,       [400],                    "Shoot 2 bullets"),
    ("shield",     "SHIELD",       3,       [300, 300, 300],          "Absorbs 1 hit each"),
]
UK,UNAME,UMAX,UCOSTS,UDESC = 0,1,2,3,4

# ══════════════════════════════════════════════════════════════════════════════
#  PARTICLES
# ══════════════════════════════════════════════════════════════════════════════
_parts = []

def spawn_parts(x, y, count=18, col=ORANGE):
    for _ in range(count):
        a = random.uniform(0, 2*math.pi)
        s = random.uniform(1,5)
        life = random.randint(14,36)
        _parts.append([x,y,math.cos(a)*s,math.sin(a)*s,life,life,col])

def tick_parts(surf):
    global _parts
    alive=[]
    for p in _parts:
        p[0]+=p[2]; p[1]+=p[3]; p[4]-=1
        if p[4]>0:
            a=int(255*p[4]/p[5]); r=max(1,int(3*p[4]/p[5]))
            s=pygame.Surface((r*2,r*2),pygame.SRCALPHA)
            pygame.draw.circle(s,(*p[6],a),(r,r),r)
            surf.blit(s,(int(p[0])-r,int(p[1])-r))
            alive.append(p)
    _parts[:]=alive

# ══════════════════════════════════════════════════════════════════════════════
#  PLAYER CLASS
# ══════════════════════════════════════════════════════════════════════════════
class Player:
    PW, PH = 46, 50

    def __init__(self, sx, sy, controls, label, hud_col, shoot_sfx='shoot'):
        self.x = float(sx);  self.y = float(sy)
        self.controls    = controls
        self.label       = label
        self.hud_col     = hud_col
        self.shoot_sfx   = shoot_sfx
        # ship state
        self.ship_idx    = 0
        self.owned       = {0}
        self.upg         = {'speed':0,'firerate':0,'doubleshot':0,'shield':0}
        self.lives       = SHIPS[0][SL]
        # game state
        self.coins       = 0
        self.score       = 0
        self.bullets     = []
        self.shoot_cd    = 0
        self.inv         = 0     # invincibility frames
        self.alive       = True

    # ── derived ───────────────────────────────────────────────────────────────
    @property
    def ship(self):  return SHIPS[self.ship_idx]
    @property
    def color(self): return self.ship[SC]
    @property
    def speed(self): return self.ship[SS] + self.upg['speed']*1.2
    @property
    def fcd(self):   return max(7, self.ship[SF] - self.upg['firerate']*3)

    # ── shop ──────────────────────────────────────────────────────────────────
    def buy_ship(self, idx):
        price = SHIPS[idx][SP]
        if idx in self.owned:
            if idx == self.ship_idx:
                return False, "Already equipped!"
            self.ship_idx = idx
            sfx('equip')
            return True, f"Equipped {SHIPS[idx][SN]}!"
        if self.coins < price:
            sfx('cantbuy'); return False, "Not enough coins!"
        self.coins -= price
        self.owned.add(idx)
        self.ship_idx = idx
        self.lives = SHIPS[idx][SL]
        sfx('buy')
        return True, f"Bought {SHIPS[idx][SN]}!"

    def buy_upgrade(self, key):
        upg = next(u for u in UPGRADES if u[UK]==key)
        cur = self.upg[key]
        if cur >= upg[UMAX]: sfx('cantbuy'); return False, "Already maxed!"
        cost = upg[UCOSTS][cur]
        if self.coins < cost: sfx('cantbuy'); return False, "Not enough coins!"
        self.coins -= cost
        self.upg[key] += 1
        sfx('buy')
        return True, f"{upg[UNAME]} → Lv{self.upg[key]}"

    # ── per-frame ─────────────────────────────────────────────────────────────
    def handle_input(self, keys):
        if not self.alive: return
        c = self.controls
        if keys[c['left']]  and self.x > 0:          self.x -= self.speed
        if keys[c['right']] and self.x < W-self.PW:  self.x += self.speed
        if keys[c['shoot']] and self.shoot_cd == 0:
            self._fire()
        if self.shoot_cd > 0: self.shoot_cd -= 1
        if self.inv > 0:      self.inv -= 1
        self.bullets = [[bx,by-14] for bx,by in self.bullets if by>-10]

    def _fire(self):
        bx = self.x + self.PW//2 - 2
        self.bullets.append([bx, self.y-4])
        if self.upg['doubleshot']:
            self.bullets.append([bx-16, self.y+6])
            self.bullets.append([bx+16, self.y+6])
        sfx(self.shoot_sfx)
        self.shoot_cd = self.fcd

    def take_hit(self):
        if self.inv > 0: return
        if self.upg['shield'] > 0:
            self.upg['shield'] -= 1
            self.inv = 60
            spawn_parts(self.x+self.PW//2, self.y+self.PH//2, 12, CYAN)
            sfx('hit'); return
        self.lives -= 1
        self.inv = 120
        spawn_parts(self.x+self.PW//2, self.y+self.PH//2, 25, RED)
        sfx('hit')
        if self.lives <= 0: self.alive = False

    def draw(self, surf):
        if not self.alive: return
        if self.inv==0 or (self.inv//6)%2==0:
            draw_ship(surf, self.ship_idx, int(self.x), int(self.y), self.color)
            if self.upg['shield']>0:
                sh = pygame.Surface((self.PW+18,self.PH+18), pygame.SRCALPHA)
                pygame.draw.ellipse(sh,(0,200,255,55),(0,0,self.PW+18,self.PH+18))
                pygame.draw.ellipse(sh,(0,200,255,160),(0,0,self.PW+18,self.PH+18),2)
                surf.blit(sh,(int(self.x)-9,int(self.y)-9))
        for bx,by in self.bullets:
            pygame.draw.rect(surf, YELLOW, (int(bx),int(by),4,14))
            pygame.draw.ellipse(surf, WHITE, (int(bx)-1,int(by)-3,6,6))

# ══════════════════════════════════════════════════════════════════════════════
#  BOT PLAYER (AI)
# ══════════════════════════════════════════════════════════════════════════════
class BotPlayer(Player):
    def __init__(self, sx, sy):
        super().__init__(sx, sy, {}, "BOT", PINK, 'shoot2')
        self.ship_idx = 1         # Bot always uses Fighter
        self.owned    = {0,1}
        self.lives    = SHIPS[1][SL]
        self._tgt_x   = float(sx)
        self._dodge   = 0

    def handle_input(self, keys, enemies=None, e_bullets=None):
        if not self.alive: return
        enemies   = enemies   or []
        e_bullets = e_bullets or []

        # Pick nearest enemy as target
        if enemies:
            nearest = min(enemies, key=lambda e: abs(e[0]+22-(self.x+self.PW//2)))
            self._tgt_x = float(nearest[0]+22 - self.PW//2)

        # Dodge incoming bullets
        danger = [eb for eb in e_bullets
                  if abs(eb[0]-self.x)<90 and self.y-120<eb[1]<self.y+20 and eb[3]>0]
        if danger:
            avg = sum(eb[0] for eb in danger)/len(danger)
            self._tgt_x += 130 if avg < self.x+self.PW//2 else -130

        self._tgt_x = max(0, min(W-self.PW, self._tgt_x))
        dx = self._tgt_x - self.x
        if abs(dx)>3: self.x += math.copysign(min(self.speed, abs(dx)), dx)

        # Shoot
        if enemies and self.shoot_cd==0:
            nearest_ex = min(enemies, key=lambda e: abs(e[0]+22-(self.x+self.PW//2)))[0]
            if abs(nearest_ex+22-(self.x+self.PW//2)) < 50:
                self._fire()

        if self.shoot_cd>0: self.shoot_cd-=1
        if self.inv>0:      self.inv-=1
        self.bullets = [[bx,by-14] for bx,by in self.bullets if by>-10]

# ══════════════════════════════════════════════════════════════════════════════
#  ENEMY HELPERS
# ══════════════════════════════════════════════════════════════════════════════
def draw_enemy(surf, x, y, etype):
    cx,cy = int(x)+22, int(y)+18
    ix,iy = int(x), int(y)
    if etype==0:
        pygame.draw.ellipse(surf, RED,    (ix,    iy+8,  44,18))
        pygame.draw.ellipse(surf, ORANGE, (cx-12, iy,    24,22))
        pygame.draw.ellipse(surf, YELLOW, (cx-5,  iy+4,  10,10))
    elif etype==1:
        pygame.draw.polygon(surf, PURPLE, [(cx,iy),(cx-20,iy+36),(cx,iy+24),(cx+20,iy+36)])
        pygame.draw.polygon(surf, BLUE,   [(cx-20,iy+36),(cx-34,iy+12),(cx-10,iy+20)])
        pygame.draw.polygon(surf, BLUE,   [(cx+20,iy+36),(cx+34,iy+12),(cx+10,iy+20)])
    elif etype==2:
        pts=[(cx+int(23*math.cos(math.radians(a))),
              cy+int(17*math.sin(math.radians(a)))) for a in range(0,360,60)]
        pygame.draw.polygon(surf,(180,0,50),pts)
        pygame.draw.polygon(surf,RED,pts,3)
        pygame.draw.circle(surf,YELLOW,(cx,cy),9)

def draw_enemy_bullet(surf, x, y):
    pygame.draw.rect(surf,  RED,    (int(x),int(y),4,12))
    pygame.draw.ellipse(surf,ORANGE,(int(x)-1,int(y)+10,6,5))

def draw_expl(surf, x, y, frame, maxf):
    prog=frame/maxf; r=int(prog*52); alp=int(255*(1-prog))
    for roff,col in [(0,ORANGE),(8,YELLOW),(18,RED)]:
        rr=max(1,r-roff)
        s=pygame.Surface((rr*2+4,rr*2+4),pygame.SRCALPHA)
        pygame.draw.circle(s,(*col,max(0,alp-roff*8)),(rr+2,rr+2),rr,3)
        surf.blit(s,(x-rr-2,y-rr-2))

def spawn_wave(level):
    cols  = min(9, 4+level)
    rows  = min(4, 1+level//2)
    etype = min(2,(level-1)//3)
    wave  = []
    for row in range(rows):
        for col in range(cols):
            ex = 55 + col*((W-110)//cols)
            ey = 62 + row*58
            hp = 1 + level//3
            wave.append([float(ex),float(ey),hp,etype,1,random.randint(60,180)])
    return wave

# ══════════════════════════════════════════════════════════════════════════════
#  SHOP SCREEN
# ══════════════════════════════════════════════════════════════════════════════
def run_shop(player: Player):
    """Blocking shop loop. Returns when player closes shop."""
    sel_sec = 0    # 0=ships, 1=upgrades
    sel_idx = 0
    msg     = ""
    msg_timer = 0

    while True:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                sfx('select')

                if event.key in (pygame.K_s, pygame.K_ESCAPE):
                    return  # close shop

                elif event.key == pygame.K_TAB:
                    sel_sec = 1 - sel_sec
                    sel_idx = 0

                elif event.key == pygame.K_LEFT:
                    sel_idx = max(0, sel_idx-1)
                elif event.key == pygame.K_RIGHT:
                    max_i = len(SHIPS)-1 if sel_sec==0 else len(UPGRADES)-1
                    sel_idx = min(max_i, sel_idx+1)

                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    if sel_sec == 0:
                        ok, msg = player.buy_ship(sel_idx)
                    else:
                        ok, msg = player.buy_upgrade(UPGRADES[sel_idx][UK])
                    msg_timer = 120

        if msg_timer > 0: msg_timer -= 1
        else: msg = ""

        # ── draw ─────────────────────────────────────────────────────────────
        screen.fill(DKBLUE)
        draw_stars(screen)
        _draw_shop_ui(screen, player, msg, sel_sec, sel_idx)
        pygame.display.flip()


def _draw_shop_ui(surf, player, msg, sel_sec, sel_idx):
    # panel
    panel = pygame.Rect(18, 18, W-36, H-36)
    pygame.draw.rect(surf,(8,8,35),panel,border_radius=12)
    pygame.draw.rect(surf,CYAN,panel,2,border_radius=12)

    # header
    t = FM.render("  S H O P  ", True, GOLD)
    surf.blit(t,(W//2-t.get_width()//2, 28))
    c = FM.render(f"COINS: {player.coins:,}", True, GOLD)
    surf.blit(c,(W-c.get_width()-30, 28))
    lbl = FS.render(f"{player.label}  |  {SHIPS[player.ship_idx][SN]}", True, player.hud_col)
    surf.blit(lbl,(30,28))

    # ── SHIPS section ─────────────────────────────────────────────────────────
    sh_lbl = FS.render("[ SHIPS ]", True, CYAN if sel_sec==0 else GREY)
    surf.blit(sh_lbl,(30,70))

    CARD_W, CARD_H = 196, 200
    gap = (W - 36 - 4*CARD_W) // 5

    for i, ship in enumerate(SHIPS):
        col  = ship[SC]
        cx   = 30 + gap + i*(CARD_W+gap)
        cy   = 94
        is_sel    = sel_sec==0 and sel_idx==i
        is_active = player.ship_idx==i
        is_owned  = i in player.owned

        bg = (20,80,20) if is_active else ((40,40,120) if is_sel else (18,18,50))
        pygame.draw.rect(surf, bg,  (cx,cy,CARD_W,CARD_H), border_radius=8)
        border_col = LIME if is_active else (CYAN if is_sel else GREY)
        pygame.draw.rect(surf, border_col, (cx,cy,CARD_W,CARD_H), 2, border_radius=8)

        draw_ship(surf, i, cx+74, cy+8, col, scale=0.78)

        surf.blit(FS.render(ship[SN], True, col),                  (cx+6, cy+74))
        surf.blit(FX.render(ship[SD], True, GREY),                 (cx+6, cy+95))
        surf.blit(FX.render(f"SPD {ship[SS]:.1f}  FCD {ship[SF]}", True, WHITE),(cx+6,cy+113))
        surf.blit(FX.render(f"LIVES: {ship[SL]}", True, RED),      (cx+6, cy+130))

        if is_active:
            surf.blit(FX.render("[ EQUIPPED ]", True, LIME),  (cx+6, cy+150))
        elif is_owned:
            surf.blit(FX.render("[ OWNED  - select ]", True, GREEN), (cx+6, cy+150))
        else:
            pc = GOLD if player.coins>=ship[SP] else RED
            surf.blit(FX.render(f"COST: {ship[SP]:,}", True, pc),(cx+6,cy+150))
            surf.blit(FX.render("ENTER to buy", True, GREY),     (cx+6,cy+168))

    # ── UPGRADES section ──────────────────────────────────────────────────────
    up_lbl = FS.render("[ UPGRADES ]", True, CYAN if sel_sec==1 else GREY)
    surf.blit(up_lbl,(30,318))

    UPG_W, UPG_H = 196, 168
    ugap = (W-36-4*UPG_W)//5

    for i, upg in enumerate(UPGRADES):
        ux   = 30 + ugap + i*(UPG_W+ugap)
        uy   = 342
        cur  = player.upg[upg[UK]]
        maxed= cur >= upg[UMAX]
        is_sel = sel_sec==1 and sel_idx==i

        bg = (10,50,10) if maxed else ((40,40,120) if is_sel else (18,18,50))
        pygame.draw.rect(surf, bg,  (ux,uy,UPG_W,UPG_H), border_radius=8)
        bc = LIME if maxed else (CYAN if is_sel else GREY)
        pygame.draw.rect(surf, bc,  (ux,uy,UPG_W,UPG_H), 2, border_radius=8)

        surf.blit(FS.render(upg[UNAME], True, CYAN), (ux+6,uy+8))
        surf.blit(FX.render(upg[UDESC], True, GREY), (ux+6,uy+32))

        # pips
        for p in range(upg[UMAX]):
            pc = GOLD if p<cur else (30,30,50)
            pygame.draw.rect(surf, pc, (ux+6+p*26,uy+54,20,14), border_radius=3)
            pygame.draw.rect(surf, GREY, (ux+6+p*26,uy+54,20,14), 1, border_radius=3)

        if maxed:
            surf.blit(FX.render("★ MAXED OUT!", True, LIME),   (ux+6,uy+80))
        else:
            cost = upg[UCOSTS][cur]
            cc   = GOLD if player.coins>=cost else RED
            surf.blit(FX.render(f"COST: {cost}", True, cc),    (ux+6,uy+80))
            surf.blit(FX.render(f"LV {cur} → {cur+1}", True, WHITE),(ux+6,uy+98))

        surf.blit(FX.render("ENTER to buy", True, GREY),(ux+6,uy+118))

    # ── message & hint ────────────────────────────────────────────────────────
    if msg:
        ms = FM.render(msg, True, YELLOW)
        surf.blit(ms,(W//2-ms.get_width()//2, H-76))

    hint = FX.render("◄ ► Navigate    ENTER Buy/Equip    TAB Switch section    S / ESC Close", True, GREY)
    surf.blit(hint,(W//2-hint.get_width()//2, H-42))

# ══════════════════════════════════════════════════════════════════════════════
#  HUD
# ══════════════════════════════════════════════════════════════════════════════
def draw_hud(surf, players, level, high_score):
    pygame.draw.rect(surf,(8,8,28),(0,0,W,50))
    pygame.draw.line(surf,CYAN,(0,50),(W,50),2)

    # high score centred
    hs = FS.render(f"BEST {high_score:,}", True, YELLOW)
    surf.blit(hs,(W//2-hs.get_width()//2,14))

    # level
    lv = FS.render(f"LVL {level}", True, CYAN)
    surf.blit(lv,(W//2-lv.get_width()//2-90,14))

    # per-player panels
    panel_w = min(230, (W-20)//len(players))
    for i, p in enumerate(players):
        px = 10 + i*panel_w
        col = p.hud_col

        # score
        s = FX.render(f"{p.label} {p.score:,}", True, col)
        surf.blit(s,(px,6))

        # lives as mini ships
        for li in range(p.lives):
            draw_ship(surf, p.ship_idx, px+li*26, 24, col, scale=0.42)

        # coin icon + count
        pygame.draw.circle(surf,GOLD,(px+p.lives*26+16,31),7)
        pygame.draw.circle(surf,YELLOW,(px+p.lives*26+16,31),5)
        cn = FX.render(f"{p.coins:,}", True, GOLD)
        surf.blit(cn,(px+p.lives*26+26,25))

    # shop hint
    sh = FX.render("[S] SHOP", True, GREY)
    surf.blit(sh,(W-sh.get_width()-8,16))

# ══════════════════════════════════════════════════════════════════════════════
#  TITLE SCREEN
# ══════════════════════════════════════════════════════════════════════════════
MODE_LABELS = ["1 PLAYER", "2 PLAYERS", "3 PLAYERS", "VS  BOT"]
MODE_DESCS  = [
    "Classic single player",
    "Co-op on one keyboard",
    "Three heroes co-op",
    "You vs an AI opponent",
]
MODE_COLS   = [CYAN, GREEN, ORANGE, PINK]

def title_screen():
    sel = 0
    sfx('start')
    while True:
        clock.tick(FPS)
        scroll_stars()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    sel = (sel-1)%4; sfx('select')
                elif event.key == pygame.K_DOWN:
                    sel = (sel+1)%4; sfx('select')
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    sfx('buy'); return sel
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()

        screen.fill(DKBLUE)
        draw_stars(screen)

        # title
        for off,col in [(5,(0,60,100)),(2,BLUE),(0,CYAN)]:
            t=FL.render("SPACE SHOOTER",True,col)
            screen.blit(t,(W//2-t.get_width()//2+off,110+off))

        # subtitle
        sub=FS.render("Select game mode", True, GREY)
        screen.blit(sub,(W//2-sub.get_width()//2,175))

        # mode cards
        for i,(lbl,desc,col) in enumerate(zip(MODE_LABELS,MODE_DESCS,MODE_COLS)):
            cy = 220+i*90
            is_sel = i==sel
            bg = (30,30,80) if not is_sel else (50,50,160)
            pygame.draw.rect(screen,bg,(W//2-220,cy,440,78),border_radius=10)
            border = col if is_sel else GREY
            pygame.draw.rect(screen,border,(W//2-220,cy,440,78),2,border_radius=10)
            arrow = "▶" if is_sel else " "
            lbl_s = FM.render(f" {arrow} {lbl}", True, col if is_sel else GREY)
            screen.blit(lbl_s,(W//2-220+14,cy+10))
            d_s = FX.render(desc, True, WHITE if is_sel else GREY)
            screen.blit(d_s,(W//2-220+22,cy+44))
            # mini ship preview
            draw_ship(screen, i%4, W//2+168, cy+14, col, scale=0.6)

        # controls reminder
        for txt,y in [("↑↓ Choose    ENTER Start    ESC Quit", 588)]:
            c=FX.render(txt,True,GREY)
            screen.blit(c,(W//2-c.get_width()//2,y))

        pygame.display.flip()

# ══════════════════════════════════════════════════════════════════════════════
#  CONTROLS HELP  (shown at game-start)
# ══════════════════════════════════════════════════════════════════════════════
CONTROL_INFO = {
    "P1" : "← → move   SPACE shoot   S shop",
    "P2" : "A  D move   F     shoot",
    "P3" : "J  L move   I     shoot",
    "BOT": "AI controlled",
}

# ══════════════════════════════════════════════════════════════════════════════
#  GAME LOOP
# ══════════════════════════════════════════════════════════════════════════════
def build_players(mode):
    """Return list of Player objects for chosen mode."""
    p1 = Player(W//2-80, H-90,
                {'left':pygame.K_LEFT,'right':pygame.K_RIGHT,'shoot':pygame.K_SPACE},
                "P1", CYAN, 'shoot')
    if mode==0:    # 1 player
        return [p1]
    if mode==1:    # 2 players
        p2 = Player(W//2+34, H-90,
                    {'left':pygame.K_a,'right':pygame.K_d,'shoot':pygame.K_f},
                    "P2", GREEN, 'shoot2')
        return [p1,p2]
    if mode==2:    # 3 players
        p1.x = W//2-120
        p2 = Player(W//2-24, H-90,
                    {'left':pygame.K_a,'right':pygame.K_d,'shoot':pygame.K_f},
                    "P2", GREEN, 'shoot2')
        p3 = Player(W//2+70, H-90,
                    {'left':pygame.K_j,'right':pygame.K_l,'shoot':pygame.K_i},
                    "P3", ORANGE, 'shoot')
        return [p1,p2,p3]
    if mode==3:    # vs bot
        bot = BotPlayer(W//2+60, H-90)
        return [p1,bot]


def run_game(mode, high_score):
    players   = build_players(mode)
    level     = 1
    enemies   = spawn_wave(level)
    e_bullets = []
    explosions= []
    paused    = False
    banner_alpha = 510
    game_over = False
    new_best  = False
    _parts.clear()

    # brief control-hint screen
    _show_controls(mode, players)

    while True:
        clock.tick(FPS)

        # ── events ────────────────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if game_over:
                    if event.key == pygame.K_RETURN: return high_score
                    if event.key == pygame.K_ESCAPE: pygame.quit(); sys.exit()
                    continue
                if event.key == pygame.K_p and not game_over:
                    paused = not paused
                # shop — P1 always, or P2/P3 if desired
                if event.key == pygame.K_s and not paused:
                    run_shop(players[0])
                if event.key == pygame.K_2 and len(players)>1 and not isinstance(players[1],BotPlayer):
                    run_shop(players[1])
                if event.key == pygame.K_3 and len(players)>2:
                    run_shop(players[2])

        if paused:
            _draw_pause(); pygame.display.flip(); continue
        if game_over:
            screen.fill(DKBLUE); draw_stars(screen)
            tick_parts(screen)
            _draw_gameover(screen, players, high_score, new_best)
            pygame.display.flip(); continue

        # ── update ────────────────────────────────────────────────────────────
        scroll_stars()
        keys = pygame.key.get_pressed()

        for p in players:
            if isinstance(p, BotPlayer):
                p.handle_input(keys, enemies, e_bullets)
            else:
                p.handle_input(keys)

        # move enemies
        spd_x = 1.1 + level*0.28
        edge  = any((e[4]==1 and e[0]>=W-62) or (e[4]==-1 and e[0]<=10) for e in enemies)
        drop  = 22 if edge else 0
        for e in enemies:
            if edge: e[4]*=-1
            e[0]+=spd_x*e[4]
            e[1]+=drop
            e[5]-=1
            if e[5]<=0:
                # shoot toward nearest player
                tgt = min([p for p in players if p.alive],
                          key=lambda p: math.hypot(p.x+p.PW//2-(e[0]+22), p.y+p.PH//2-(e[1]+18)),
                          default=None)
                if tgt:
                    cx2,cy2 = e[0]+22, e[1]+36
                    ang = math.atan2(tgt.y+tgt.PH//2-cy2, tgt.x+tgt.PW//2-cx2)
                    spd2 = 2.4+level*0.18
                    e_bullets.append([cx2,cy2,math.cos(ang)*spd2,math.sin(ang)*spd2])
                e[5]=max(28,random.randint(88-level*4,145-level*4))

        e_bullets=[[x+vx,y+vy,vx,vy] for x,y,vx,vy in e_bullets if -10<x<W+10 and -10<y<H+10]

        # player bullets vs enemies
        for p in players:
            if not p.alive: continue
            alive_b=[]
            for bx,by in p.bullets:
                hit=False
                for e in enemies[:]:
                    if e[0]<bx<e[0]+44 and e[1]<by<e[1]+36:
                        e[2]-=1
                        spawn_parts(bx,by,8,p.color)
                        hit=True
                        if e[2]<=0:
                            spawn_parts(e[0]+22,e[1]+18,28,ORANGE)
                            explosions.append([e[0]+22,e[1]+18,0,22])
                            sfx('explosion')
                            p.score += 100
                            p.coins += 100
                            enemies.remove(e)
                        break
                if not hit: alive_b.append([bx,by])
            p.bullets=alive_b

        # enemy bullets vs players
        alive_eb=[]
        for eb in e_bullets:
            bx,by=eb[0],eb[1]
            hit=False
            for p in players:
                if p.alive and p.x<bx<p.x+p.PW and p.y<by<p.y+p.PH:
                    p.take_hit(); hit=True; break
            if not hit: alive_eb.append(eb)
        e_bullets=alive_eb

        # enemies reach bottom
        for e in enemies:
            if e[1]+36>=H-10:
                for p in players: p.lives=0; p.alive=False

        # advance level
        if not enemies:
            level+=1; sfx('levelup')
            enemies=spawn_wave(level)
            e_bullets.clear()
            banner_alpha=510
            for p in players: p.bullets.clear()

        # update explosions
        explosions=[[x,y,f+1,mf] for x,y,f,mf in explosions if f<mf]

        # check game over
        if all(not p.alive for p in players) and not game_over:
            game_over=True
            best_score=max(p.score for p in players)
            new_best=best_score>high_score
            if new_best: high_score=best_score
            sfx('gameover')

        # ── draw ──────────────────────────────────────────────────────────────
        screen.fill(DKBLUE)
        draw_stars(screen)

        for e in enemies:
            draw_enemy(screen,e[0],e[1],e[3])
            if e[2]>1:
                mx=1+level//3
                pygame.draw.rect(screen,RED,(int(e[0]),int(e[1])-8,44,5))
                pygame.draw.rect(screen,GREEN,(int(e[0]),int(e[1])-8,int(44*e[2]/mx),5))

        for p in players: p.draw(screen)
        for eb in e_bullets: draw_enemy_bullet(screen,eb[0],eb[1])
        for x,y,f,mf in explosions: draw_expl(screen,x,y,f,mf)
        tick_parts(screen)
        draw_hud(screen,players,level,high_score)

        if banner_alpha>0:
            _draw_banner(screen,level,min(255,banner_alpha))
            banner_alpha-=8

        pygame.display.flip()

    return high_score


# ── helper screens ─────────────────────────────────────────────────────────────
def _show_controls(mode, players):
    wait=180
    while wait>0:
        clock.tick(FPS)
        scroll_stars()
        for event in pygame.event.get():
            if event.type==pygame.QUIT: pygame.quit(); sys.exit()
            if event.type==pygame.KEYDOWN: return
        screen.fill(DKBLUE)
        draw_stars(screen)
        t=FM.render("CONTROLS",True,CYAN)
        screen.blit(t,(W//2-t.get_width()//2,200))
        for i,p in enumerate(players):
            info=CONTROL_INFO.get(p.label,"")
            s=FS.render(f"{p.label}: {info}",True,p.hud_col)
            screen.blit(s,(W//2-s.get_width()//2,250+i*34))
        h=FX.render("Press any key to start / S to open shop anytime",True,GREY)
        screen.blit(h,(W//2-h.get_width()//2,430))
        wait-=1
        pygame.display.flip()


def _draw_pause():
    ov=pygame.Surface((W,H),pygame.SRCALPHA); ov.fill((0,0,0,160)); screen.blit(ov,(0,0))
    t=FL.render("PAUSED",True,CYAN)
    screen.blit(t,(W//2-t.get_width()//2,H//2-50))
    r=FS.render("P to resume",True,WHITE)
    screen.blit(r,(W//2-r.get_width()//2,H//2+20))


def _draw_gameover(surf, players, high_score, new_best):
    ov=pygame.Surface((W,H),pygame.SRCALPHA); ov.fill((0,0,0,210)); surf.blit(ov,(0,0))
    t=FL.render("GAME  OVER",True,RED)
    surf.blit(t,(W//2-t.get_width()//2,130))

    for i,p in enumerate(players):
        s=FM.render(f"{p.label}  Score: {p.score:,}  Coins: {p.coins:,}",True,p.hud_col)
        surf.blit(s,(W//2-s.get_width()//2,225+i*44))

    if new_best:
        nb=FM.render("🏆 NEW HIGH SCORE!",True,YELLOW)
        surf.blit(nb,(W//2-nb.get_width()//2,340))
    else:
        hs=FM.render(f"Best: {high_score:,}",True,YELLOW)
        surf.blit(hs,(W//2-hs.get_width()//2,340))

    r=FM.render("ENTER Play again    ESC Quit",True,GREEN)
    surf.blit(r,(W//2-r.get_width()//2,420))


def _draw_banner(surf, level, alpha):
    ov=pygame.Surface((W,80),pygame.SRCALPHA); ov.fill((0,0,0,min(160,alpha)))
    surf.blit(ov,(0,H//2-40))
    t=FL.render(f"LEVEL  {level}",True,(*YELLOW,min(255,alpha)))
    ts=pygame.Surface(t.get_size(),pygame.SRCALPHA); ts.blit(t,(0,0))
    surf.blit(ts,(W//2-t.get_width()//2,H//2-28))


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════════════════════
def main():
    high_score = 0
    while True:
        mode       = title_screen()
        high_score = run_game(mode, high_score)

if __name__ == '__main__':
    main()