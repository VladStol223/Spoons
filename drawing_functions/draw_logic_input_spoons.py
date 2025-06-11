import pygame
import pygame_gui
import math
from pygame_gui.elements import UITextEntryLine, UILabel
from config import *

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
    tinted = image.copy()
    ts = pygame.Surface(image.get_size(), pygame.SRCALPHA)
    ts.fill(tint_color)
    tinted.blit(ts, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    return tinted

def get_pulse_alpha(t, min_alpha=128, max_alpha=255, speed=4.0):
    return int(min_alpha + (max_alpha - min_alpha) * 0.3 * (1 + math.sin(t * speed)))

def draw_input_spoons(screen, manager, UI_elements_initialized, daily_spoons, spoons, delta_time, icon_image, x_offset=40):
    global labels, daily_inputs, spoon_rects, rest_icon_rects, rest_labels

    short_rest_amount = 2
    half_rest_amount  = 5
    full_rest_amount  = 10

    sw, sh = screen.get_size()
    sw = sw - 200  # leave some space for the UI manager
    mouse_x, mouse_y = pygame.mouse.get_pos()

    # — title & prompt —
    title_font = pygame.font.Font("fonts/Stardew_Valley.ttf", int(sh * 0.07))
    title_surf = title_font.render("Current Spoon Status", True, (255,255,255))
    tx = ((sw - title_surf.get_width())//2) + x_offset
    ty = int(sh * layout_heights["spoon_label"])
    screen.blit(title_surf, (tx, ty))
    prompt_font = pygame.font.Font("fonts/Stardew_Valley.ttf", int(sh * 0.045))
    prompt_surf1 = prompt_font.render("Enter the number of", True, (255,255,255))
    prompt_surf2 = prompt_font.render("spoons you start", True, (255,255,255))
    prompt_surf3 = prompt_font.render("start with each day:", True, (255,255,255))
    px1 = 755
    py1 = int(sh * layout_heights["daily_prompt"])
    px2 = px1 + 20
    py2 = py1 + prompt_surf1.get_height()
    px3 = px1
    py3 = py2 + prompt_surf2.get_height()
    screen.blit(prompt_surf1, (px1, py1))
    screen.blit(prompt_surf2, (px2, py2))
    screen.blit(prompt_surf3, (px3, py3))

    box_w = int(sw * 0.06)
    box_h = 30
    dx = 785
    dy = py3 + prompt_surf3.get_height()  # start just below prompt
    day_font = pygame.font.Font("fonts/Stardew_Valley.ttf", 24)
    for day in days:
        # render label
        lbl = day_font.render(f"{day}:", True, (255,255,255))
        screen.blit(lbl, (dx, dy))
        dy += box_h + 10

    if not UI_elements_initialized:
        manager.clear_and_reset()
        labels.clear()
        daily_inputs.clear()

        # draw day inputs vertically under prompt
        dy = py3 + prompt_surf3.get_height()
        for day in days:
            # input box
            inp_rect = pygame.Rect((dx + 50, dy), (box_w, box_h))
            inp = UITextEntryLine(inp_rect, manager=manager)
            inp.set_text(str(daily_spoons.get(day,0)))
            daily_inputs[day] = inp
            dy += box_h + 10

    # — rest-icon rects —
    button_w = button_h = int(sh * 0.175)
    spacing  = sw * 0.05
    total_w  = 3 * button_w + 2 * spacing
    start_x  = ((sw - total_w) // 2) + x_offset
    y_rest   = int(sh * layout_heights["rest_buttons"])
    rest_icon_rects = {
        "short": pygame.Rect(start_x,                          y_rest, button_w, button_h),
        "half":  pygame.Rect(start_x + (button_w + spacing),  y_rest, button_w, button_h),
        "full":  pygame.Rect(start_x + 2*(button_w + spacing),y_rest, button_w, button_h)
    }

    # — rest labels —
    rest_labels.clear()
    font_small = pygame.font.Font("fonts/Stardew_Valley.ttf", int(sh * 0.04))
    texts = {"short": "Short rest","half": "Half rest","full": "Full rest"}
    for name in ("short", "half", "full"):
        rect = rest_icon_rects[name]
        surf = font_small.render(texts[name], True, (255, 255, 255))
        lbl_rect = surf.get_rect(center=(rect.centerx, rect.bottom + surf.get_height()/2 + 5))
        rest_labels[name] = (surf, lbl_rect)

    

    # — draw rest icons & detect hover —
    icons = {"short": short_rest, "half": half_rest, "full": full_rest}
    hovered_rest = None
    for name, rect in rest_icon_rects.items():
        img_s = pygame.transform.scale(icons[name], rect.size)
        screen.blit(img_s, rect.topleft)
        if rect.collidepoint(mouse_x, mouse_y):
            hovered_rest = name

    # — draw rest labels —
    for name, (surf, lbl_rect) in rest_labels.items():
        screen.blit(surf, lbl_rect)

    # — spoon grid —
    icon_w, icon_h = icon_image.get_size()
    grid_spacing = 10
    grid_start_x = ((sw - (10*icon_w + 9*grid_spacing)) // 2) + x_offset
    start_y = int(sh * layout_heights["spoon_input_line"])
    spoon_rects = []
    hovered_spoon_index = None
    for i in range(20):
        r, c = divmod(i, 10)
        x = grid_start_x + c*(icon_w + grid_spacing)
        y = start_y + r*(icon_h + grid_spacing)
        rect = pygame.Rect(x, y, icon_w, icon_h)
        spoon_rects.append((i, rect))
        if rect.collidepoint(mouse_x, mouse_y):
            hovered_spoon_index = i

    pulse_alpha = get_pulse_alpha(pygame.time.get_ticks()/1000.0)
    rest_amounts = {"short": short_rest_amount,"half": half_rest_amount,"full": full_rest_amount}
    add_amt = rest_amounts.get(hovered_rest, 0)

    # — draw stars with tint/alpha —
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

    # — UI manager on top —
    manager.update(delta_time)
    manager.draw_ui(screen)

    return UI_elements_initialized, daily_spoons, spoons

def logic_input_spoons(event, manager, short_rest_amount, half_rest_amount, full_rest_amount, daily_spoons, spoons):
    global spoon_rects, rest_icon_rects
    page = "input_spoons"

    # handle rest and spoon-grid clicks
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        # rest icons first
        for name, rect in rest_icon_rects.items():
            if rect.collidepoint(event.pos):
                spoons += {'short':short_rest_amount,'half':half_rest_amount,'full':full_rest_amount}[name]
                return spoons, daily_spoons, page
        # spoon grid
        for i, rect in spoon_rects:
            if rect.collidepoint(event.pos):
                spoons = i+1
                break

    # sanitize inputs
    for day, inp in daily_inputs.items():
        txt = inp.get_text()
        num = ''.join(ch for ch in txt if ch.isdigit())
        inp.set_text(num)
        daily_spoons[day] = int(num) if num else 0

    spoons = min(spoons, 20)
    return spoons, daily_spoons, page
