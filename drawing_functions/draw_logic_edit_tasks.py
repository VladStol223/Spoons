from config import *
import pygame
import calendar
from datetime import datetime
from drawing_functions.draw_rounded_button import draw_rounded_button
from drawing_functions.draw_input_box import draw_input_box

# Add these global variables
editing_state = {
    "editing": False,
    "original_task": None,
    "task_index": -1,
    "new_name": "",
    "new_spoons": "",
    "new_month": 1,
    "new_day": 1,
    "days_until_due": 0,
    "new_done_status": "❌"
}

def draw_edit_tasks(screen, spoons, type, task_list, buttons, input_active, scroll_offset, 
                    complete_tasks_task_color, icon_image, spoon_name,
                    folder_one, folder_two, folder_three, folder_four, folder_five, folder_six):
    """ Draws the task editing interface """
    if editing_state["editing"]:
        return draw_editing_interface(screen, spoons, task_list, complete_tasks_task_color, input_active,
                                     icon_image, spoon_name, buttons)
    else:
        return draw_normal_interface(screen, spoons, type, task_list, buttons, scroll_offset,
                                    complete_tasks_task_color, icon_image, spoon_name,
                                    folder_one, folder_two, folder_three, folder_four, 
                                    folder_five, folder_six)

def draw_normal_interface(screen, spoons, type, task_list, buttons, scroll_offset,
                         complete_tasks_task_color, icon_image, spoon_name, *folders):
    scroll_limit = len(task_list) - 8
    current_time = pygame.time.get_ticks() / 1000  # Current time in seconds

    draw_rounded_button(screen, hub_toggle, LIGHT_GRAY, BLACK, 0, 2)# type: ignore
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
        title = font.render(f"What {folder_one} tasks do you want to edit?", True, BLACK)# type: ignore
    elif type == "Chores":
        title = font.render(f"What {folder_two} tasks do you want to edit?", True, BLACK)# type: ignore
    elif type == "Work":
        title = font.render(f"What {folder_three} tasks do you want to edit?", True, BLACK)# type: ignore
    elif type == "Misc":
        title = font.render(f"What {folder_four} tasks do you want to edit?", True, BLACK)# type: ignore
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

