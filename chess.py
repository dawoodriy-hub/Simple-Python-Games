import turtle
import random
import time

# 1. Setup
win = turtle.Screen()
win.title("Chess: Bot vs 2-Player Fixed")
win.setup(width=600, height=750)
win.tracer(0)

DARK_GREEN, LIGHT_CREAM, HIGHLIGHT = "#769656", "#eeeed2", "#f7f769"
pieces_icons = {
    "WK": "♔", "WQ": "♕", "WR": "♖", "WB": "♗", "WN": "♘", "WP": "♙",
    "BK": "♚", "BQ": "♛", "BR": "♜", "BB": "♝", "BN": "♞", "BP": "♟"
}

draw = turtle.Turtle()
draw.hideturtle()

def init_game():
    global board, turn, selected_sq, game_over, mode
    board = [
        ["BR", "BN", "BB", "BQ", "BK", "BB", "BN", "BR"],
        ["BP", "BP", "BP", "BP", "BP", "BP", "BP", "BP"],
        ["--"]*8, ["--"]*8, ["--"]*8, ["--"]*8,
        ["WP", "WP", "WP", "WP", "WP", "WP", "WP", "WP"],
        ["WR", "WN", "WB", "WQ", "WK", "WB", "WN", "WR"]
    ]
    turn, selected_sq, game_over, mode = "W", None, False, None
    draw_menu()

# 2. Rule Engine
def is_path_clear(start, end):
    r1, c1, r2, c2 = start[0], start[1], end[0], end[1]
    dr = 1 if r2 > r1 else -1 if r2 < r1 else 0
    dc = 1 if c2 > c1 else -1 if c2 < c1 else 0
    curr_r, curr_c = r1 + dr, c1 + dc
    while (curr_r, curr_c) != (r2, c2):
        if not (0 <= curr_r < 8 and 0 <= curr_c < 8): return False
        if board[curr_r][curr_c] != "--": return False
        curr_r += dr; curr_c += dc
    return True

def is_legal(start, end, p_code, p_color, ignore_king=False):
    r1, c1, r2, c2 = start[0], start[1], end[0], end[1]
    p_type = p_code[1] 
    dr, dc = abs(r2 - r1), abs(c2 - c1)
    target = board[r2][c2]
    
    if not ignore_king and target.endswith("K"): return False 
    if target.startswith(p_color): return False 

    if p_type in ['R', 'B', 'Q']:
        if not is_path_clear(start, end): return False

    if p_type == 'P':
        direction = -1 if p_color == 'W' else 1
        if c1 == c2 and target == "--":
            if r2 - r1 == direction: return True
            if (r1 == 6 or r1 == 1) and r2 - r1 == 2 * direction:
                if board[r1+direction][c1] == "--": return True
        if dr == 1 and dc == 1 and target != "--": return True
    elif p_type == 'N': return (dr == 2 and dc == 1) or (dr == 1 and dc == 2)
    elif p_type == 'R': return r1 == r2 or c1 == c2
    elif p_type == 'B': return dr == dc
    elif p_type == 'Q': return r1 == r2 or c1 == c2 or dr == dc
    elif p_type == 'K': return dr <= 1 and dc <= 1
    return False

def is_in_check(color):
    king_pos = None
    enemy_color = "B" if color == "W" else "W"
    for r in range(8):
        for c in range(8):
            if board[r][c] == color + "K": king_pos = (r, c); break
    if not king_pos: return False
    for r in range(8):
        for c in range(8):
            if board[r][c].startswith(enemy_color):
                if is_legal((r, c), king_pos, board[r][c], enemy_color, ignore_king=True): return True
    return False

# 3. Bot Logic
def bot_make_move():
    global turn, game_over
    if game_over: return
    
    legal_moves = []
    for r in range(8):
        for c in range(8):
            if board[r][c].startswith("B"):
                for tr in range(8):
                    for tc in range(8):
                        if is_legal((r, c), (tr, tc), board[r][c], "B"):
                            legal_moves.append(((r, c), (tr, tc)))
    
    if legal_moves:
        (r, c), (tr, tc) = random.choice(legal_moves)
        board[tr][tc], board[r][c] = board[r][c], "--"
        if tr == 7 and board[tr][tc] == "BP": board[tr][tc] = "BQ"
        if is_in_check("W"): game_over = True
        turn = "W"
        update_display()

# 4. UI
def draw_curvy_button(x, y, w, h, text, color):
    draw.penup(); draw.goto(x + 20, y); draw.pendown()
    draw.color(color); draw.begin_fill()
    for _ in range(2):
        draw.forward(w - 40); draw.circle(20, 90)
        draw.forward(h - 40); draw.circle(20, 90)
    draw.end_fill()
    draw.penup(); draw.goto(x + w/2, y + h/2 - 10); draw.color("white")
    draw.write(text, align="center", font=("Arial", 16, "bold"))

def draw_menu():
    draw.clear(); draw.penup(); draw.goto(0, 100); draw.color("black")
    draw.write("CHOOSE GAME MODE", align="center", font=("Arial", 24, "bold"))
    draw_curvy_button(-150, -50, 300, 60, "1 Player (VS Bot)", DARK_GREEN)
    draw_curvy_button(-150, -150, 300, 60, "2 Player", "#5C4033")
    win.update()

def update_display():
    if mode is None: return
    draw.clear()
    for r in range(8):
        for c in range(8):
            draw.color(HIGHLIGHT if selected_sq == (r, c) else (LIGHT_CREAM if (r+c)%2==0 else DARK_GREEN))
            draw.penup(); draw.goto(c*60-240, 240-r*60); draw.begin_fill()
            for _ in range(4): draw.forward(60); draw.right(90)
            draw.end_fill()
            if board[r][c] != "--":
                draw.goto(c*60-210, 235-r*60-50); draw.color("black")
                draw.write(pieces_icons[board[r][c]], align="center", font=("Arial", 32, "normal"))
    if game_over:
        draw.penup(); draw.goto(0, 20); draw.color("red")
        draw.write("YOU WON!!!!!!", align="center", font=("Arial", 44, "bold"))
        draw_curvy_button(-100, -100, 200, 60, "RESTART", DARK_GREEN)
    win.update()

# 5. Input
def handle_click(x, y):
    global mode, selected_sq, turn, game_over
    if mode is None:
        if -150 < x < 150:
            if -50 < y < 10: mode = "bot" # Fixed: Mode is now 'bot'
            elif -150 < y < -90: mode = "human" # Fixed: Mode is now 'human'
            if mode: update_display()
        return
    if game_over:
        if -100 < x < 100 and -100 < y < -40: init_game()
        return
    
    if mode == "bot" and turn == "B": return # Block clicks during bot turn

    c, r = int((x+240)//60), int((240-y)//60)
    if not (0 <= r < 8 and 0 <= c < 8): return

    if selected_sq is None:
        if board[r][c].startswith(turn): selected_sq = (r, c)
    else:
        sr, sc = selected_sq
        if is_legal((sr, sc), (r, c), board[sr][sc], turn):
            board[r][c], board[sr][sc] = board[sr][sc], "--"
            if turn == "W" and r == 0 and board[r][c] == "WP": board[r][c] = "WQ"
            if is_in_check("B" if turn == "W" else "W"): game_over = True
            turn = "B" if turn == "W" else "W"
            if mode == "bot" and not game_over:
                win.ontimer(bot_make_move, 600) # Wait a bit for the bot to move
        selected_sq = None
    update_display()

init_game()
win.onclick(handle_click)
win.mainloop()
