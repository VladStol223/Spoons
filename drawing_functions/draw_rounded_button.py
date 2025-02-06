import pygame

def draw_rounded_button(screen, rect, color, border_color, border_radius=10, border_width=2):
    pygame.draw.rect(screen, border_color, rect, border_radius=border_radius)
    inner_rect = rect.inflate(-border_width * 4, -border_width * 4)  
    pygame.draw.rect(screen, color, inner_rect, border_radius=border_radius)