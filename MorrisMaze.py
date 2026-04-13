from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import time
import random

app = Ursina()

# --- Experiment Settings ---
MAX_TRIALS = 25
MAP_SIZE = 25
GOAL_POS = Vec3(-2, 0.5, 0)
trial_results = []
k_presses = []
current_trial_k_count = 0
current_trial = 1
start_time = 0
force_visible = False

# --- Preplanned Spawn Points ---
SPAWN_POINTS = [
    Vec3(9, 2, 9), Vec3(0, 2, 0), Vec3(-8, 2, 8),
    Vec3(8, 2, -8), Vec3(-5, 2, -5)
]
random.seed(42)
while len(SPAWN_POINTS) < MAX_TRIALS:
    SPAWN_POINTS.append(Vec3(random.uniform(-9, 9), 2, random.uniform(-9, 9)))

# --- Environment Setup ---
Sky(color=color.light_gray)

# Ground with Grid
ground = Entity(
    model='quad',
    collider='box',
    scale=MAP_SIZE,
    rotation_x=90,
    texture='white_cube',
    texture_scale=(MAP_SIZE, MAP_SIZE),  # This creates the grid effect
    color=color.white
)

# Colored Walls
wall_thickness, wall_height = 0.01, 15
walls = [
    (Vec3(-MAP_SIZE / 2, 1.5, 0), (wall_thickness, wall_height, MAP_SIZE), color.white),
    (Vec3(MAP_SIZE / 2, 1.5, 0), (wall_thickness, wall_height, MAP_SIZE), color.white),
    (Vec3(0, 1.5, MAP_SIZE / 2), (MAP_SIZE, wall_height, wall_thickness), color.black),
    (Vec3(0, 1.5, -MAP_SIZE / 2), (MAP_SIZE, wall_height, wall_thickness), color.black)
]
for pos, scl, clr in walls:
    Entity(model='cube', collider='box', position=pos, scale=scl, color=clr)

goal = Entity(model='cube', color=color.green, scale=1, position=GOAL_POS, collider='box')

player = FirstPersonController()
player.cursor.color = color.white

feedback_text = Text(text='', origin=(0, -15), color=color.yellow, scale=2)


def spawn_player():
    global current_trial_k_count, force_visible
    player.position = SPAWN_POINTS[current_trial - 1]
    current_trial_k_count = 0
    force_visible = False

    msg = "Practice Round" if current_trial == 1 else f"Trial {current_trial} Started!"
    feedback_text.text = msg
    invoke(setattr, feedback_text, 'text', '', delay=1.5)


def finish_experiment():
    if not player.enabled: return
    player.enabled = False
    mouse.locked = False
    goal.enabled = False

    status = "EXPERIMENT COMPLETE" if len(trial_results) >= (MAX_TRIALS - 1) else "EXPERIMENT TERMINATED"
    results_summary = f"{status}\n(T1 Excluded)\n\n"

    for i in range(len(trial_results)):
        t_num = i + 2
        results_summary += f"T{t_num}: {trial_results[i]:.2f}s (K:{k_presses[i]})  "
        if (i + 1) % 3 == 0: results_summary += "\n"

    Text(text=results_summary, origin=(0, 0), scale=1, background=True)


def input(key):
    global current_trial_k_count, force_visible

    if key == 'q' or key == 'escape':
        finish_experiment() if trial_results else application.quit()

    if key == 'k':
        current_trial_k_count += 1
        force_visible = True
        print(f"K pressed! Total this trial: {current_trial_k_count}")


# Initial Start
spawn_player()
start_time = time.time()


def update():
    global start_time, current_trial

    if not player.enabled: return

    # Visibility: Visible for Trials 1-3 OR if K is pressed
    goal.visible = True if (current_trial <= 3 or force_visible) else False

    if (player.position - goal.position).length() < 1.5:
        end_time = time.time()

        if current_trial > 1:
            trial_results.append(end_time - start_time)
            k_presses.append(current_trial_k_count)
            print(f"Trial {current_trial} cleared. K-presses: {current_trial_k_count}")

        if current_trial < MAX_TRIALS:
            current_trial += 1
            spawn_player()
            start_time = time.time()
        else:
            finish_experiment()


app.run()