def draw_editing_interface(screen, spoons, task_list, complete_tasks_task_color, input_active, icon_image, spoon_name, buttons):
    """ Draws the editing interface for a single task """
    draw_rounded_button(screen, hub_toggle, LIGHT_GRAY, BLACK, 0, 2)  # type: ignore

    # Draw the task being edited
    task = editing_state["original_task"]
    title = font.render(f"How do you want to edit '{editing_state['new_name']}'?", True, BLACK)  # type: ignore
    screen.blit(title, (50, 65))

    button = pygame.Rect(100, 100, 600, 50)
    draw_rounded_button(screen, button, complete_tasks_task_color, BLACK, 15)  # type: ignore
    task_text = font.render(f"{editing_state['new_name']}:", True, BLACK)  # type: ignore
    screen.blit(task_text, (button.x + 10, button.y + 15))

    # Draw spoon images
    for j in range(int(editing_state["new_spoons"])):
        screen.blit(spoon_bracket_image, (button.x + j * 40 + 310, button.y + 10))
        if editing_state["new_done_status"] == "✅":
            screen.blit(icon_image, (button.x + j * 40 + 310, button.y + 10))

    hover_text = font.render(f"{editing_state["days_until_due"]} days", True, BLACK)# type: ignore
    screen.blit(hover_text, (button.x + button.width + 10, button.y))
    screen.blit(font.render("left", True, BLACK), (button.x + button.width + 10, button.y + 25))# type: ignore

    # Draw input boxes
    screen.blit(font.render("Enter new task name:", True, BLACK), (125, 170))# type: ignore
    draw_input_box(screen, edit_task_taskname_input_box, input_active == "name", editing_state["new_name"], GREEN, LIGHT_GRAY)  # type: ignore
    screen.blit(font.render(f"Enter new # of {spoon_name}:", True, BLACK), (117, 270))# type: ignore
    draw_input_box(screen, edit_task_spoon_input_box, input_active == "spoons", editing_state["new_spoons"], GREEN, LIGHT_GRAY)  # type: ignore

    up_arrow = font.render(">", True, BLACK)# type: ignore
    down_arrow = font.render("<", True, BLACK)# type: ignore

    screen.blit(font.render("Enter new due date:", True, BLACK), (495, 170))# type: ignore
    draw_input_box(screen, month_input_box_edit_task, input_active == "month", str(editing_state["new_month"]), GREEN, LIGHT_GRAY)# type: ignore
    draw_input_box(screen, day_input_box_edit_task, input_active == "day", str(editing_state["new_day"]), GREEN, LIGHT_GRAY)# type: ignore
    pygame.draw.rect(screen, done_button_color, month_up_button_edit_task)
    pygame.draw.rect(screen, done_button_color, month_down_button_edit_task)
    pygame.draw.rect(screen, done_button_color, day_up_button_edit_task)
    pygame.draw.rect(screen, done_button_color, day_down_button_edit_task)
    screen.blit(up_arrow, (620, 203))
    screen.blit(down_arrow, (620, 228))
    screen.blit(up_arrow, (715, 203))
    screen.blit(down_arrow, (715, 228))

    screen.blit(font.render("Toggle 'Done' State:", True, BLACK), (500, 270))# type: ignore
    draw_rounded_button(screen, done_toggle_edit_task, GREEN if editing_state["new_done_status"] == "✅" else RED, BLACK, 15)# type: ignore

    # Draw save/cancel buttons
    draw_rounded_button(screen, save_button, (0, 255, 0), BLACK, 15)  # type: ignore
    draw_rounded_button(screen, cancel_button, (255, 0, 0), BLACK, 15)  # type: ignore

    save_text = big_font.render("Save", True, (0, 0, 0))
    cancel_text = big_font.render("Cancel", True, (0, 0, 0))
    screen.blit(save_text, (save_button.x + (save_button.width/2) - (save_text.get_width()/2), save_button.y + (save_button.height/2) - (save_text.get_height()/2)))
    screen.blit(cancel_text, (cancel_button.x + (cancel_button.width/2) - (cancel_text.get_width()/2), cancel_button.y + (cancel_button.height/2) - (cancel_text.get_height()/2)))

def logic_edit_tasks(event, input_active, pos, task_list, buttons, max_days):
    """ Handles logic for task editing """
    if editing_state["editing"]:
        return handle_editing_events(event, input_active, pos, task_list, buttons, max_days)
    else:
        return handle_normal_events(event, pos, task_list, buttons)

def handle_normal_events(event, pos, task_list, buttons):
    """ Handle events in normal (non-editing) mode """
    if event.type == pygame.MOUSEBUTTONDOWN:
        for button, index in buttons:
            if button.collidepoint(pos):
                # Enter editing mode
                editing_state.update({
                    "editing": True,
                    "original_task": task_list[index],
                    "task_index": index,
                    "new_name": task_list[index][0],
                    "new_spoons": str(task_list[index][1]),
                    "new_month": task_list[index][4].month,
                    "new_day": task_list[index][4].day,
                    "days_until_due": task_list[index][3],
                    "new_done_status": task_list[index][2]
                })
                return "name", task_list  # Start with name field active
    return None, task_list  # No input active

