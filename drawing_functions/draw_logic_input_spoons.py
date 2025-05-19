import pygame
import pygame_gui
import math
from pygame_gui.elements import UITextEntryLine, UIButton, UILabel

# Global UI elements
rest_buttons = {}
daily_inputs = {}
labels = []
spoon_rects = []  # Stores clickable spoon icon rects

layout_heights = {
    "spoon_label": 0.1,
    "spoon_input_line": 0.2,
    "rest_buttons": 0.4,
    "daily_prompt": 0.6,
    "day_label": 0.7,
    "day_input": 0.8
}


def set_opacity(image, alpha):
    temp = image.copy()
    temp.set_alpha(alpha)
    return temp


def tint_image(image, tint_color):
    tinted = image.copy()
    tint_surface = pygame.Surface(image.get_size(), pygame.SRCALPHA)
    tint_surface.fill(tint_color)
    tinted.blit(tint_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    return tinted


def get_pulse_alpha(time_sec, min_alpha=128, max_alpha=255, speed=4.0):
    return int(min_alpha + (max_alpha - min_alpha) * 0.3 * (1 + math.sin(time_sec * speed)))


def draw_input_spoons(screen, manager, UI_elements_initialized, daily_spoons, spoons, delta_time, icon_image):
    global rest_buttons, daily_inputs, labels, spoon_rects
    screen_width, screen_height = screen.get_size()

    if not UI_elements_initialized:
        manager.clear_and_reset()
        input_width = int(screen_width * 0.06)
        button_width = screen_width * 0.15
        button_height = screen_height * 0.1
        spacing = screen_width * 0.02
        font = pygame.font.Font(None, int(screen_height * 0.06))
        big_font = pygame.font.Font(None, int(screen_height * 0.067))

        # Label: "Current Spoon Status"
        label_text = "Current Spoon Status"
        text_width, text_height = font.size(label_text)
        labels.append(UILabel(
            relative_rect=pygame.Rect(
                ((screen_width - text_width) // 2, screen_height * layout_heights["spoon_label"]),
                (text_width, text_height + 10)
            ),
            text=label_text,
            manager=manager
        ))

        # Rest Buttons (Short, Half, Full)
        y_rest = int(screen_height * layout_heights["rest_buttons"])
        total_button_area = 3 * button_width + 2 * spacing
        start_x = (screen_width - total_button_area) // 2

        rest_buttons['short'] = UIButton(
            relative_rect=pygame.Rect((start_x, y_rest), (button_width, button_height)),
            text='Short Rest (+2)', manager=manager
        )
        rest_buttons['half'] = UIButton(
            relative_rect=pygame.Rect((start_x + button_width + spacing, y_rest), (button_width, button_height)),
            text='Half Rest (+5)', manager=manager
        )
        rest_buttons['full'] = UIButton(
            relative_rect=pygame.Rect((start_x + 2 * (button_width + spacing), y_rest), (button_width, button_height)),
            text='Full Rest (+10)', manager=manager
        )

        # Daily Spoon Prompt
        label_text = "Enter the number of spoons you start with each day:"
        text_width, text_height = font.size(label_text)
        labels.append(UILabel(
            pygame.Rect(
                ((screen_width - text_width) // 2, screen_height * layout_heights["daily_prompt"]),
                (text_width, text_height + 10)
            ),
            text=label_text,
            manager=manager
        ))

        # Daily Inputs (Mon–Sun)
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        box_width = input_width
        box_height = 30
        total_width = len(days) * box_width + (len(days) - 1) * spacing
        start_x = (screen_width - total_width) // 2
        y_day_label = screen_height * layout_heights["day_label"]
        y_day_input = screen_height * layout_heights["day_input"]

        for i, day in enumerate(days):
            x_pos = start_x + i * (box_width + spacing)
            labels.append(UILabel(
                pygame.Rect((x_pos, y_day_label), (box_width, 20)),
                text=f"{day}:", manager=manager
            ))
            daily_inputs[day] = UITextEntryLine(
                pygame.Rect((x_pos, y_day_input), (box_width, box_height)),
                manager=manager
            )
            daily_inputs[day].set_text(str(daily_spoons.get(day, 0)))

        UI_elements_initialized = True

    # Update & draw UI manager
    manager.update(delta_time)
    manager.draw_ui(screen)

    # Spoon Icon Drawing
    icon_w, icon_h = icon_image.get_size()
    spacing = 10
    start_x = (screen_width - (10 * icon_w + 9 * spacing)) // 2
    start_y = int(screen_height * layout_heights["spoon_input_line"])

    mouse_x, mouse_y = pygame.mouse.get_pos()
    hovered_index = None
    spoon_rects = []

    # Detect hovered spoon
    for i in range(20):
        row = i // 10
        col = i % 10
        x = start_x + col * (icon_w + spacing)
        y = start_y + row * (icon_h + spacing)
        rect = pygame.Rect(x, y, icon_w, icon_h)
        spoon_rects.append((i, rect))
        if rect.collidepoint(mouse_x, mouse_y):
            hovered_index = i

    # Pulse for hover feedback
    time_sec = pygame.time.get_ticks() / 1000.0
    pulse_alpha = get_pulse_alpha(time_sec)

    for i, rect in spoon_rects:
        if i < spoons:
            icon = icon_image.copy()
            if hovered_index is not None and i >= hovered_index and hovered_index < spoons:
                icon = tint_image(icon, (255, 0, 0, 100))
                icon.set_alpha(pulse_alpha)
        else:
            icon = set_opacity(icon_image, 128)
            if hovered_index is not None and i <= hovered_index and hovered_index >= spoons:
                icon = tint_image(icon, (0, 255, 0, 100))
                icon.set_alpha(pulse_alpha)

        screen.blit(icon, rect.topleft)


def logic_input_spoons(event, manager, short_rest_amount, half_rest_amount, full_rest_amount, daily_spoons, spoons):
    global rest_buttons, daily_inputs, spoon_rects

    page = "input_spoons"

    if event.type == pygame.USEREVENT and event.user_type == pygame_gui.UI_BUTTON_PRESSED:
        if event.ui_element == rest_buttons['short']:
            spoons += short_rest_amount
        elif event.ui_element == rest_buttons['half']:
            spoons += half_rest_amount
        elif event.ui_element == rest_buttons['full']:
            spoons += full_rest_amount

    elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
        mouse_pos = event.pos
        for index, rect in spoon_rects:
            if rect.collidepoint(mouse_pos):
                spoons = index + 1
                break

    # Sanitize and apply daily inputs
    for day, input_box in daily_inputs.items():
        raw_day_text = input_box.get_text()
        numeric_day_text = ''.join(c for c in raw_day_text if c.isdigit())
        if raw_day_text != numeric_day_text:
            input_box.set_text(numeric_day_text)
        try:
            daily_spoons[day] = int(numeric_day_text)
        except ValueError:
            daily_spoons[day] = 0

    if spoons > 20:
        spoons = 20

    return spoons, daily_spoons, page
