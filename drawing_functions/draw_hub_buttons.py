from config import *
from drawing_functions.draw_rounded_button import draw_rounded_button

import pygame

button_widths = {}

def draw_hub_buttons(screen, page, tool_tips, background_color, add_spoons_color, add_tasks_color,
                     manage_tasks_color, study_color, calendar_color, store_color,
                     stats_color, button_widths, hub_closing, delta_time):
    global hub_buttons_showing

    hub_buttons_showing = True
    mouse_pos = pygame.mouse.get_pos()

    # Button draw order
    draw_animated_button(screen, hub_add_spoons, add_spoons_color, add_spoons_color, BLACK, font, "Add Spoons", BLACK, button_widths, hub_closing, delta_time)# type: ignore
    draw_animated_button(screen, hub_add_task, add_tasks_color, add_tasks_color, BLACK, font, "Add Tasks", BLACK, button_widths, hub_closing, delta_time)# type: ignore
    draw_animated_button(screen, hub_manage_task, manage_tasks_color, manage_tasks_color, BLACK, font, "Manage Tasks", BLACK, button_widths, hub_closing, delta_time)# type: ignore
    draw_animated_button(screen, hub_study, study_color, study_color, BLACK, font, "Study", BLACK, button_widths, hub_closing, delta_time)# type: ignore
    draw_animated_button(screen, hub_calendar, calendar_color, calendar_color, BLACK, font, "Calendar", BLACK, button_widths, hub_closing, delta_time)# type: ignore
    draw_animated_button(screen, hub_store, store_color, store_color, BLACK, font, "Store", BLACK, button_widths, hub_closing, delta_time)# type: ignore
    draw_animated_button(screen, hub_stats, stats_color, stats_color, BLACK, font, "Statistics", BLACK, button_widths, hub_closing, delta_time)# type: ignore

    return button_widths


def draw_centered_text(screen, font, text, rect, color):
    text_surface = font.render(text, True, color)  # Render text
    text_width, text_height = text_surface.get_size()  # Get text dimensions
    text_x = rect.x + (rect.width - text_width) // 2  # Center horizontally
    text_y = rect.y + (rect.height - text_height) // 2  # Center vertically
    screen.blit(text_surface, (text_x, text_y))

# Function to interpolate between two values (used for smooth transition)
def lerp(a, b, t, delta_time):
    return a + (b - a) * min(t * delta_time, 1)

# Function to check if the mouse is hovering over a button
def is_hovered(rect):
    mouse_x, mouse_y = pygame.mouse.get_pos()
    return rect.collidepoint(mouse_x, mouse_y)

# Function to draw buttons with both slide-in & hover animation
def draw_animated_button(screen, rect, base_color, hover_color, border_color, font, text, text_color, 
                         button_widths, hub_closing, delta_time, hover_speed= 7.5, entry_speed= 7.5, hover_increase=100):
    rect_key = (rect.x, rect.y, rect.width, rect.height)

    # Initialize width if not present
    if rect_key not in button_widths:
        button_widths[rect_key] = 0  

    # Determine the target width based on hub state
    if hub_buttons_showing:
        target_width = rect.width  # Expand to full width
    else:
        target_width = 0  # Shrink back to 0 when hub is hidden

    # Apply animation (smooth transition)
    if hub_closing == False:
        button_widths[rect_key] = lerp(button_widths[rect_key], target_width, entry_speed, delta_time)
        current_width = int(button_widths[rect_key])
    else:
        button_widths[rect_key] = lerp(button_widths[rect_key], 0, entry_speed, delta_time)
        current_width = int(button_widths[rect_key])
    # Hover effect (slightly increase size)
    if is_hovered(rect) and hub_buttons_showing and hub_closing == False:
        target_width = rect.width + hover_increase
        button_widths[rect_key] = lerp(button_widths[rect_key], target_width, hover_speed, delta_time)
        current_width = int(button_widths[rect_key])

    # Adjust position to expand/shrink outward evenly
    final_rect = pygame.Rect(rect.x, rect.y, current_width, rect.height)

    # Draw the button
    draw_rounded_button(screen, final_rect, hover_color if is_hovered(rect) else base_color, border_color, 0, 0)
    
    # Draw centered text
    if current_width > 50 and hub_closing == False:  # Prevent text from appearing when the button is fully closed
        draw_centered_text(screen, font, text, final_rect, text_color)

def reset_button_widths():
    """ Clears the button width dictionary to reset animations. """
    global button_widths
    button_widths.clear()