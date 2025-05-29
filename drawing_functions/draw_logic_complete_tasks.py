from config import *

from drawing_functions.draw_rounded_button import draw_rounded_button

import pygame
import time
import random
from datetime import datetime, timedelta
"""
Summary:
    Draws the completed tasks interface on the given screen, including task details and scroll functionality.

Parameters:
    screen (pygame.Surface): The surface on which the completed tasks interface will be drawn.
    type (str): The type of tasks being displayed (e.g., "homework", "chores").
    task_list (list): List of tasks to be displayed.
    buttons (list): List to store button objects for task interaction.
    spoons (int): The current number of spoons.
    scroll_offset (int): The current scroll offset for the task list.
    complete_tasks_task_color (tuple): Color for the task buttons. 

Returns:
    No returns.
"""

def draw_complete_tasks(screen, type, task_list, buttons, spoons, scroll_offset,
                        complete_tasks_task_color, icon_image, spoon_name,
                        folder_one, folder_two, folder_three, folder_four, folder_five, folder_six):
    global hub_buttons_showing, done, scroll_last_update_time
    scroll_limit = len(task_list) - 8
    current_time = pygame.time.get_ticks() / 1000  # Current time in seconds

    draw_rounded_button(screen, hub_toggle, LIGHT_GRAY, BLACK, 0, 2)# type: ignore
    pygame.draw.rect(screen, BLACK, hub_menu1)# type: ignore
    pygame.draw.rect(screen, BLACK, hub_menu2)# type: ignore
    pygame.draw.rect(screen, BLACK, hub_menu3)# type: ignore
    if len(task_list) > 8:
        scroll_multiplier = 1
        scroll_limit = len(task_list) - 8
    else:
        scroll_multiplier = 0
        scroll_limit = 0

    # Sorts task_list so that incomplete tasks come before completed tasks
    for i in range(len(task_list)):
        for j in range(len(task_list) - 1 - i):
            if task_list[j][2] == "✅" and task_list[j + 1][2] == "❌":
                # Swap the completed task with the incomplete task
                task_list[j], task_list[j + 1] = task_list[j + 1], task_list[j]


    # Check if there are more than 8 tasks
    if len(task_list) > 8:
        # Draw scroll bar and buttons
        scroll_bar_inner_body = pygame.Rect(
        15, 136 + int((378 - int(378 * (8 / len(task_list)))) * (scroll_offset / max(1, len(task_list) - 8))),
        20, int(378 * (8 / len(task_list))) if len(task_list) > 8 else 378)
        draw_rounded_button(screen, scroll_bar_body, LIGHT_GRAY, BLACK, 0, 1)# type: ignore
        draw_rounded_button(screen, scroll_bar_up_button, LIGHT_GRAY, BLACK, 0, 0)# type: ignore
        draw_rounded_button(screen, scroll_bar_down_button, LIGHT_GRAY, BLACK, 0, 0)# type: ignore
        draw_rounded_button(screen, scroll_bar_inner_body, DARK_GRAY, DARK_GRAY, 0, 0)# type: ignore
        pygame.draw.polygon(screen, BLACK, [(20, 120), (25, 110), (30, 120)])# type: ignore
        pygame.draw.polygon(screen, BLACK, [(20, 530), (25, 540), (30, 530)])# type: ignore
    else:
        scroll_offset = 0

    if type == "Homework":
        title = font.render(f"What {folder_one} tasks have you completed?", True, BLACK)# type: ignore
    elif type == "Chores":
        title = font.render(f"What {folder_two} tasks have you completed?", True, BLACK)# type: ignore
    elif type == "Work":
        title = font.render(f"What {folder_three} tasks have you completed?", True, BLACK)# type: ignore
    elif type == "Misc":
        title = font.render(f"What {folder_four} tasks have you completed?", True, BLACK)# type: ignore
    elif type == "Exams":
        title = font.render(f"What {folder_five} tasks have you completed?", True, BLACK)# type: ignore
    elif type == "Projects":
        title = font.render(f"What {folder_six} tasks have you completed?", True, BLACK)# type: ignore
    screen.blit(title, (50, 65))
    buttons.clear()
    mouse_pos = pygame.mouse.get_pos()

    # Limit the task list to show 8 tasks starting from the scroll_offset
    visible_tasks = task_list[scroll_offset:scroll_offset + 8]

    for i, (task, spoons_needed, done, days, date, start_time, end_time) in enumerate(visible_tasks):
        button = pygame.Rect(100, 100 + i * 60, 600, 50)
        draw_rounded_button(screen, button, complete_tasks_task_color if spoons >= spoons_needed else LIGHT_GRAY, BLACK, 15)# type: ignore
        task_text = font.render(f"{task}:", True, BLACK)# type: ignore
        screen.blit(task_text, (button.x + 10, button.y + 15))

        # Show warnings based on days left
        if days <= 0:
            warning_text = font.render("!!!!!", True, BLACK)# type: ignore
            screen.blit(warning_text, (button.x - 50, button.y + 15))
        elif days <= 1:
            warning_text = font.render("!!!", True, BLACK)# type: ignore
            screen.blit(warning_text, (button.x - 30, button.y + 15))
        elif days <= 3:
            warning_text = font.render("!!", True, BLACK)# type: ignore
            screen.blit(warning_text, (button.x - 20, button.y + 15))
        elif days <= 7:
            warning_text = font.render("!", True, BLACK)# type: ignore
            screen.blit(warning_text, (button.x - 10, button.y + 15))

        # Draw spoon images
        if spoons >= spoons_needed:
            for j in range(spoons_needed):
                screen.blit(spoon_bracket_image, (button.x + j * 40 + 310, button.y + 10))
                if done == "✅":
                    screen.blit(icon_image, (button.x + j * 40 + 310, button.y + 10))
        else:
            for j in range(spoons_needed):
                screen.blit(spoon_bracket_image, (button.x + j * 40 + 310, button.y + 10))
                if done == "✅":
                    screen.blit(icon_image, (button.x + j * 40 + 310, button.y + 10))

        buttons.append((button, scroll_offset + i))  # Map button to actual task index in task_list

    # Text for days left
    for button, index in buttons:
        hover_text = font.render(f"{task_list[index][3]} days", True, BLACK)# type: ignore
        screen.blit(hover_text, (button.x + button.width + 10, button.y))
        screen.blit(font.render("left", True, BLACK), (button.x + button.width + 10, button.y + 25))# type: ignore

