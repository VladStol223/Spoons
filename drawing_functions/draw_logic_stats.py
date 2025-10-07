import os
import pygame
from copyparty_sync import clear_credentials, get_current_user

_logout_rect = None

def draw_stats(screen, font, big_font, *_unused):
    global _logout_rect
    sw, sh = screen.get_size()

    # Title
    title = big_font.render("Settings", True, (255, 255, 255))
    screen.blit(title, ((sw - title.get_width()) // 2, int(sh * 0.18)))

    # Signed-in username
    username = get_current_user() or "(not signed in)"
    user_surf = font.render(f"Signed in as: {username}", True, (200, 200, 200))
    screen.blit(user_surf, ((sw - user_surf.get_width()) // 2, int(sh * 0.28)))

    # Log out button
    btn_w, btn_h = int(sw * 0.28), int(sh * 0.10)
    _logout_rect = pygame.Rect((sw - btn_w) // 2, int(sh * 0.40), btn_w, btn_h)
    pygame.draw.rect(screen, (200, 70, 70), _logout_rect, border_radius=16)

    label = font.render("Log out", True, (255, 255, 255))
    screen.blit(label, (_logout_rect.centerx - label.get_width() // 2,
                        _logout_rect.centery - label.get_height() // 2))


def logic_stats(event, page):
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and _logout_rect:
        if _logout_rect.collidepoint(event.pos):
            clear_credentials()
            return "login"
    return page
