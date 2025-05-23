import pygame
from config import font
from colors import COLORS
from datetime import datetime
for name, value in COLORS.items():
    globals()[name] = value

def draw_spoons(screen, spoons, icon_image, spoon_name):
    # render the text
    spoon_text = font.render(f"{spoon_name}:", True, BLACK) #type: ignore
    text_x, text_y = 100, 20
    screen.blit(spoon_text, (text_x, text_y))

    # compute where to start drawing icons:
    # text_width + a little padding
    padding = 5
    start_x = text_x + spoon_text.get_width() + padding
    icon_y  = 15        # your existing vertical offset
    icon_w, icon_h = icon_image.get_size()

    if 0 < spoons < 21:
        # draw one icon per spoon
        for i in range(spoons):
            screen.blit(icon_image, (start_x + i * (icon_w + padding), icon_y))
    else:
        # no spoons
        none_text = font.render("None", True, BLACK) #type: ignore
        screen.blit(none_text, (start_x, text_y))
