from config import *
from drawing_functions.draw_rounded_button import draw_rounded_button

import pygame

button_widths = {}
button_positions = {}
animation_complete = False

def draw_hub_buttons(screen, page, tool_tips, background_color, add_spoons_color, add_tasks_color, complete_tasks_color, remove_tasks_color, daily_schedule_color, calendar_color, settings_color):
    global hub_buttons_showing
    hub_buttons_showing = True
    mouse_pos = pygame.mouse.get_pos()

    darker_background_color = (max(0, background_color[0] - 20), 
        max(0, background_color[1] - 20), 
        max(0, background_color[2] - 20))
    pygame.draw.rect(screen, darker_background_color, hub_cover)
    pygame.draw.rect(screen, LIGHT_GRAY, hub_toggle)# type: ignore
    pygame.draw.rect(screen, BLACK,hub_menu1)# type: ignore
    pygame.draw.rect(screen, BLACK,hub_menu2_open)# type: ignore
    pygame.draw.rect(screen, BLACK,hub_menu3) # type: ignore

    entry_speed = 0.06

    draw_animated_button(screen, hub_add_spoons, add_spoons_color, add_spoons_color, BLACK, font, "Add Spoons", BLACK, entry_speed=entry_speed) # type: ignore
    draw_animated_button(screen, hub_add_task, add_tasks_color, add_tasks_color, BLACK, font, "Add Tasks", BLACK, entry_speed=entry_speed) # type: ignore
    draw_animated_button(screen, hub_complete_task, complete_tasks_color, complete_tasks_color, BLACK, font, "Complete Tasks", BLACK, entry_speed=entry_speed) # type: ignore
    draw_animated_button(screen, hub_remove_task, remove_tasks_color, remove_tasks_color, BLACK, font, "Remove Tasks", BLACK, entry_speed=entry_speed) # type: ignore
    draw_animated_button(screen, hub_daily_schedule, daily_schedule_color, daily_schedule_color, BLACK, font, "Daily Schedule", BLACK, entry_speed=entry_speed) # type: ignore
    draw_animated_button(screen, hub_calendar, calendar_color, calendar_color, BLACK, font, "Calendar", BLACK, entry_speed=entry_speed) # type: ignore
    draw_animated_button(screen, hub_settings, settings_color, settings_color, BLACK, font, "Settings", BLACK, entry_speed=entry_speed) # type: ignore


    if tool_tips == True:
        if hub_add_spoons.collidepoint(mouse_pos):
            draw_rounded_button(screen, add_spoons_tool_tip_rect, LIGHT_GRAY, BLACK, 5, 3)# type: ignore
            hover_text = f"Allows users to increase the\namount of energy, or {spoon_name}\nthey have, representing\navailable energy or capacity\nfor tasks. Users can manually\nadd {spoon_name} for themselves\nor have them be added\nautomatically."
            text_lines = hover_text.split('\n')
            y_offset = 0
            for line in text_lines:
                rendered_text = small_font.render(line, True, BLACK)# type: ignore
                screen.blit(rendered_text, (262 + tool_tips_x_offset, 42 + y_offset))
                y_offset += 22
        elif hub_add_task.collidepoint(mouse_pos):
            draw_rounded_button(screen, add_task_tool_tip_rect, LIGHT_GRAY, BLACK, 5, 3)# type: ignore
            hover_text = f"Allows users to create new \ntasks and assign them to \nspecific folders based on \ncategories such as work, \nchores, or personal projects. \nEach task can have a name, \namount of {spoon_name}, and \ndue date."
            text_lines = hover_text.split('\n')
            y_offset = 0
            for line in text_lines:
                rendered_text = small_font.render(line, True, BLACK)# type: ignore
                screen.blit(rendered_text, (262 + tool_tips_x_offset, 112 + y_offset))
                y_offset += 22
        elif hub_complete_task.collidepoint(mouse_pos):
            draw_rounded_button(screen, complete_task_tool_tip_rect, LIGHT_GRAY, BLACK, 5, 3)# type: ignore
            hover_text = f"Allows users to view a list \nof tasks that are due or \ncurrently in progress and \nmark them as completed \nonce they have been finished. \nThe interface allows users to \ntrack progress across \ndifferent areas of their life."
            text_lines = hover_text.split('\n')
            y_offset = 0
            for line in text_lines:
                rendered_text = small_font.render(line, True, BLACK)# type: ignore
                screen.blit(rendered_text, (262 + tool_tips_x_offset, 182 + y_offset))
                y_offset += 22
        elif hub_remove_task.collidepoint(mouse_pos):
            draw_rounded_button(screen, remove_task_tool_tip_rect, LIGHT_GRAY, BLACK, 5, 3)# type: ignore
            hover_text = f"Allows users to delete tasks \nthat are either completed or \nhave become obsolete. \nThis helps in keeping the \ntask lists clean and focused \non actionable items, making \na streamlined approach to \ntask management."
            text_lines = hover_text.split('\n')
            y_offset = 0
            for line in text_lines:
                rendered_text = small_font.render(line, True, BLACK)# type: ignore
                screen.blit(rendered_text, (262 + tool_tips_x_offset, 252 + y_offset))
                y_offset += 22
        elif hub_daily_schedule.collidepoint(mouse_pos):
            draw_rounded_button(screen, daily_schedule_tool_tip_rect, LIGHT_GRAY, BLACK, 5, 3)# type: ignore
            hover_text = f"Allows users to create, edit, \nand manage daily schedules \nfor various needs. This page \nsimplifies planning for trips, \nensuring that all necessary \nitems are noted down and \nthat lists can be easily \nchecked off during their day."
            text_lines = hover_text.split('\n')
            y_offset = 0
            for line in text_lines:
                rendered_text = small_font.render(line, True, BLACK)# type: ignore
                screen.blit(rendered_text, (262 + tool_tips_x_offset, 322 + y_offset))
                y_offset += 22
        elif hub_calendar.collidepoint(mouse_pos):
            draw_rounded_button(screen, calendar_tool_tip_rect, LIGHT_GRAY, BLACK, 5, 3)# type: ignore
            hover_text = f"Allows users to see what is \nplanned for each day. Color-\ncoded Task folders are \ndisplayed on their respective \ndue dates. Users can hover \nover these folders for more \ndetailed infor about the tasks \ndue on any given day."
            text_lines = hover_text.split('\n')
            y_offset = 0
            for line in text_lines:
                rendered_text = small_font.render(line, True, BLACK)# type: ignore
                screen.blit(rendered_text, (262 + tool_tips_x_offset, 392 + y_offset))
                y_offset += 22
        elif hub_settings.collidepoint(mouse_pos):
            draw_rounded_button(screen, settings_tool_tip_rect, LIGHT_GRAY, BLACK, 5, 3)# type: ignore
            hover_text = f"Allows users to customize \nthe appearance of the \nSpoons App. This includes \nchanging themes, colors, \nicons, naming schemes, and \nother personalization \noptions to match user \npreferences."
            text_lines = hover_text.split('\n')
            y_offset = 0
            for line in text_lines:
                rendered_text = small_font.render(line, True, BLACK)# type: ignore
                screen.blit(rendered_text, (262 + tool_tips_x_offset, 392 + y_offset))
                y_offset += 22
        else:
            None

