from config import *

from drawing_functions.draw_rounded_button import draw_rounded_button
from drawing_functions.draw_input_box import draw_input_box

import pygame

"""
Summary:
    Draws the input interface for entering the number of spoons and rest options on the given screen.

Parameters:
    screen (pygame.Surface): The surface on which the input interface will be drawn.
    daily_spoons (dict): Dictionary containing the number of spoons for each day of the week.
    spoons (int): The current number of spoons.
    done_button_color (tuple): Color for the 'Done' button.

Returns:
    daily_spoon_inputs (dict): Dictionary containing the values of the spoon input boxes for each day of the week.
"""

def draw_input_spoons(screen, daily_spoons, spoons, done_button_color, input_active):
    global hub_buttons_showing

    # Draw current UI elements
    draw_rounded_button(screen, hub_toggle, LIGHT_GRAY, BLACK, 0, 2)# type: ignore
    pygame.draw.rect(screen, BLACK, hub_menu1)# type: ignore
    pygame.draw.rect(screen, BLACK, hub_menu2)# type: ignore
    pygame.draw.rect(screen, BLACK, hub_menu3)# type: ignore

    # Main spoon input box
    draw_input_box(screen, spoon_amount_input_box, input_active == "spoons", str(spoons), GREEN, LIGHT_GRAY)# type: ignore
    prompt = font.render("Enter Number of Spoons:", True, BLACK)# type: ignore
    screen.blit(prompt, (255, 50))

    # Rest buttons and labels
    draw_rounded_button(screen, spoon_done_button, done_button_color, BLACK, 15)# type: ignore
    done_text = font.render("Done", True, WHITE)# type: ignore
    screen.blit(done_text, (done_button.x + 69, done_button.y - 313))

    draw_rounded_button(screen, short_rest_button, done_button_color, BLACK, 15, 3)# type: ignore
    screen.blit(font.render("Short Rest", True, BLACK), (short_rest_button.x + 45, short_rest_button.y + 12))# type: ignore
    draw_rounded_button(screen, half_rest_button, done_button_color, BLACK, 15, 3)# type: ignore
    screen.blit(font.render("Half Rest", True, BLACK), (half_rest_button.x + 55, half_rest_button.y + 12))# type: ignore
    draw_rounded_button(screen, full_rest_button, done_button_color, BLACK, 15, 3)# type: ignore
    screen.blit(font.render("Full Rest", True, BLACK), (full_rest_button.x + 55, full_rest_button.y + 12))# type: ignore

    # Weekly spoon settings section
    days_of_week = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    daily_spoon_inputs = {}  # Store each input box for the days of the week

    automatic_spoon_add_label = font.render("Enter number of Spoons you start off with in the morning:", True, BLACK)# type: ignore
    screen.blit(automatic_spoon_add_label, (80, 330))

    for i, day in enumerate(days_of_week):
        # Define the position of each day's input box
        day_input_box = pygame.Rect(40 + i * 110, 400, 50, 50)
        daily_spoon_inputs[day] = day_input_box

        # Draw the input box and label for each day
        draw_input_box(screen, day_input_box, input_active == day, str(daily_spoons.get(day, 0)), GREEN, LIGHT_GRAY)# type: ignore
        day_label = small_font.render(f"{day}:", True, BLACK)# type: ignore
        screen.blit(day_label, (35 + i * 112, 370))

    return daily_spoon_inputs  # Return the dictionary to use for input handling

"""
Summary:
    Handles the logic for interacting with the input interface for entering the number of spoons and rest options.

Parameters:
    event (pygame.event.Event): The event object containing information about the user input.
    short_rest_amount (int): The number of spoons added for a short rest.
    half_rest_amount (int): The number of spoons added for a half rest.
    full_rest_amount (int): The number of spoons added for a full rest.
    daily_spoons (dict): Dictionary containing the number of spoons for each day of the week.
    spoons (int): The current number of spoons.
    daily_spoon_inputs (dict): Dictionary containing the input boxes for each day of the week.
    input_active (str or bool): The currently active input box or False if none is active.

Returns:
    (tuple) Updated values for: spoons, daily_spoons, input_active, and page.
"""

def logic_input_spoons(event, short_rest_amount, half_rest_amount, full_rest_amount, 
                       daily_spoons, spoons, daily_spoon_inputs, input_active):
    page = "input_spoons"
    if event.type == pygame.MOUSEBUTTONDOWN:
        # Check for general input box and rest buttons
        if spoon_amount_input_box.collidepoint(event.pos):
            input_active = "spoons"  # Activate general spoons input
        elif spoon_done_button.collidepoint(event.pos):
            page = "input_tasks"
            input_active = False  # Deactivate after done
        elif short_rest_button.collidepoint(event.pos):
            spoons += short_rest_amount
        elif half_rest_button.collidepoint(event.pos):
            spoons += half_rest_amount
        elif full_rest_button.collidepoint(event.pos):
            spoons += full_rest_amount
        else:
            # Check each day’s input box
            for day, box in daily_spoon_inputs.items():
                if box.collidepoint(event.pos):
                    input_active = day  # Activate input for the specific day
                    break
            else:
                input_active = False  # Deactivate if clicked outside all boxes

    # Handle text input for spoons or daily spoon counts
    if event.type == pygame.KEYDOWN and input_active:
        if event.key == pygame.K_RETURN:
            # Deactivate on Enter
            page = "input_tasks"
            input_active = False
        elif event.key == pygame.K_BACKSPACE:
            # Backspace handling
            if input_active == "spoons":
                spoons = spoons // 10
            else:
                daily_spoons[input_active] = daily_spoons.get(input_active, 0) // 10
        else:
            try:
                # Update either general spoons or specific day's spoon count
                if input_active == "spoons":
                    spoons = spoons * 10 + int(event.unicode)
                else:
                    # Update the daily spoon count for the specific day
                    daily_spoons[input_active] = daily_spoons.get(input_active, 0) * 10 + int(event.unicode)
            except ValueError:
                pass
    return spoons, daily_spoons, input_active, page