def handle_editing_events(event, input_active, pos, task_list, buttons, max_days):
    """ Handle events in editing mode """
    if event.type == pygame.MOUSEBUTTONDOWN:
        # Check for input box clicks
        if edit_task_taskname_input_box.collidepoint(pos):
            input_active = "name"
        elif edit_task_spoon_input_box.collidepoint(pos):
            input_active = "spoons"
        elif save_button.collidepoint(pos):
            # Save changes
            try:
                # Create a new date with the updated month and day
                new_date = datetime(
                    editing_state["original_task"][4].year,  # Keep the original year
                    editing_state["new_month"],  # Updated month
                    editing_state["new_day"]    # Updated day
                )
                # Update days_until_due based on the new date
                days_until_due = (new_date - datetime.now()).days + 1
            except ValueError:
                # If the date is invalid (e.g., February 30), use the original date
                new_date = editing_state["original_task"][4]
                days_until_due = editing_state["original_task"][3] + 1

            task_list[editing_state["task_index"]] = [
                editing_state["new_name"],
                int(editing_state["new_spoons"]),
                editing_state["new_done_status"],
                days_until_due,  # Updated days left
                new_date,  # Updated date
                editing_state["original_task"][5],  # Start time
                editing_state["original_task"][6]   # End time
            ]
            editing_state["editing"] = False
            input_active = None

        elif cancel_button.collidepoint(pos):
            # Cancel changes
            editing_state["editing"] = False
            input_active = None

        # Handle month/day buttons
        elif month_up_button_edit_task.collidepoint(event.pos):
            editing_state["new_month"] = editing_state["new_month"] + 1 if editing_state["new_month"] < 12 else 1
            # Update max_days for the new month
            max_days = calendar.monthrange(datetime.now().year, editing_state["new_month"])[1]
            if editing_state["new_day"] > max_days:
                editing_state["new_day"] = max_days
            # Update days_until_due
            new_date = datetime(datetime.now().year, editing_state["new_month"], editing_state["new_day"])
            editing_state["days_until_due"] = (new_date - datetime.now()).days + 1

        elif month_down_button_edit_task.collidepoint(event.pos):
            editing_state["new_month"] = editing_state["new_month"] - 1 if editing_state["new_month"] > 1 else 12
            # Update max_days for the new month
            max_days = calendar.monthrange(datetime.now().year, editing_state["new_month"])[1]
            if editing_state["new_day"] > max_days:
                editing_state["new_day"] = max_days
            # Update days_until_due
            new_date = datetime(datetime.now().year, editing_state["new_month"], editing_state["new_day"])
            editing_state["days_until_due"] = (new_date - datetime.now()).days + 1

        elif day_up_button_edit_task.collidepoint(event.pos):
            editing_state["new_day"] = editing_state["new_day"] + 1 if editing_state["new_day"] < max_days else 1
            # Update days_until_due
            new_date = datetime(datetime.now().year, editing_state["new_month"], editing_state["new_day"])
            editing_state["days_until_due"] = (new_date - datetime.now()).days + 1

        elif day_down_button_edit_task.collidepoint(event.pos):
            editing_state["new_day"] = editing_state["new_day"] - 1 if editing_state["new_day"] > 1 else max_days
            # Update days_until_due
            new_date = datetime(datetime.now().year, editing_state["new_month"], editing_state["new_day"])
            editing_state["days_until_due"] = (new_date - datetime.now()).days + 1


        # Toggle done status
        elif done_toggle_edit_task.collidepoint(event.pos):
            editing_state["new_done_status"] = "✅" if editing_state["new_done_status"] == "❌" else "❌"

    elif event.type == pygame.KEYDOWN and input_active:
        if input_active == "name":
            if event.key == pygame.K_BACKSPACE:
                editing_state["new_name"] = editing_state["new_name"][:-1]
            else:
                editing_state["new_name"] += event.unicode
        elif input_active == "spoons":
            if event.key == pygame.K_BACKSPACE:
                editing_state["new_spoons"] = editing_state["new_spoons"][:-1]
                if editing_state["new_spoons"] == "":  # If empty, set to 0
                    editing_state["new_spoons"] = "0"
            elif event.unicode.isdigit():  # Only allow numbers
                editing_state["new_spoons"] += event.unicode

    return input_active, task_list