def draw_centered_text(screen, font, text, rect, color):
    text_surface = font.render(text, True, color)  # Render text
    text_width, text_height = text_surface.get_size()  # Get text dimensions
    text_x = rect.x + (rect.width - text_width) // 2  # Center horizontally
    text_y = rect.y + (rect.height - text_height) // 2  # Center vertically
    screen.blit(text_surface, (text_x, text_y))

def is_hovered(rect):
    mouse_x, mouse_y = pygame.mouse.get_pos()
    return rect.collidepoint(mouse_x, mouse_y)

def draw_hovered_button(screen, rect, base_color, hover_color, border_color, font, text, text_color):
    # Expand the width if the button is hovered
    expanded_rect = pygame.Rect(rect.x, rect.y, rect.width + (100 if is_hovered(rect) else 0), rect.height)
    
    # Draw the button
    draw_rounded_button(screen, expanded_rect, hover_color if is_hovered(rect) else base_color, border_color, 0, 0)

    # Draw centered text
    draw_centered_text(screen, font, text, expanded_rect if is_hovered(rect) else rect, text_color)

# Function to interpolate between two values (used for smooth transition)
def lerp(a, b, t):
    return a + (b - a) * t  # Linear interpolation

# Function to check if the mouse is hovering over a button
def is_hovered(rect):
    mouse_x, mouse_y = pygame.mouse.get_pos()
    return rect.collidepoint(mouse_x, mouse_y)

def animate_button_entry(rect, target_x, speed=0.01):
    global animation_complete

    # Convert rect to an immutable tuple (used as dictionary key)
    rect_key = (rect.x, rect.y, rect.width, rect.height)

    # Initialize button's X position if not already set
    if rect_key not in button_positions:
        button_positions[rect_key] = -300  # Start off-screen on the left

    # Smoothly move the button to its target position
    button_positions[rect_key] = lerp(button_positions[rect_key], target_x, speed)

    # Round the value to avoid subpixel artifacts
    current_x = int(button_positions[rect_key])

    # Check if all buttons have reached their target positions
    if all(abs(button_positions[key] - key[0]) < 2 for key in button_positions):
        animation_complete = True  # Mark animation as complete

    return current_x

# Function to draw buttons with both slide-in & hover animation
def draw_animated_button(screen, rect, base_color, hover_color, border_color, font, text, text_color, hover_speed=0.01, entry_speed=0.05):
    global button_positions

    # Animate the button sliding in from the left
    animated_x = animate_button_entry(rect, rect.x, speed=entry_speed)
    animated_rect = pygame.Rect(animated_x, rect.y, rect.width, rect.height)

    # Hover effect (expanding width)
    target_width = rect.width + 100 if is_hovered(rect) else rect.width
    button_widths[(rect.x, rect.y, rect.width, rect.height)] = lerp(button_widths.get((rect.x, rect.y, rect.width, rect.height), rect.width), target_width, hover_speed)
    current_width = int(button_widths[(rect.x, rect.y, rect.width, rect.height)])

    # Adjust position to expand outward evenly
    adjusted_x = animated_rect.x - (current_width - rect.width) // 2
    final_rect = pygame.Rect(adjusted_x, rect.y, current_width, rect.height)

    # Draw the button
    draw_rounded_button(screen, final_rect, hover_color if is_hovered(rect) else base_color, border_color, 0, 0)

    # Draw centered text
    draw_centered_text(screen, font, text, final_rect, text_color)