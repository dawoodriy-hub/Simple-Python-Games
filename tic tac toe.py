import turtle
import random

# 1. Setup
win = turtle.Screen()
win.title("Python Tic Tac Toe")
win.bgcolor("white")
win.setup(width=600, height=600)
win.tracer(0)

# Game State
board = [" " for _ in range(9)]
turn = "X"
game_over = False
mode = None # "bot" or "human"

draw = turtle.Turtle()
draw.hideturtle()
draw.speed(0)

# 2. UI Functions
def draw_button(x, y, w, h, text, color):
    draw.penup(); draw.goto(x + 20, y); draw.pendown()
    draw.color(color); draw.begin_fill()
    for _ in range(2):
        draw.forward(w - 40); draw.circle(20, 90)
        draw.forward(h - 40); draw.circle(20, 90)
    draw.end_fill()
    draw.penup(); draw.goto(x + w/2, y + h/2 - 10); draw.color("white")
    draw.write(text, align="center", font=("Arial", 16, "bold"))

def draw_menu():
    draw.clear()
    draw.penup(); draw.goto(0, 100); draw.color("black")
    draw.write("TIC TAC TOE", align="center", font=("Arial", 32, "bold"))
    draw_button(-150, -20, 300, 60, "VS Smart Bot", "#769656")
    draw_button(-150, -100, 300, 60, "2 Player", "#5C4033")
    win.update()

def draw_grid():
    draw.clear()
    draw.color("black")
    draw.pensize(5)
    # Vertical lines
    for x in [-100, 100]:
        draw.penup(); draw.goto(x, 300); draw.pendown(); draw.goto(x, -300)
    # Horizontal lines
    for y in [-100, 100]:
        draw.penup(); draw.goto(-300, y); draw.pendown(); draw.goto(300, y)

def draw_markers():
    for i in range(9):
        x = (i % 3) * 200 - 200
        y = (i // 3) * -200 + 200
        if board[i] == "X":
            draw.penup(); draw.goto(x - 50, y - 50); draw.color("blue"); draw.pendown()
            draw.goto(x + 50, y + 50); draw.penup(); draw.goto(x + 50, y - 50)
            draw.pendown(); draw.goto(x - 50, y + 50)
        elif board[i] == "O":
            draw.penup(); draw.goto(x, y - 60); draw.color("red"); draw.pendown()
            draw.circle(60)

# 3. Game Logic
def check_win(b, p):
    win_combos = [(0,1,2), (3,4,5), (6,7,8), (0,3,6), (1,4,7), (2,5,8), (0,4,8), (2,4,6)]
    for combo in win_combos:
        if b[combo[0]] == b[combo[1]] == b[combo[2]] == p:
            return True
    return False

def bot_move():
    global turn, game_over
    if game_over: return
    
    # 1. Try to win or Block player
    for p in ["O", "X"]:
        for i in range(9):
            if board[i] == " ":
                board[i] = p
                if check_win(board, p):
                    board[i] = "O"
                    finalize_move()
                    return
                board[i] = " "
    
    # 2. Pick center, then random
    if board[4] == " ": board[4] = "O"
    else:
        empty = [i for i, x in enumerate(board) if x == " "]
        if empty: board[random.choice(empty)] = "O"
    
    finalize_move()

def finalize_move():
    global turn, game_over
    if check_win(board, "O"):
        game_over = "O Wins!"
    elif " " not in board:
        game_over = "Draw!"
    else:
        turn = "X"
    update_screen()

def update_screen():
    draw_grid()
    draw_markers()
    if game_over:
        draw.penup(); draw.goto(0, 0); draw.color("orange")
        draw.write(game_over, align="center", font=("Arial", 50, "bold"))
        draw_button(-75, -250, 150, 50, "RESTART", "gray")
    win.update()

def handle_click(x, y):
    global mode, turn, game_over, board
    
    if mode is None:
        if -150 < x < 150:
            if -20 < y < 40: mode = "bot"
            elif -100 < y < -40: mode = "human"
            if mode: update_screen()
        return

    if game_over:
        if -75 < x < 75 and -250 < y < -200:
            board = [" " for _ in range(9)]; turn = "X"; game_over = False; mode = None
            draw_menu()
        return

    # Convert click to board index
    col = int((x + 300) // 200)
    row = int((300 - y) // 200)
    idx = row * 3 + col

    if 0 <= idx < 9 and board[idx] == " " and not game_over:
        board[idx] = turn
        if check_win(board, turn):
            game_over = f"{turn} Wins!"
        elif " " not in board:
            game_over = "Draw!"
        else:
            if mode == "bot":
                turn = "O"
                update_screen()
                win.ontimer(bot_move, 500)
                return
            turn = "O" if turn == "X" else "X"
        update_screen()

win.onclick(handle_click)
draw_menu()
win.mainloop()
