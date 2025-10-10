import os
import threading
import pygame

from copyparty_sync import (
    clear_credentials,
    get_current_user,
    upload_data_json,
    download_data_json_if_present,
    get_auto_download_flag,
    set_auto_download_flag,
)
from config import *

_logout_rect = None

_upload_rect = None
_upload_pos  = None
_upload_state = {
    "uploading": False,
    "done": False,          # set True when thread completes
    "ok": False,            # True if verified, False if failed
    "anim_step": 0,
    "next_tick_ms": 0,
    "done_started_at": None,
}

_download_rect = None
_download_pos  = None
_download_state = {
    "downloading": False,
    "done": False,
    "ok": False,
    "done_started_at": None,
}

_auto_rect = None  # toggle checkbox rect

def _start_upload_thread():
    def _worker():
        ok = False
        try:
            ok = upload_data_json()  # returns True if verified
        except Exception:
            ok = False
        finally:
            _upload_state["uploading"] = False
            _upload_state["done"] = True
            _upload_state["ok"] = bool(ok)
            _upload_state["done_started_at"] = None
    threading.Thread(target=_worker, daemon=True).start()

def _start_download_thread(): # STOP FUCKING MAKING DAEMON
    def _worker():
        ok = False
        try:
            from main import sync_and_reload
            sync_and_reload(True)  # force download + reload
            ok = True
        except Exception:
            ok = False
        finally:
            _download_state["downloading"] = False
            _download_state["done"] = True
            _download_state["ok"] = bool(ok)
            _download_state["done_started_at"] = None
    threading.Thread(target=_worker, daemon=True).start()

def _update_upload_anim(now_ms):
    if now_ms >= _upload_state["next_tick_ms"]:
        _upload_state["anim_step"] = (_upload_state["anim_step"] + 1) % 4
        _upload_state["next_tick_ms"] = now_ms + 500

def _draw_result_overlay(screen, ok: bool, pos: tuple, started_at_key: str):
    """Shows checkmark or redX for 3s, then fades for 3s."""
    now = pygame.time.get_ticks()
    started = _upload_state if started_at_key == "upload" else _download_state
    key = "done_started_at"
    if started.get(key) is None:
        started[key] = now
    elapsed = now - started[key]

    surf = (floppy_disk_checkmark if ok else floppy_disk_redx).convert_alpha()
    if elapsed < 3000:
        screen.blit(surf, pos)
    elif elapsed < 6000:
        fade = int(255 * (1 - (elapsed - 3000) / 3000.0))
        s2 = surf.copy(); s2.set_alpha(fade)
        screen.blit(s2, pos)
    else:
        started["done"] = False
        started[key] = None