"""
Summary:
    Handles the logic for interacting with the completed tasks interface, including task completion and scrolling.

Parameters:
    task_list (list): List of tasks to be displayed.
    buttons (list): List of button objects for task interaction.
    event (pygame.event.Event): The event object containing information about the user input.
    spoons (int): The current number of spoons.

Returns:
    tuple: Updated task_list and spoons.
"""

from datetime import datetime, timedelta

...

def logic_complete_tasks(task_list, buttons, event, spoons, streak_dates, streak_task_completed):
    global scroll_offset, scroll_last_update_time, confetti_particles
    current_time = pygame.time.get_ticks() / 1000  # Current time in seconds
    task_completed = False

    today = datetime.now()
    today_str = today.strftime("%Y-%m-%d")
    yesterday_str = (today - timedelta(days=1)).strftime("%Y-%m-%d")

    if event.type == pygame.MOUSEBUTTONDOWN:
        if event.button == 1:
            for button, index in buttons:
                if button.collidepoint(event.pos) and task_list[index][2] == "❌":
                    if spoons >= task_list[index][1]:
                        task_data = list(task_list[index])
                        task_data[2] = '✅'
                        task_list[index] = tuple(task_data)
                        spoons -= task_list[index][1]
                        task_completed = True

                        # Streak logic
                        if not streak_task_completed:
                            streak_task_completed = True
                            if not streak_dates:
                                streak_dates.append([today_str, today_str])
                            else:
                                start_date, end_date = streak_dates[-1]
                                if today_str > end_date:
                                    if end_date == yesterday_str:
                                        streak_dates[-1][1] = today_str
                                    else:
                                        streak_dates.append([today_str, today_str])

                        for _ in range(30):
                            confetti_particles.append(ConfettiParticle(-50, 400, "left"))
                            confetti_particles.append(ConfettiParticle(850, 400, "right"))
                        break

    # Handle scrolling logic
    if scroll_bar_up_button.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
        # Scroll up if enough time has passed since the last scroll
        if current_time - scroll_last_update_time >= scroll_update_interval and scroll_offset > 0:
            scroll_offset -= 1
            scroll_last_update_time = current_time  # Update the last update time
    elif scroll_bar_down_button.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
        # Scroll down if enough time has passed since the last scroll
        if current_time - scroll_last_update_time >= scroll_update_interval and scroll_offset < len(task_list) - 8:
            scroll_offset += 1
            scroll_last_update_time = current_time  # Update the last update time

    return task_completed, spoons, confetti_particles, streak_dates


class ConfettiParticle:
    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.vx = random.uniform(.5, 1.5) * (-1 if direction == "right" else 1) * 7.5
        self.vy = random.uniform(-1.5, -.7) * 7.55
        self.color = random.choice([(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255)])
        self.lifetime = 100  # Controls how long it stays on screen

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.15  # gravity effect
        self.lifetime -= 1  # Reduce lifetime

    def is_alive(self):
        return self.lifetime > 0

    
import time

# Track the start time of confetti
confetti_start_time = None

def update_and_draw_confetti(screen, confetti_particles):
    global confetti_start_time

    if confetti_start_time is None:
        confetti_start_time = time.time()  # Start the timer when confetti begins

    current_time = time.time()

    # Update and draw confetti
    for particle in confetti_particles[:]:  
        particle.update()

        if isinstance(particle.x, (int, float)) and isinstance(particle.y, (int, float)):
            if 0 <= particle.x <= screen.get_width() and 0 <= particle.y <= screen.get_height():
                pygame.draw.circle(screen, particle.color, (int(particle.x), int(particle.y)), 5)

    # Remove expired particles after 3 seconds
    if current_time - confetti_start_time >= 3:
        confetti_particles[:] = [p for p in confetti_particles if p.is_alive()]
        confetti_start_time = None  # Reset timer so the next confetti burst starts fresh