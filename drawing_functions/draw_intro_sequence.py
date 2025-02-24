import pygame
import random
import math
from config import *
from drawing_functions.draw_rounded_button import draw_rounded_button

# Define widths
letter_width = 80  # Approximate width of each normal letter
exclamation_width = 20  # Exclamation is 1/4 the width of a letter
degrees = 55 # Amount that the spoons change angle at when they come in.

# Extract letters
letters = [spoons_logo.subsurface((i * letter_width, 0, letter_width, 80)) for i in range(6)]

# Correct exclamation mark position
exclamation_x = 6 * letter_width  # Start position of the exclamation mark
exclamation_mark = spoons_logo.subsurface((exclamation_x, 0, exclamation_width, 80))

# Function to create a glow surface with a radial gradient
def create_glow_surface(radius, color):
    """
    Create a glow surface with a radial gradient.
    """
    glow_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
    for i in range(radius, 0, -1):
        alpha = int(255 * (1- (i / radius)))  # Decrease alpha as radius decreases
        glow_color = (*color[:3], alpha)  # Set alpha for the current circle
        pygame.draw.circle(glow_surface, glow_color, (radius, radius), i)
    return glow_surface

def draw_intro_sequence(screen, clock):
    screen_width, screen_height = screen.get_size()
    background_color = (30, 30, 30)
    confetti_colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]

    # Initialize game state
    spoon_bar = []
    task_spoons = []
    tasks_rows = {}
    task_rows_full = [
        {"task1": ["Finish Homework", 3, pygame.Rect(100, 300, 600, 50)]},
        {"task2": ["Finish Chores", 4, pygame.Rect(100, 360, 600, 50)]},
        {"task3": ["Finish Work", 3, pygame.Rect(100, 420, 600, 50)]}
    ]
    confetti_particles = []
    task_spoons_placed = {"task1": 0, "task2": 0, "task3": 0}
    
    intro_running = True
    spoon_count = 0
    task_progress = 0
    tasks_shown = 0
    confetti_playing = False
    moving_spoon = None
    target_pos = None
    next_spoon_time = pygame.time.get_ticks()  # Timer for adding spoons
    step1_complete = False  # Track if all spoons are in place

    # Confetti generator
    def generate_confetti():
        return [{
            "x": random.randint(screen_width // 2 - 50, screen_width // 2 + 50),
            "y": screen_height // 2 - 50,
            "dx": random.uniform(-2, 2),
            "dy": random.uniform(-5, -1),
            "color": random.choice(confetti_colors),
            "size": random.randint(3, 6),
            "lifetime": 100
        } for _ in range(40)]

    pygame.time.delay(200)

    while intro_running:
        screen.fill(background_color)
        current_time = pygame.time.get_ticks()

        # --- STEP 1: Build the spoon bar with animation ---
        if spoon_count < 10:
            if current_time >= next_spoon_time:
                # Calculate delay for next spoon
                delay = 4 * (10 + 0.5 * (spoon_count ** 2))
                next_spoon_time = current_time + delay

                # Target position for the spoon
                target_x = 100 + spoon_count * 60
                target_y = screen_height - 400

                # Calculate angle for the current spoon
                if spoon_count == 0:
                    # First spoon: random angle
                    base_angle = random.uniform(0, 2 * math.pi)
                else:
                    # Subsequent spoons: 30 degrees clockwise from the previous spoon
                    base_angle = spoon_bar[-1]["angle"] + (math.pi / 180) * degrees

                # Ensure the angle stays within 0 to 2*pi
                base_angle = base_angle % (2 * math.pi)

                # Calculate start position using trigonometry
                distance = max(screen_width, screen_height)  # Start far enough to ensure off-screen
                start_x = target_x + distance * math.cos(base_angle)
                start_y = target_y + distance * math.sin(base_angle)

                # Add spoon with animation properties
                spoon_bar.append({
                    "start_x": start_x,
                    "start_y": start_y,
                    "target_x": target_x,
                    "target_y": target_y,
                    "start_time": current_time,
                    "duration": 500,  # Animation duration in ms
                    "glow_radius": 25,
                    "x": start_x,
                    "y": start_y,
                    "angle": base_angle  # Store the angle for the next spoon
                })
                spoon_count += 1

        # Update spoon positions
        for spoon in spoon_bar:
            elapsed = current_time - spoon["start_time"]
            progress = min(elapsed / spoon["duration"], 1.0)
            spoon["x"] = spoon["start_x"] + (spoon["target_x"] - spoon["start_x"]) * progress
            spoon["y"] = spoon["start_y"] + (spoon["target_y"] - spoon["start_y"]) * progress

        # Check if all spoons have arrived
        if spoon_count == 10 and not step1_complete:
            step1_complete = all(
                (current_time - spoon["start_time"]) >= spoon["duration"] 
                for spoon in spoon_bar
            )

        # Draw spoon bar
        for spoon in spoon_bar:
            glow_surface = create_glow_surface(spoon["glow_radius"], (255, 255, 150))
            screen.blit(glow_surface, (spoon["x"] - spoon["glow_radius"], spoon["y"] - spoon["glow_radius"]))
            screen.blit(icon_image, (spoon["x"] - 15, spoon["y"] - 15))

        # --- STEP 2: Animate tasks appearing ---
        if spoon_count == 10 and tasks_shown < 3 and step1_complete:
            task_dict = task_rows_full[tasks_shown]  # Get the current task
            key, value = next(iter(task_dict.items()))  # Extract task details

            # Initialize task with 0 width
            task_rect = value[2]
            tasks_rows[key] = [value[0], value[1], pygame.Rect(task_rect.x, task_rect.y, 0, task_rect.height)]

            # Animate task width expansion
            full_width = task_rect.width
            animation_time = 0.5  # Time in seconds for full expansion
            start_time = pygame.time.get_ticks()

            while True:
                elapsed_time = (pygame.time.get_ticks() - start_time) / 1000.0  # Convert to seconds
                t = min(elapsed_time / animation_time, 1)  # Normalize to range [0,1]
                animated_width = int(full_width * t)  # Lerp from 0 to full width

                screen.fill(background_color)  # Clear screen

                # Redraw spoon bar
                for spoon in spoon_bar:
                    glow_surface = create_glow_surface(spoon["glow_radius"], (255, 255, 150))
                    screen.blit(glow_surface, (spoon["x"] - spoon["glow_radius"], spoon["y"] - spoon["glow_radius"]))
                    screen.blit(icon_image, (spoon["x"] - 15, spoon["y"] - 15))

                # Redraw tasks
                for k, v in tasks_rows.items():
                    task_r = v[2]
                    if k == key:
                        task_r.width = animated_width  # Expand the task dynamically
                    draw_rounded_button(screen, task_r, (0, 149, 182), (0, 0, 0), 15)
                    task_text = font.render(v[0], True, (0, 0, 0))
                    screen.blit(task_text, (task_r.x + 10, task_r.y + 15))
                    for j in range(v[1]):  # Draw brackets
                        screen.blit(spoon_bracket_image, (task_r.x + j * 40 + 310, task_r.y + 10))

                pygame.display.flip()
                clock.tick(60)  # Keep the animation smooth

                if t >= 1:  # Break the loop when animation is complete
                    break

            tasks_shown += 1
            pygame.time.delay(300)  # Small delay before next task starts animating

        # --- STEP 3: Move spoons into tasks ---
        if ((spoon_count == 10 and task_progress < 10 and tasks_shown == 3) or task_progress == 10) and step1_complete:

            # Redraw tasks
            for k, v in tasks_rows.items():
                task_r = v[2]
                if k == key:
                    task_r.width = animated_width  # Expand the task dynamically
                draw_rounded_button(screen, task_r, (0, 149, 182), (0, 0, 0), 15)
                task_text = font.render(v[0], True, (0, 0, 0))
                screen.blit(task_text, (task_r.x + 10, task_r.y + 15))
                for j in range(v[1]):  # Draw brackets
                    screen.blit(spoon_bracket_image, (task_r.x + j * 40 + 310, task_r.y + 10))

            if not moving_spoon:  # Start moving a new spoon
                for key in tasks_rows:
                    task_data = tasks_rows[key]
                    needed = task_data[1] - task_spoons_placed[key]
                    if needed > 0 and spoon_bar:
                        moving_spoon = spoon_bar.pop()
                        task_x = task_data[2].x
                        target_pos = (
                            task_x + (task_spoons_placed[key]) * 40 + 310,
                            task_data[2].y + 10
                        )
                        break

            if moving_spoon:  # Update spoon position
                # Move horizontally
                if moving_spoon["x"] > target_pos[0]:
                    moving_spoon["x"] -= 10
                elif moving_spoon["x"] < target_pos[0]:
                    moving_spoon["x"] += 10

                # Move vertically
                if moving_spoon["y"] < target_pos[1]:
                    moving_spoon["y"] += 10

                # Check if spoon reached target
                if (abs(moving_spoon["x"] - target_pos[0]) < 5) and (abs(moving_spoon["y"] - target_pos[1]) < 5):
                    task_spoons.append({"x": target_pos[0], "y": target_pos[1]})
                    task_spoons_placed[key] += 1
                    task_progress += 1
                    moving_spoon = None
                    target_pos = None

                    # TRIGGER CONFETTI AT MILESTONES
                    if task_progress in [3, 7]:
                        confetti_particles = generate_confetti()
                        confetti_playing = True

        # --- Draw moving spoon with glow ---
        if moving_spoon:
            glow_surface = create_glow_surface(moving_spoon["glow_radius"], (255, 255, 150))
            screen.blit(glow_surface, (moving_spoon["x"] - moving_spoon["glow_radius"], moving_spoon["y"] - moving_spoon["glow_radius"]))
            screen.blit(icon_image, (moving_spoon["x"] - 15, moving_spoon["y"] - 15))

        # --- Draw placed spoons ---
        for spoon in task_spoons:
            screen.blit(icon_image, (spoon["x"], spoon["y"]))

        # --- Confetti animation ---
        if confetti_playing:
            for particle in confetti_particles:
                particle["x"] += particle["dx"]
                particle["y"] += particle["dy"]
                particle["dy"] += 0.2
                particle["lifetime"] -= 1
                pygame.draw.circle(
                    screen, particle["color"],
                    (int(particle["x"]), int(particle["y"])),
                    particle["size"]
                )
            confetti_particles = [p for p in confetti_particles if p["lifetime"] > 0]
            if not confetti_particles:
                confetti_playing = False

        # --- Exit condition ---
        if task_progress == 10 and not confetti_playing:
            # Animate logo appearance
            for i in range(7):  # 6 letters + 1 exclamation mark

                # Draw each letter up to the current index
                for j in range(i + 1):  # Include the current index
                    if j < 6:  # First six letters
                        screen.blit(letters[j], (screen_width // 2 - 250 + j * letter_width, screen_height // 2 - 200))
                    else:  # The exclamation mark appears at the end
                        screen.blit(exclamation_mark, (screen_width // 2 - 250 + 6 * letter_width, screen_height // 2 - 200))

                pygame.display.flip()
                pygame.time.delay(300)  # Delay for each letter appearing

            # End the intro sequence
            pygame.time.delay(500)
            intro_running = False
            
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN or event.type == pygame.QUIT or event.type == pygame.MOUSEBUTTONDOWN:
                intro_running = False

        pygame.display.flip()
        clock.tick(50)