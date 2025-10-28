import pygame
import math
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
    "spoon_input_line":0.40,
    "rest_buttons":    0.35,
    "daily_prompt":    0.27,
}

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

def draw_input_spoons(screen, spoons, spoon_name, delta_time, icon_image, input_active, background_color, x_offset=40):
    global spoon_rects, rest_icon_rects, rest_labels

    sw, sh = screen.get_size()
    mouse_x, mouse_y = pygame.mouse.get_pos()
    sw -= 200

    title_font = pygame.font.Font("fonts/Stardew_Valley.ttf", int(sh * 0.07))
    rest_font = pygame.font.Font("fonts/Stardew_Valley.ttf", int(sh * 0.045))

    # — rest icon buttons —
    button_w = button_h = int(sh * 0.35)
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
                if spoons > 99:
                    spoons = 99
                return spoons, daily_spoons, "input_spoons", False
            

    return spoons, daily_spoons, page, input_active
