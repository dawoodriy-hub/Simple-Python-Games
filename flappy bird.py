import turtle
import random
import time

# 1. Setup the Screen
win = turtle.Screen()
win.title("Flappy Bird: Memory-Only Edition")
win.bgcolor("#87CEEB")
win.setup(width=500, height=700)
win.tracer(0)

# --- HIGH SCORE (Resetting version) ---
high_score = 0 # This will reset to 0 every time you close the game

# 2. Game Objects
bird = turtle.Turtle()
bird.shape("circle"); bird.color("yellow"); bird.penup()

eye = turtle.Turtle(); eye.shape("circle"); eye.color("white"); eye.shapesize(0.5); eye.penup()
pupil = turtle.Turtle(); pupil.shape("circle"); pupil.color("black"); pupil.shapesize(0.2); pupil.penup()
beak = turtle.Turtle(); beak.shape("triangle"); beak.color("orange"); beak.shapesize(0.5); beak.penup()

particles = []
def create_particles(x, y):
    for _ in range(5):
        p = turtle.Turtle()
        p.shape("circle"); p.shapesize(0.3); p.color("yellow"); p.penup()
        p.goto(x, y)
        p.dx = random.uniform(-4, -1)
        p.dy = random.uniform(-2, 2)
        p.life = 15
        particles.append(p)

pipes = []
score = 0
pen = turtle.Turtle(); pen.hideturtle(); pen.penup(); pen.color("white")

# 3. Controls
def jump(x=0, y=0):
    bird.dy = current_jump
    create_particles(bird.xcor(), bird.ycor())

win.listen()
win.onkeypress(jump, "space")
win.onkeypress(jump, "Up")
win.onclick(jump)

def create_pipe():
    y_pos = random.randint(-150, 150)
    t = turtle.Turtle(); t.shape("square"); t.color("green"); t.shapesize(25, 3); t.penup(); t.goto(300, y_pos + 350)
    b = turtle.Turtle(); b.shape("square"); b.color("green"); b.shapesize(25, 3); b.penup(); b.goto(300, y_pos - 350)
    pipes.append([t, b])

# 4. Main Game Loop
while True:
    # Reset Logic
    for p_pair in pipes: p_pair[0].hideturtle(); p_pair[1].hideturtle()
    pipes.clear()
    for p in particles: p.hideturtle()
    particles.clear()
    
    bird.goto(-100, 0); bird.dy = 0; score = 0
    current_pipe_speed = 4
    current_gravity = -0.3
    current_jump = 6
    
    for i in range(3, 0, -1):
        pen.clear(); pen.goto(0, 0)
        pen.write(f"{i}", align="center", font=("Arial", 60, "bold"))
        win.update(); time.sleep(1)
    pen.clear(); win.update()

    game_running = True
    last_pipe_time = time.time()
    
    while game_running:
        win.update(); time.sleep(0.01)

        # Update Face
        bx, by = bird.xcor(), bird.ycor()
        eye.goto(bx + 10, by + 5); pupil.goto(bx + 12, by + 5)
        beak.goto(bx + 15, by - 5); beak.setheading(0)

        # Physics
        bird.dy += current_gravity
        bird.sety(bird.ycor() + bird.dy)

        # Screen Wrap
        if bird.ycor() > 350: bird.sety(-340)
        elif bird.ycor() < -350: bird.sety(340)

        # Particles
        for p in particles[:]:
            p.setx(p.xcor() + p.dx); p.sety(p.ycor() + p.dy); p.life -= 1
            if p.life <= 0: p.hideturtle(); particles.remove(p)

        # Pipe Spawning
        spawn_delay = max(0.8, 1.5 - (score * 0.05))
        if time.time() - last_pipe_time > spawn_delay:
            create_pipe(); last_pipe_time = time.time()

        for p_pair in pipes:
            p_pair[0].setx(p_pair[0].xcor() - current_pipe_speed)
            p_pair[1].setx(p_pair[1].xcor() - current_pipe_speed)

            # Collision
            if bird.xcor() + 10 > p_pair[0].xcor() - 30 and bird.xcor() - 10 < p_pair[0].xcor() + 30:
                if bird.ycor() + 10 > p_pair[0].ycor() - 250 or bird.ycor() - 10 < p_pair[1].ycor() + 250:
                    game_running = False

            # Scoring & Speed Up
            if p_pair[0].xcor() < -100 and not hasattr(p_pair[0], 'scored'):
                score += 1; p_pair[0].scored = True
                current_pipe_speed += 0.2
                current_gravity -= 0.01
                if score > high_score: high_score = score
                pen.clear(); pen.goto(0, 300)
                pen.write(f"Score: {score}  Best: {high_score}", align="center", font=("Arial", 20, "bold"))

        # Cleanup
        if len(pipes) > 0 and pipes[0][0].xcor() < -300:
            old = pipes.pop(0)
            old[0].hideturtle(); old[1].hideturtle()

    pen.goto(0, 0); pen.color("red")
    pen.write("GAME OVER!", align="center", font=("Arial", 40, "bold"))
    win.update(); time.sleep(2); pen.color("white")
