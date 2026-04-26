import turtle
import random
import time

# 1. Setup
win = turtle.Screen()
win.title("Super Pong: Trail & Power-Up Edition")
win.bgcolor("black")
win.setup(width=800, height=600)
win.tracer(0)

# 2. Instructions
instr = turtle.Turtle()
instr.color("white")
instr.penup()
instr.hideturtle()
instr.goto(0, 0)
instr.write("HOW TO PLAY\n\nUp/Down Arrows to Move\n\nBlue [ ] = Speed Up\nGreen O = Big Paddle\nRed <3 = +5 Points\n\nClick Screen to Start", 
            align="center", font=("Courier", 18, "bold"))

# 3. Game Objects
paddle_a = turtle.Turtle()
paddle_a.shape("square")
paddle_a.color("cyan")
paddle_a.shapesize(stretch_wid=5, stretch_len=1)
paddle_a.penup()
paddle_a.goto(-350, 0)

paddle_b = turtle.Turtle()
paddle_b.shape("square")
paddle_b.color("hotpink")
paddle_b.shapesize(stretch_wid=5, stretch_len=1)
paddle_b.penup()
paddle_b.goto(350, 0)

ball = turtle.Turtle()
ball.shape("circle")
ball.color("white")
ball.penup()
ball.goto(0, 0)
ball.dx = 0.25
ball.dy = 0.25

# TRAIL SETUP
trails = []
for _ in range(10): # 10 segments for the trail
    t = turtle.Turtle()
    t.shape("circle")
    t.color("gray")
    t.penup()
    t.hideturtle()
    trails.append(t)

# Power-Ups
def create_powerup(shape, color, pos):
    p = turtle.Turtle()
    p.shape(shape)
    p.color(color)
    p.penup()
    p.goto(pos)
    return p

p_speed = create_powerup("square", "blue", (0, 150))
p_size = create_powerup("circle", "green", (0, 0))
p_heart = create_powerup("triangle", "red", (0, -150))
p_heart.setheading(180)

# 4. Settings
score_a = 0
score_b = 0
player_speed = 0.6
ai_speed = 0.22
paddle_a_timer = 0

pen = turtle.Turtle()
pen.color("white")
pen.penup()
pen.hideturtle()
pen.goto(0, 260)
pen.write("Player: 0  AI: 0", align="center", font=("Courier", 24, "bold"))

keys = {"Up": False, "Down": False}
def up_p(): keys["Up"] = True
def up_r(): keys["Up"] = False
def down_p(): keys["Down"] = True
def down_r(): keys["Down"] = False

win.listen()
win.onkeypress(up_p, "Up")
win.onkeyrelease(up_r, "Up")
win.onkeypress(down_p, "Down")
win.onkeyrelease(down_r, "Down")

def start_game(x, y):
    instr.clear()
    game_loop()

# 5. Main Loop
def game_loop():
    global score_a, score_b, paddle_a_timer
    
    while True:
        win.update()

        # Update Trail Positions
        for i in range(len(trails)-1, 0, -1):
            trails[i].goto(trails[i-1].pos())
            trails[i].showturtle()
        trails[0].goto(ball.pos())
        trails[0].showturtle()

        # Paddle Size Timer
        if time.time() < paddle_a_timer:
            paddle_a.shapesize(stretch_wid=10, stretch_len=1)
        else:
            paddle_a.shapesize(stretch_wid=5, stretch_len=1)

        # Movement
        if keys["Up"] and paddle_a.ycor() < 250:
            paddle_a.sety(paddle_a.ycor() + player_speed)
        if keys["Down"] and paddle_a.ycor() > -250:
            paddle_a.sety(paddle_a.ycor() - player_speed)

        ball.setx(ball.xcor() + ball.dx)
        ball.sety(ball.ycor() + ball.dy)

        # Bounces
        if ball.ycor() > 290 or ball.ycor() < -290:
            ball.dy *= -1

        # Power-Up Hits
        if ball.distance(p_speed) < 25:
            ball.dx *= 1.5
            p_speed.goto(1000, 1000)

        if ball.distance(p_size) < 25:
            paddle_a_timer = time.time() + 10
            p_size.goto(1000, 1000)

        if ball.distance(p_heart) < 25:
            if ball.dx > 0: score_a += 5
            else: score_b += 5
            pen.clear()
            pen.write(f"Player: {score_a}  AI: {score_b}", align="center", font=("Courier", 24, "bold"))
            p_heart.goto(1000, 1000)

        # AI
        if ball.xcor() > 0:
            if paddle_b.ycor() < ball.ycor() - 10: paddle_b.sety(paddle_b.ycor() + ai_speed)
            elif paddle_b.ycor() > ball.ycor() + 10: paddle_b.sety(paddle_b.ycor() - ai_speed)

        # Scoring & Reset
        if ball.xcor() > 390 or ball.xcor() < -390:
            if ball.xcor() > 390: score_a += 1
            else: score_b += 1
            ball.goto(0, 0)
            ball.dx = 0.25 if ball.dx < 0 else -0.25
            ball.dy = 0.25
            pen.clear()
            pen.write(f"Player: {score_a}  AI: {score_b}", align="center", font=("Courier", 24, "bold"))
            # Reset Power-Ups
            p_speed.goto(0, random.randint(-200, 200))
            p_size.goto(0, random.randint(-200, 200))
            p_heart.goto(0, random.randint(-200, 200))

        # Paddle Collisions
        if (ball.xcor() > 340 and ball.xcor() < 350) and (ball.ycor() < paddle_b.ycor() + 50 and ball.ycor() > paddle_b.ycor() - 50):
            ball.setx(340)
            ball.dx *= -1
        if (ball.xcor() < -340 and ball.xcor() > -350) and (ball.ycor() < paddle_a.ycor() + 100 and ball.ycor() > paddle_a.ycor() - 100):
            ball.setx(-340)
            ball.dx *= -1

win.onclick(start_game)
win.mainloop()
