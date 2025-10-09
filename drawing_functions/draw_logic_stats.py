import os
import pygame
from copyparty_sync import clear_credentials, get_current_user, upload_data_json 
from config import *
import threading

_logout_rect = None
_upload_rect = None
_upload_pos = None  # (x, y) the top-left where the floppy is drawn
_upload_state = {
    "uploading": False,   # True while background upload is running
    "done": False,        # True when upload thread completes (see note below)
    "anim_step": 0,       # 0=left, 1=left+mid, 2=left+mid+right, 3=none (clear), repeats
    "next_tick_ms": 0     # pygame.time.get_ticks() threshold for next step
}

def _start_upload_thread():
    def _worker():
        try:
            upload_data_json()
        except Exception as _e:
            # upload_data_json() mostly handles/prints its own errors; we treat completion as "done"
            pass
        finally:
            _upload_state["uploading"] = False
            _upload_state["done"] = True
    t = threading.Thread(target=_worker, daemon=True)
    t.start()

def _update_upload_anim(now_ms):
    # advance animation every 500 ms through steps [0,1,2,3] then loop
    if now_ms >= _upload_state["next_tick_ms"]:
        _upload_state["anim_step"] = (_upload_state["anim_step"] + 1) % 4
        _upload_state["next_tick_ms"] = now_ms + 500

def draw_stats(screen, font, big_font, *_unused):
    global _logout_rect, _upload_rect, _upload_pos
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

    if username == "(not signed in)":
        pygame.draw.rect(screen, (70, 200, 70), _logout_rect, border_radius=16)
        label = font.render("Log In", True, (255, 255, 255))
    else:
        pygame.draw.rect(screen, (200, 70, 70), _logout_rect, border_radius=16)
        label = font.render("Log out", True, (255, 255, 255))
    screen.blit(label, (_logout_rect.centerx - label.get_width() // 2, _logout_rect.centery - label.get_height() // 2))

    # --- Upload floppy position & hitbox ---
    # You already chose this location:
    _upload_pos = (int(sw * 0.9), int(sh * 0.9 - 45))
    screen.blit(floppy_disk_upload, _upload_pos)
    uw, uh = floppy_disk_upload.get_size()
    _upload_rect = pygame.Rect(_upload_pos[0], _upload_pos[1], uw, uh)

    # --- Overlay animation/checkmark logic ---
    # While uploading: animate dots; when done: show checkmark for a short time.
    now = pygame.time.get_ticks()
    if _upload_state["uploading"]:
        _update_upload_anim(now)
        # draw dots overlay progressively (image split into three equal-width thirds)
        dw, dh = floppy_disk_dots.get_size()
        third = dw // 3
        x0, y0 = _upload_pos
        # step 0 -> left only; step 1 -> left+middle; step 2 -> left+middle+right; step 3 -> none
        visible_count = 0 if _upload_state["anim_step"] == 3 else (_upload_state["anim_step"] + 1)
        if visible_count >= 1:
            screen.blit(floppy_disk_dots.subsurface(pygame.Rect(0, 0, third, dh)), (x0, y0))
        if visible_count >= 2:
            screen.blit(floppy_disk_dots.subsurface(pygame.Rect(third, 0, third, dh)), (x0 + third, y0))
        if visible_count >= 3:
            screen.blit(floppy_disk_dots.subsurface(pygame.Rect(third * 2, 0, third, dh)), (x0 + third * 2, y0))


    elif _upload_state["done"]:
        # Show checkmark 3s at full opacity, then linearly fade to 0 over next 3s
        if _upload_state.get("done_started_at") is None:
            _upload_state["done_started_at"] = now
        elapsed = now - _upload_state["done_started_at"]
        if elapsed < 3000:
            screen.blit(floppy_disk_checkmark, _upload_pos)
        elif elapsed < 6000:
            alpha = int(255 * (1 - (elapsed - 3000) / 3000.0))
            chk = floppy_disk_checkmark.convert_alpha().copy()
            chk.set_alpha(alpha)
            screen.blit(chk, _upload_pos)
        else:
            _upload_state["done"] = False
            _upload_state["done_started_at"] = None


def logic_stats(event, page):
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        if _logout_rect and _logout_rect.collidepoint(event.pos):
            clear_credentials()
            return "login"
        # Start upload when floppy is clicked (only if not already uploading)
        if _upload_rect and _upload_rect.collidepoint(event.pos) and not _upload_state["uploading"]:
            _upload_state["uploading"] = True
            _upload_state["done"] = False
            _upload_state["done_started_at"] = None
            _upload_state["anim_step"] = 3
            _upload_state["next_tick_ms"] = pygame.time.get_ticks() + 500
            _start_upload_thread()

    return page
