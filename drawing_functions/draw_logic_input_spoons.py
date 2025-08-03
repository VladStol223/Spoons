import pygame
import pygame_gui
import math
from pygame_gui.elements import UITextEntryLine, UILabel
from config import *
from drawing_functions.draw_input_box import draw_input_box

# Global UI elements
daily_inputs    = {}
labels          = []
spoon_rects     = []  # for the 20-spoons grid
rest_icon_rects = {}  # for our 3 rest icons 
rest_labels = {}

layout_heights = {
    "spoon_label":     0.32,
    "spoon_input_line":0.42,
    "rest_buttons":    0.65,
    "daily_prompt":    0.27,
}

days = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]

def set_opacity(image, alpha):
    temp = image.copy()
    temp.set_alpha(alpha)
    return temp

def tint_image(image, tint_color):
    surf = image.copy().convert_alpha()
    r, g, b = tint_color[:3]

    mask = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    mask.fill((r, g, b, 255))

    surf.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    return surf


def get_pulse_alpha(t, min_alpha=128, max_alpha=255, speed=4.0):
    return int(min_alpha + (max_alpha - min_alpha) * 0.3 * (1 + math.sin(t * speed)))

def draw_input_spoons(screen, daily_spoons, spoons, delta_time, icon_image, input_active, background_color, x_offset=40):
    global spoon_rects, rest_icon_rects, rest_labels

    short_rest_amount = 2
    half_rest_amount  = 5
    full_rest_amount  = 10

    sw, sh = screen.get_size()
    mouse_x, mouse_y = pygame.mouse.get_pos()
    sw -= 200

    title_font = pygame.font.Font("fonts/Stardew_Valley.ttf", int(sh * 0.07))
    prompt_font = pygame.font.Font("fonts/Stardew_Valley.ttf", int(sh * 0.045))
    day_font = pygame.font.Font("fonts/Stardew_Valley.ttf",  int(sh * 0.045))
    rest_font = pygame.font.Font("fonts/Stardew_Valley.ttf", int(sh * 0.045))

    # — title & prompt —
    title_surf = title_font.render("Current Spoon Status", True, (255,255,255))
    tx = ((sw - title_surf.get_width())//2) + x_offset
    ty = int(sh * layout_heights["spoon_label"])
    screen.blit(title_surf, (tx, ty))

    prompts = [
        prompt_font.render("Enter the number of", True, (255,255,255)),
        prompt_font.render("spoons you start", True, (255,255,255)),
        prompt_font.render("start with each day:", True, (255,255,255)),
    ]
    px1 = 755
    py = int(sh * layout_heights["daily_prompt"])
    for surf in prompts:
        screen.blit(surf, (px1, py))
        py += surf.get_height()

    # — daily input labels & boxes —
    dx, dy = 785, py
    box_w, box_h = int(sw * 0.06), 30
    for i, day in enumerate(days):
        label = day_font.render(f"{day}:", True, (255,255,255))
        screen.blit(label, (dx, dy + i * (box_h + 10)))

        input_rect = pygame.Rect(dx + 50, dy + i * (box_h + 10), box_w, box_h)
        value = str(daily_spoons.get(day, ""))
        active = input_active == day
        draw_input_box(screen, input_rect, active, value, LIGHT_GRAY, DARK_SLATE_GRAY, True, background_color, "light", 9, 0.045) #type: ignore

    # — rest icon buttons —
    button_w = button_h = int(sh * 0.175)
    spacing = sw * 0.05
    total_w = 3 * button_w + 2 * spacing
    start_x = ((sw - total_w) // 2) + x_offset
    y_rest = int(sh * layout_heights["rest_buttons"])

    rest_icon_rects = {
        "short": pygame.Rect(start_x, y_rest, button_w, button_h),
        "half":  pygame.Rect(start_x + (button_w + spacing), y_rest, button_w, button_h),
        "full":  pygame.Rect(start_x + 2*(button_w + spacing), y_rest, button_w, button_h)
    }

    icons = {"short": short_rest, "half": half_rest, "full": full_rest}
    hovered_rest = None
    for name, rect in rest_icon_rects.items():
        img = pygame.transform.scale(icons[name], rect.size)
        screen.blit(img, rect.topleft)
        if rect.collidepoint(mouse_x, mouse_y):
            hovered_rest = name

    # — rest labels —
    rest_labels.clear()
    texts = {"short": "Short rest", "half": "Half rest", "full": "Full rest"}
    for name, rect in rest_icon_rects.items():
        label = rest_font.render(texts[name], True, (255, 255, 255))
        label_rect = label.get_rect(center=(rect.centerx, rect.bottom + label.get_height()//2 + 5))
        screen.blit(label, label_rect)

    # — spoon grid —
    icon_w, icon_h = icon_image.get_size()
    grid_spacing = 10
    grid_start_x = ((sw - (10 * icon_w + 9 * grid_spacing)) // 2) + x_offset
    start_y = int(sh * layout_heights["spoon_input_line"])

    spoon_rects = []
    hovered_spoon_index = None
    for i in range(20):
        row, col = divmod(i, 10)
        x = grid_start_x + col * (icon_w + grid_spacing)
        y = start_y + row * (icon_h + grid_spacing)
        rect = pygame.Rect(x, y, icon_w, icon_h)
        spoon_rects.append((i, rect))
        if rect.collidepoint(mouse_x, mouse_y):
            hovered_spoon_index = i

    pulse_alpha = get_pulse_alpha(pygame.time.get_ticks()/1000.0)
    rest_amounts = {"short": short_rest_amount, "half": half_rest_amount, "full": full_rest_amount}
    add_amt = rest_amounts.get(hovered_rest, 0)

    for i, rect in spoon_rects:
        star = icon_image.copy()
        if hovered_rest:
            if i < spoons:
                pass
            elif i < spoons + add_amt:
                star = tint_image(star, (0,255,0,100)); star.set_alpha(pulse_alpha)
            else:
                star = set_opacity(star, 128)
        else:
            if i < spoons:
                if hovered_spoon_index is not None and hovered_spoon_index < spoons and i >= hovered_spoon_index:
                    star = tint_image(star, (255,0,0,100)); star.set_alpha(pulse_alpha)
            else:
                star = set_opacity(star, 128)
                if hovered_spoon_index is not None and hovered_spoon_index >= spoons and i <= hovered_spoon_index:
                    star = tint_image(star, (0,255,0,100)); star.set_alpha(pulse_alpha)
        screen.blit(star, rect.topleft)

    return daily_spoons, spoons, input_active

def logic_input_spoons(event, daily_spoons, spoons, input_active):
    global spoon_rects, rest_icon_rects
    page = "input_spoons"

    short_rest_amount = 2
    half_rest_amount  = 5
    full_rest_amount  = 10

    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        # Rest icon clicks
        for name, rect in rest_icon_rects.items():
            if rect.collidepoint(event.pos):
                spoons += {"short": short_rest_amount, "half": half_rest_amount, "full": full_rest_amount}[name]
                return spoons, daily_spoons, "input_spoons", False

        # Spoon grid click
        for i, rect in spoon_rects:
            if rect.collidepoint(event.pos):
                spoons = i + 1
                return spoons, daily_spoons, page, False

        # Daily input box clicks
        dx = 785 + 50
        box_h = 30
        py_start = int(pygame.display.get_surface().get_height() * layout_heights["daily_prompt"])
        py_start += 3 * 22  # Skip prompt lines
        for i, day in enumerate(days):
            rect = pygame.Rect(dx, py_start + i * (box_h + 10), 60, box_h)
            if rect.collidepoint(event.pos):
                return spoons, daily_spoons, page, day  # set this input as active

        input_active = False  # clicked outside any input

    elif event.type == pygame.KEYDOWN and input_active:
        current_val = daily_spoons.get(input_active, "")
        if isinstance(current_val, int): current_val = str(current_val)
        if event.key == pygame.K_BACKSPACE:
            current_val = current_val[:-1]
        elif event.unicode.isdigit() and len(current_val) < 2:
            current_val += event.unicode
        daily_spoons[input_active] = int(current_val) if current_val else 0

    spoons = min(spoons, 20)
    return spoons, daily_spoons, page, input_active
