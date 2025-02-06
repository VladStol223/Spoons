import pygame
from config import font, small_font
from colors import COLORS
for name, value in COLORS.items():
    globals()[name] = value

def draw_input_box(screen, rect, active, text, active_color, inactive_color):
    if active == "small_font":
        text_surface = small_font.render(str(text), True, BLACK) # type: ignore
        color = inactive_color
        screen.blit(text_surface, (rect.x + 5, rect.y + 7))
    else:
        color = active_color if active else inactive_color
        text_surface = font.render(str(text), True, BLACK) # type: ignore
        screen.blit(text_surface, (rect.x + 5, rect.y + 12))
    pygame.draw.rect(screen, color, rect, 2)