def draw_stats(screen, font, big_font, *_unused):
    global _logout_rect, _upload_rect, _upload_pos, _download_rect, _download_pos, _auto_rect
    sw, sh = screen.get_size()

    # Title
    title = bigger_font.render("Settings", True, (255, 255, 255))
    screen.blit(title, (((sw+82) - title.get_width()) // 2, int(sh * 0.05)))

    # Signed-in username
    username = get_current_user() or "(not signed in)"
    user_surf = font.render(f"Signed in as: {username}", True, (200, 200, 200))
    screen.blit(user_surf, (((sw+82)  - user_surf.get_width()) // 2, int(sh * 0.4)))

    # Toggle: Auto-download at startup
    toggle_y = int(sh * 0.90) - 5
    label = font.render("Auto-Sync", True, (200, 200, 200))
    screen.blit(label, (sw*0.85, toggle_y))
    box_size = int(sh * 0.06)
    _auto_rect = pygame.Rect(sw * 0.81, toggle_y, box_size, box_size)
    pygame.draw.rect(screen, (180, 180, 180), _auto_rect, width=3, border_radius=6)
    # icon inside
    inner = pygame.Rect(_auto_rect.x, _auto_rect.y, _auto_rect.w, _auto_rect.h)
    if get_auto_download_flag():
        # downsize checkmark to fit
        chk = pygame.transform.smoothscale(floppy_disk_checkmark, (inner.w, inner.h))
        screen.blit(chk, inner.topleft)
    else:
        rx = pygame.transform.smoothscale(floppy_disk_redx, (inner.w, inner.h))
        screen.blit(rx, inner.topleft)

    # Log out / Log in button
    btn_w, btn_h = int(sw * 0.28), int(sh * 0.10)
    _logout_rect = pygame.Rect(((sw+82)  - btn_w) // 2, int(sh * 0.5), btn_w, btn_h)
    if username == "(not signed in)":
        pygame.draw.rect(screen, (70, 200, 70), _logout_rect, border_radius=16)
        label = font.render("Log In", True, (255, 255, 255))
    else:
        pygame.draw.rect(screen, (200, 70, 70), _logout_rect, border_radius=16)
        label = font.render("Log out", True, (255, 255, 255))
    screen.blit(label, (_logout_rect.centerx - label.get_width() // 2, _logout_rect.centery - label.get_height() // 2))

    # --- Upload floppy (right-bottom) ---
    _upload_pos = (int(sw * 0.90), int(sh * 0.90 - 75))
    screen.blit(floppy_disk_upload, _upload_pos)
    uw, uh = floppy_disk_upload.get_size()
    _upload_rect = pygame.Rect(_upload_pos[0], _upload_pos[1], uw, uh)

    now = pygame.time.get_ticks()
    if _upload_state["uploading"]:
        _update_upload_anim(now)
        # dots animation
        dw, dh = floppy_disk_dots.get_size()
        third = dw // 3
        x0, y0 = _upload_pos
        visible_count = 0 if _upload_state["anim_step"] == 3 else (_upload_state["anim_step"] + 1)
        if visible_count >= 1:
            screen.blit(floppy_disk_dots.subsurface(pygame.Rect(0, 0, third, dh)), (x0, y0))
        if visible_count >= 2:
            screen.blit(floppy_disk_dots.subsurface(pygame.Rect(third, 0, third, dh)), (x0 + third, y0))
        if visible_count >= 3:
            screen.blit(floppy_disk_dots.subsurface(pygame.Rect(third * 2, 0, third, dh)), (x0 + third * 2, y0))
    elif _upload_state["done"]:
        _draw_result_overlay(screen, _upload_state["ok"], _upload_pos, "upload")

    # --- Download floppy (left of upload) ---
    _download_pos = (int(sw * 0.80), int(sh * 0.90 - 75))
    screen.blit(floppy_disk_download, _download_pos)
    dw, dh = floppy_disk_download.get_size()
    _download_rect = pygame.Rect(_download_pos[0], _download_pos[1], dw, dh)

    if _download_state["downloading"]:
        # You can animate here too if you want (optional).
        pass
    elif _download_state["done"]:
        _draw_result_overlay(screen, _download_state["ok"], _download_pos, "download")

def logic_stats(event, page):
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        # Toggle auto-download
        if _auto_rect and _auto_rect.collidepoint(event.pos):
            new_val = not get_auto_download_flag()
            set_auto_download_flag(new_val)
            return page

        # Log in/out
        if _logout_rect and _logout_rect.collidepoint(event.pos):
            clear_credentials()
            return "login"

        # Start upload
        if _upload_rect and _upload_rect.collidepoint(event.pos) and not _upload_state["uploading"]:
            _upload_state["uploading"] = True
            _upload_state["done"] = False
            _upload_state["ok"] = False
            _upload_state["anim_step"] = 3
            _upload_state["next_tick_ms"] = pygame.time.get_ticks() + 500
            _upload_state["done_started_at"] = None
            _start_upload_thread()
            return page

        # Start download
        if _download_rect and _download_rect.collidepoint(event.pos):
            # Force the download state to "ready"
            _download_state["downloading"] = True
            _download_state["done"] = False
            _download_state["ok"] = False
            _download_state["done_started_at"] = None
            print("[settings] manual sync triggered")
            from copyparty_sync import download_data_json_if_present
            download_data_json_if_present()

            try:
                from main import sync_and_reload
                sync_and_reload(True)  # True = force download + reload
                _download_state["ok"] = True
            except Exception as e:
                print(f"[settings] sync failed: {e}")
                _download_state["ok"] = False
            finally:
                _download_state["downloading"] = False
                _download_state["done"] = True
                _download_state["done_started_at"] = None

            return page

    return page
    
