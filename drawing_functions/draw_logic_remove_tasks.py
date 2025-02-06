from config import *

from drawing_functions.draw_rounded_button import draw_rounded_button
from drawing_functions.draw_spoons import draw_spoons

import pygame

def draw_remove_tasks(screen, type, task_list, buttons, spoons, scroll_offset,
                        remove_tasks_task_color, icon_image, spoon_name,
                        folder_one, folder_two, folder_three, folder_four, folder_five, folder_six):
    global hub_buttons_showing, scroll_last_update_time
    current_time = pygame.time.get_ticks() / 1000  # Current time in seconds
    scroll_multiplier = 1
    scroll_limit = len(task_list) - 8

    draw_rounded_button(screen, hub_toggle, LIGHT_GRAY, BLACK, 0, 2)# type: ignore
    pygame.draw.rect(screen, BLACK, hub_menu1)# type: ignore
    pygame.draw.rect(screen, BLACK, hub_menu2)# type: ignore
    pygame.draw.rect(screen, BLACK, hub_menu3)# type: ignore

    draw_spoons(screen, spoons, icon_image, spoon_name)

    if type == "Homework":
        title = font.render(f"What {folder_one} tasks have you completed?", True, BLACK)# type: ignore
    elif type == "Chores":
        title = font.render(f"What {folder_two} tasks have you completed?", True, BLACK)# type: ignore
    elif type == "Work":
        title = font.render(f"What {folder_three} tasks have you completed?", True, BLACK)# type: ignore
    elif type == "Misc":
        title = font.render(f"What {folder_four} tasks have you completed?", True, BLACK)# type: ignore
    screen.blit(title, (50, 65))
    buttons.clear()  # Clear the list before adding new buttons

    # Check if there are more than 8 tasks
    if len(task_list) > 8:
        # Draw scroll bar and buttons
        scroll_bar_inner_body = pygame.Rect(
            15, 136 + int((378 - int(378 * (8 / len(task_list)))) * (scroll_offset / max(1, len(task_list) - 8))),
            20, int(378 * (8 / len(task_list))) if len(task_list) > 8 else 378
        )
        draw_rounded_button(screen, scroll_bar_body, LIGHT_GRAY, BLACK, 0, 1)# type: ignore
        draw_rounded_button(screen, scroll_bar_up_button, LIGHT_GRAY, BLACK, 0, 0)# type: ignore
        draw_rounded_button(screen, scroll_bar_down_button, LIGHT_GRAY, BLACK, 0, 0)# type: ignore
        draw_rounded_button(screen, scroll_bar_inner_body, DARK_GRAY, DARK_GRAY, 0, 0)# type: ignore
        pygame.draw.polygon(screen, BLACK, [(20, 120), (25, 110), (30, 120)])# type: ignore
        pygame.draw.polygon(screen, BLACK, [(20, 530), (25, 540), (30, 530)])# type: ignore

    # Limit the task list to show 8 tasks starting from the scroll_offset
    visible_tasks = task_list[scroll_offset:scroll_offset + 8]

    for i, (task, spoons_needed, done, days, date, start_time, end_time) in enumerate(visible_tasks):
        button = pygame.Rect(100, 100 + i * 60, 600, 50)
        draw_rounded_button(screen, button, remove_tasks_task_color if spoons >= spoons_needed else LIGHT_GRAY, BLACK, 15)# type: ignore
        task_text = font.render(f"{task}:", True, BLACK)# type: ignore
        screen.blit(task_text, (button.x + 10, button.y + 15))

        # Draw spoon images
        for j in range(spoons_needed):
            screen.blit(spoon_bracket_image, (button.x + j * 40 + 310, button.y + 10))
            if done == "✅":
                screen.blit(icon_image, (button.x + j * 40 + 310, button.y + 10))

        buttons.append((button, scroll_offset + i))  # Map button to actual task index in task_list


def logic_remove_tasks(task_list, buttons, event):
    global scroll_offset, scroll_last_update_time
    current_time = pygame.time.get_ticks() / 1000  # Current time in seconds
    task_removed = False

    if event.type == pygame.MOUSEBUTTONDOWN:
        if event.button == 1:
            for button, index in buttons:
                if button.collidepoint(event.pos):
                    task_list.pop(index)  # Remove the task from the list
                    task_removed = True  # Flag that a task was removed
                    # Adjust scroll_offset if needed
                    if scroll_offset > 0 and len(task_list) <= scroll_offset + 8:
                        scroll_offset -= 1
                    break  # Exit loop after removing the task

        if task_removed:
            # Rebuild the buttons list after a task is removed
            buttons.clear()
            visible_tasks = task_list[scroll_offset:scroll_offset + 8]
            for i, _ in enumerate(visible_tasks):
                # Recreate the button positions for each task
                button = pygame.Rect(100, 100 + i * 60, 600, 50)
                buttons.append((button, scroll_offset + i))

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
