import turtle
import random
import os

# 1. Setup
win = turtle.Screen()
win.title("Whack-a-Mole: Comic Boom Edition")
win.bgcolor("#87CEEB")
win.setup(width=600, height=600)
win.tracer(0)

# Sound helper (requires 'boom.wav' and 'whack.wav' in your folder)
def play_sound(file):
    try:
        if os.name == 'posix': os.system(f"afplay {file} &")
        else:
            import winsound
            winsound.PlaySound(file, winsound.SND_ASYNC)
    except: pass

# 2. Environment (Grass & Fence)
draw = turtle.Turtle()
draw.hideturtle(); draw.penup()
draw.goto(-300, -300); draw.color("#94D050"); draw.begin_fill()
for _ in range(2): draw.forward(600); draw.left(90); draw.forward(400); draw.left(90)
draw.end_fill()

# 3. THE HOLES (Brown circles)
hole_pos = [(-180, 40), (0, 40), (180, 40), (-180, -90), (0, -90), (180, -90), (-180, -220), (0, -220), (180, -220)]
for pos in hole_pos:
    h = turtle.Turtle()
    h.shape("circle"); h.shapesize(1.5, 4); h.color("#3B2F2F") # Dark brown holes
    h.penup(); h.goto(pos)

# 4. Mole & Comic Effects
mole = turtle.Turtle(); mole.shape("circle"); mole.penup()
l_eye = turtle.Turtle(); l_eye.shape("circle"); l_eye.color("white"); l_eye.shapesize(1.5); l_eye.penup()
r_eye = turtle.Turtle(); r_eye.shape("circle"); r_eye.color("white"); r_eye.shapesize(1.5); r_eye.penup()
nose = turtle.Turtle(); nose.shape("circle"); nose.color("black"); nose.shapesize(1.0); nose.penup()
parts = [mole, l_eye, r_eye, nose]

# Comic Boom Pen
effect_pen = turtle.Turtle(); effect_pen.hideturtle(); effect_pen.penup()

def draw_comic_boom(x, y):
    # Draw White Cloud
    effect_pen.goto(x, y)
    effect_pen.color("white")
    for _ in range(8):
        effect_pen.goto(x + random.randint(-30, 30), y + random.randint(-30, 30))
        effect_pen.dot(random.randint(70, 110))
    
    # Draw Yellow Sparks
    effect_pen.color("yellow")
    for _ in range(10):
        effect_pen.goto(x, y)
        effect_pen.setheading(random.randint(0, 360))
        effect_pen.forward(random.randint(40, 80))
        effect_pen.dot(random.randint(10, 20))
    
    # Big Red Text
    effect_pen.goto(x, y - 25)
    effect_pen.color("red")
    effect_pen.write("BOOM!", align="center", font=("Impact", 50, "bold"))
    play_sound("boom.wav")

# 5. Hammer
h_head = turtle.Turtle(); h_head.shape("square"); h_head.color("#707070"); h_head.shapesize(2, 3); h_head.penup()
h_handle = turtle.Turtle(); h_handle.shape("square"); h_handle.color("#5C4033"); h_handle.shapesize(3, 0.6); h_handle.penup()

# 6. Game Logic
score = 0
time_left = 30
pen = turtle.Turtle(); pen.hideturtle(); pen.penup()

def update_ui():
    pen.clear(); pen.color("black")
    pen.goto(-180, 250); pen.write(f"Time: {time_left}", font=("Arial", 18, "bold"))
    pen.goto(100, 250); pen.write(f"Score: {score}", font=("Arial", 18, "bold"))

def move_mole():
    if time_left > 0:
        mole.is_bomb = random.random() < 0.2
        mole.color("red" if mole.is_bomb else "#A0522D")
        x, y = random.choice(hole_pos)
        y += 40
        mole.goto(x, y); l_eye.goto(x-15, y+15); r_eye.goto(x+15, y+15); nose.goto(x, y-5)
        for p in parts: p.showturtle()
        if mole.is_bomb: [p.hideturtle() for p in [l_eye, r_eye, nose]]
        win.ontimer(move_mole, 900)

def whack(x, y):
    global score
    if time_left > 0 and mole.distance(x, y) < 60:
        if mole.is_bomb:
            score -= 5
            draw_comic_boom(x, y)
        else:
            score += 1
            effect_pen.goto(x, y + 40); effect_pen.color("red")
            effect_pen.write("WHACK!", align="center", font=("Impact", 30, "bold"))
            play_sound("whack.wav")
        [p.hideturtle() for p in parts]
        win.ontimer(lambda: effect_pen.clear(), 500)

def follow_mouse(event):
    mx, my = event.x - 300, 300 - event.y
    h_head.goto(mx, my); h_handle.goto(mx, my - 35)

# Bindings
canvas = win.getcanvas(); canvas.bind('<Motion>', follow_mouse)
win.onclick(whack)

# Start
update_ui()
move_mole()
def countdown():
    global time_left
    if time_left > 0:
        time_left -= 1
        update_ui()
        win.ontimer(countdown, 1000)
countdown()

while True:
    win.update()
