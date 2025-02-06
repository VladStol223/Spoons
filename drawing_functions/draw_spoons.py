import pygame
from config import font
from colors import COLORS
from datetime import datetime
for name, value in COLORS.items():
    globals()[name] = value

def draw_spoons(screen, spoons, icon_image, spoon_name):
    current_month = datetime.now().month
    current_day = datetime.now().strftime('%d')
    date_text = font.render(f"{current_month}/{current_day}", True, BLACK) # type: ignore
    screen.blit(date_text, (740, 20))
    if spoons > 0 and spoons < 17:
        spoon_text = font.render(f"{spoon_name}:", True, BLACK)# type: ignore
        for i in range(spoons):
            screen.blit(icon_image, (150 + i * 40, 15))
    elif spoons > 16:
        spoon_text = font.render(f"{spoon_name}: {spoons}", True, BLACK)# type: ignore
        screen.blit(icon_image, (180, 15))
    else:
        spoon_text = font.render(f"{spoon_name}: None", True, BLACK)# type: ignore
    screen.blit(spoon_text, (50, 20))