import os
import threading
import pygame

from state_data import _download_state

from drawing_functions.draw_rounded_button import draw_rounded_button
from drawing_functions.draw_input_box import draw_input_box, InputBox, logic_input_box
from themes import THEMES
from switch_themes import switch_theme

from copyparty_sync import (
    clear_credentials,
    get_current_user,
    upload_data_json,
    get_auto_download_flag,
    set_auto_download_flag,
    get_social_enabled_flag,
    set_social_enabled_flag,
)
from config import *

layout_heights = {
    "spoon_label":     0.32,
    "spoon_input_line":0.42,
    "rest_buttons":    0.65,
    "daily_prompt":    0.18,
}

days = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]

# --- InputBox registries for Settings tabs ---
spoons_input_boxes = {
    "Mon": InputBox(None, text="", multiline=False, fontsize=0.045, box_type="number"),
    "Tue": InputBox(None, text="", multiline=False, fontsize=0.045, box_type="number"),
    "Wed": InputBox(None, text="", multiline=False, fontsize=0.045, box_type="number"),
    "Thu": InputBox(None, text="", multiline=False, fontsize=0.045, box_type="number"),
    "Fri": InputBox(None, text="", multiline=False, fontsize=0.045, box_type="number"),
    "Sat": InputBox(None, text="", multiline=False, fontsize=0.045, box_type="number"),
    "Sun": InputBox(None, text="", multiline=False, fontsize=0.045, box_type="number"),
    "short": InputBox(None, text="", multiline=False, fontsize=0.045, box_type="number"),
    "half": InputBox(None, text="", multiline=False, fontsize=0.045, box_type="number"),
    "full": InputBox(None, text="", multiline=False, fontsize=0.045, box_type="number"),
    "time_per_spoon": InputBox(None, text="", multiline=False, fontsize=0.045, box_type="number"),
}

folders_input_boxes = {
    "folder_one": InputBox(None, text="", multiline=False, fontsize=0.05, box_type="text"),
    "folder_two": InputBox(None, text="", multiline=False, fontsize=0.05, box_type="text"),
    "folder_three": InputBox(None, text="", multiline=False, fontsize=0.05, box_type="text"),
    "folder_four": InputBox(None, text="", multiline=False, fontsize=0.05, box_type="text"),
    "folder_five": InputBox(None, text="", multiline=False, fontsize=0.05, box_type="text"),
    "folder_six": InputBox(None, text="", multiline=False, fontsize=0.05, box_type="text"),
    "folder_one_days": InputBox(None, text="", multiline=False, fontsize=0.05, box_type="number"),
    "folder_two_days": InputBox(None, text="", multiline=False, fontsize=0.05, box_type="number"),
    "folder_three_days": InputBox(None, text="", multiline=False, fontsize=0.05, box_type="number"),
    "folder_four_days": InputBox(None, text="", multiline=False, fontsize=0.05, box_type="number"),
    "folder_five_days": InputBox(None, text="", multiline=False, fontsize=0.05, box_type="number"),
    "folder_six_days": InputBox(None, text="", multiline=False, fontsize=0.05, box_type="number"),
}


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

_auto_rect = None  # toggle checkbox rect
_social_rect = None
_spoons_rect = None
_graphics_rect = None
_account_rect = None
_extensions_rect = None
_git_rect = None
_forks_rect = None
_knives_rect = None
_folders_rect = None
_sound_rect = None
_spoons_debt_rect = None
_spoons_debt_cons_rect = None

def get_image_brightness_color(image_surface):
    width = image_surface.get_width()
    height = image_surface.get_height()

    step = 10  # sample ~1% of pixels
    total_lum = 0
    count = 0

    w_r = 0.2126
    w_g = 0.7152
    w_b = 0.0722

    for x in range(0, width, step):
        for y in range(0, height, step):
            r, g, b, _ = image_surface.get_at((x, y))
            total_lum += (w_r*r + w_g*g + w_b*b)
            count += 1

    avg = total_lum / count

    return [BLACK,DARK_SLATE_GRAY] if avg > 60 else [WHITE,LIGHT_GRAY] #type: ignore

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

# track which tab is active
_active_settings_tab = "account"  # default tab

def draw_settings(screen, font, daily_spoons, input_active, sound_toggle, spoons_debt_toggle, spoons_debt_consequences_toggle, icon_image, manillaFolder_name, rest_spoons, time_per_spoon, v_number, reference_version, folder_days_ahead, *inventory_args):
    """
    Draws the Settings screen.
    Uses:
    - spoons_input_boxes for Spoons tab inputs
    - folders_input_boxes for Folders tab inputs
    """
    sw, sh = screen.get_size()
    day_font = pygame.font.Font("fonts/Stardew_Valley.ttf", int(sh * 0.045))
    global _logout_rect, _upload_rect, _upload_pos, _download_rect, _download_pos, _auto_rect, _social_rect
    global _active_settings_tab, _graphics_rect, _account_rect, _spoons_rect, _extensions_rect, _folders_rect, _sound_rect
    global _spoons_debt_rect, _spoons_debt_cons_rect
    global folder_days_rects
    global spoons_input_boxes, folders_input_boxes

    spoon_name_input, inventory_tab, background_color, folder_one, folder_two, folder_three, folder_four, folder_five, folder_six, folders_dropdown_open = inventory_args

    # --- Tab buttons ---
    tab_font = pygame.font.Font("fonts/Stardew_Valley.ttf", int(sh * 0.060))
    btn_w = 155
    btn_h = 45
    top_y = int(sh * 0.05)

    # Legacy rects (for click regions)
    total_tabs = 5
    total_width = total_tabs * btn_w + (total_tabs - 1)
    start_x_legacy = (sw - total_width) // 2 + 25

    account_rect = pygame.Rect(start_x_legacy + (btn_w) * 0, top_y, btn_w, btn_h)
    graphics_rect = pygame.Rect(start_x_legacy + (btn_w) * 1, top_y, btn_w, btn_h)
    spoons_rect = pygame.Rect(start_x_legacy + (btn_w) * 2, top_y, btn_w, btn_h)
    folders_rect = pygame.Rect(start_x_legacy + (btn_w) * 3, top_y, btn_w, btn_h)
    extensions_rect = pygame.Rect(start_x_legacy + (btn_w) * 4, top_y, btn_w, btn_h)
    sound_button_rect = pygame.Rect(sw - 80, 20, 60, 60)

    # --- Tab Labels with dynamic spacing ---
    tab_labels = ["Account", "Customization", "Spoons", "Folders", "Extensions"]
    start_x, end_x = 150, 850
    y_center = top_y + btn_h // 2

    text_widths = [tab_font.size(t)[0] for t in tab_labels]
    total_text_width = sum(text_widths)
    space = (end_x - start_x - total_text_width) / (len(tab_labels) - 1)

    tab_positions = []
    cur_x = start_x
    for width in text_widths:
        tab_positions.append(cur_x)
        cur_x += width + space

    for text, x_pos in zip(tab_labels, tab_positions):
        active = _active_settings_tab == text.lower() or (text == "Customization" and _active_settings_tab == "graphics")
        color = (0, 0, 0) if active else (40, 40, 40)
        label = tab_font.render(text, True, color)
        screen.blit(label, (x_pos, y_center - label.get_height() // 2))

    # --- Sound toggle button ---
    screen.blit(sound_button, sound_button_rect)
    if not sound_toggle:
        sx, sy = sound_button.get_size()
        redx = pygame.transform.smoothscale(floppy_disk_redx, (sx, sy))
        screen.blit(redx, sound_button_rect)

    _graphics_rect = graphics_rect
    _account_rect = account_rect
    _spoons_rect = spoons_rect
    _folders_rect = folders_rect
    _extensions_rect = extensions_rect
    _sound_rect = sound_button_rect

    # --- Separator line below tabs ---
    pygame.draw.line(screen, (0, 0, 0), (int(sw * 0.14), top_y + btn_h), (int(sw * 0.90), top_y + btn_h), 4)

    left_x = 575
    text_x = 150
    start_y = int(sh * 0.18)
    gap_y = 70
    scale = 0.80
    box_size = int(sh * 0.083)

    # --- Active tab content ---
    if _active_settings_tab == "graphics":
        if inventory_args:
            draw_inventory(screen, icon_image, manillaFolder_name, input_active, *inventory_args)

    elif _active_settings_tab == "account":
        username = get_current_user() or "(not signed in)"
        logged_in = username != "(not signed in)"
        user_surf = font.render(f"Signed in as: {username}", True, WHITE)  # type: ignore
        screen.blit(user_surf, (text_x, start_y + gap_y * 4))

        if v_number > reference_version:
            msg = f"Update available! {reference_version} > {v_number}"
        elif v_number < reference_version:
            msg = "Version mismatch (dev)"
        else:
            msg = f"Version {v_number}: Up to date!"
        label = font.render("Open GitHub Repo", True, WHITE)  # type: ignore
        sub = small_font.render(msg, True, GRAY)  # type: ignore
        screen.blit(label, (text_x, start_y + gap_y * 3))
        screen.blit(sub, (text_x, start_y + 28 + gap_y * 3))

        git_btn = pygame.Rect(left_x, start_y + gap_y * 3, 45, 45)
        pygame.draw.rect(screen, (70, 130, 180), git_btn, border_radius=8)
        screen.blit(toggleButtons["openLinkIcon"], (git_btn.x + 5, git_btn.y + 5))
        global _git_rect
        _git_rect = git_btn

        btn_w2, btn_h2 = int(sw * 0.25), int(sh * 0.10)
        _logout_rect = pygame.Rect(text_x, start_y + gap_y * 4 + 45, btn_w2, btn_h2)
        if username == "(not signed in)":
            pygame.draw.rect(screen, (70, 200, 70), _logout_rect, border_radius=16)
            label = font.render("Log In", True, (255, 255, 255))
        else:
            pygame.draw.rect(screen, (200, 70, 70), _logout_rect, border_radius=16)
            label = font.render("Log out", True, (255, 255, 255))
        screen.blit(label, (_logout_rect.centerx - label.get_width() // 2, _logout_rect.centery - label.get_height() // 2))

        label = font.render("Auto-Sync", True, WHITE)  # type: ignore
        screen.blit(label, (text_x, start_y))
        sub = small_font.render("Automatically syncs data from other devices", True, GRAY)  # type: ignore
        screen.blit(sub, (text_x, start_y + 28))

        _auto_rect = pygame.Rect(left_x, start_y, box_size, box_size)
        pygame.draw.rect(screen, (180, 180, 180), _auto_rect, width=3, border_radius=6)
        inner = pygame.Rect(_auto_rect.x, _auto_rect.y, _auto_rect.w, _auto_rect.h)
        if get_auto_download_flag():
            chk = pygame.transform.smoothscale(floppy_disk_checkmark, (inner.w, inner.h))
            screen.blit(chk, inner.topleft)
        else:
            rx = pygame.transform.smoothscale(floppy_disk_redx, (inner.w, inner.h))
            screen.blit(rx, inner.topleft)

        dw, dh = floppy_disk_download.get_size()
        redx_overlay = pygame.transform.scale(floppy_disk_redx, (dw * scale, dh * scale))
        label = font.render("Upload", True, WHITE)  # type: ignore
        screen.blit(label, (text_x, start_y + gap_y))
        sub = small_font.render("Saves your progress to the cloud", True, GRAY)  # type: ignore
        screen.blit(sub, (text_x, start_y + gap_y + 28))

        _upload_pos = (left_x, start_y + gap_y)
        uw, uh = floppy_disk_upload.get_size()
        floppy_disk_upload_small = pygame.transform.scale(floppy_disk_upload, (uw * scale, uh * scale))
        screen.blit(floppy_disk_upload_small, _upload_pos)
        if not logged_in:
            screen.blit(redx_overlay, _upload_pos)
        _upload_rect = pygame.Rect(_upload_pos[0], _upload_pos[1], uw * scale, uh * scale)

        label = font.render("Download", True, WHITE)  # type: ignore
        screen.blit(label, (text_x, start_y + gap_y * 2))
        sub = small_font.render("Retrieves your saved progress from the cloud", True, GRAY)  # type: ignore
        screen.blit(sub, (text_x, start_y + gap_y * 2 + 28))

        _download_pos = (left_x, start_y + gap_y * 2)
        floppy_disk_download_small = pygame.transform.scale(floppy_disk_download, (dw * scale, dh * scale))
        screen.blit(floppy_disk_download_small, _download_pos)
        if not logged_in:
            screen.blit(redx_overlay, _download_pos)
        _download_rect = pygame.Rect(_download_pos[0], _download_pos[1], dw * scale, dh * scale)

        now = pygame.time.get_ticks()
        if _upload_state["uploading"]:
            _update_upload_anim(now)
            dw2, dh2 = floppy_disk_dots.get_size()
            third = dw2 // 3
            x0, y0 = _upload_pos
            x0 = x0 - 5
            visible_count = 0 if _upload_state["anim_step"] == 3 else (_upload_state["anim_step"] + 1)
            if visible_count >= 1:
                screen.blit(floppy_disk_dots.subsurface(pygame.Rect(0, 0, third, dh2)), (x0, y0))
            if visible_count >= 2:
                screen.blit(floppy_disk_dots.subsurface(pygame.Rect(third, 0, third, dh2)), (x0 + third, y0))
            if visible_count >= 3:
                screen.blit(floppy_disk_dots.subsurface(pygame.Rect(third * 2, 0, third, dh2)), (x0 + third * 2, y0))
        elif _upload_state["done"]:
            _draw_result_overlay(screen, _upload_state["ok"], _upload_pos, "upload")

        if _download_state["done"]:
            _draw_result_overlay(screen, _download_state["ok"], _download_pos, "download")

    elif _active_settings_tab == "spoons":
        sw, sh = screen.get_size()
        input_gap_x = 10
        font_color = (255, 255, 255)
        sub_color = (180, 180, 180)

        # DAILY WAKE-UP SPOONS
        title = font.render("Daily Wake-up Spoons", True, font_color)
        screen.blit(title, (text_x, start_y))
        sub = small_font.render("Set how many spoons you wake up with", True, sub_color)
        screen.blit(sub, (text_x, start_y + 28))

        dy = start_y
        box_w, box_h = int(sw * 0.04), 30

        for i, day in enumerate(days):
            label = day_font.render(f"{day}:", True, font_color)
            lx = left_x + i * (box_w + input_gap_x)
            screen.blit(label, (lx, dy))
            input_rect = pygame.Rect(left_x + i * (box_w + input_gap_x), dy + 27, box_w, box_h)
            box = spoons_input_boxes[day]
            box.rect = input_rect
            if not box.initialized:
                box.text = str(daily_spoons.get(day, 0))
                box.initialized = True
            box.active = (input_active == day)
            draw_input_box(screen, box, LIGHT_GRAY, DARK_SLATE_GRAY, background_color=background_color, infill="light")  # type: ignore

        # REST SPOONS
        rest_y = dy + 65
        title = font.render("Rest Spoons", True, font_color)
        screen.blit(title, (text_x, rest_y))
        sub = small_font.render("The number of spoons you get from resting", True, sub_color)
        screen.blit(sub, (text_x, rest_y + 28))

        rest_labels = ["Short Rest", "Half Rest", "Full Rest"]
        rest_keys = ["short", "half", "full"]
        rest_y += 5
        rest_box_w = int(sw * 0.08)
        rest_gap = 40

        for i, key in enumerate(rest_keys):
            r_label = rest_labels[i]
            lx = left_x + i * (rest_box_w + rest_gap)
            label = day_font.render(r_label, True, font_color)
            screen.blit(label, (lx, rest_y))
            input_rect = pygame.Rect(lx, rest_y + 27, rest_box_w, box_h)
            box = spoons_input_boxes[key]
            box.rect = input_rect
            if not box.initialized:
                box.text = str(rest_spoons.get(key, 0))
                box.initialized = True
            box.active = (input_active == key)
            draw_input_box(screen, box, LIGHT_GRAY, DARK_SLATE_GRAY, background_color=background_color, infill="light")  # type: ignore

        # TIME PER SPOON
        tps_y = rest_y + 65
        label = font.render("Time per Spoon", True, font_color)
        sub = small_font.render("Spoon to minute ratio (used in timers)", True, sub_color)
        input_w = int(sw * 0.08)
        input_rect = pygame.Rect(left_x, tps_y + 20, input_w, box_h)
        box = spoons_input_boxes["time_per_spoon"]
        box.rect = input_rect
        if not box.initialized:
            box.text = str(time_per_spoon)
            box.initialized = True
        box.active = (input_active == "time_per_spoon")
        draw_input_box(screen, box, LIGHT_GRAY, DARK_SLATE_GRAY, background_color=background_color, infill="light")  # type: ignore
        screen.blit(label, (text_x, tps_y))
        screen.blit(sub, (text_x, tps_y + 28))

        # ENABLE SPOONS DEBT
        debt_y = tps_y + gap_y
        debt_label = font.render("Enable Spoons Debt", True, font_color)
        sub = small_font.render("Allows your spoons to go negative", True, sub_color)
        screen.blit(debt_label, (text_x, debt_y))
        screen.blit(sub, (text_x, debt_y + 28))
        _spoons_debt_rect = pygame.Rect(left_x, debt_y, box_size, box_size)
        pygame.draw.rect(screen, (180, 180, 180), _spoons_debt_rect, width=3, border_radius=6)
        if spoons_debt_toggle:
            chk = pygame.transform.smoothscale(floppy_disk_checkmark, (box_size, box_size))
            screen.blit(chk, _spoons_debt_rect.topleft)
        else:
            rx = pygame.transform.smoothscale(floppy_disk_redx, (box_size, box_size))
            screen.blit(rx, _spoons_debt_rect.topleft)

        # SPOONS DEBT CONSEQUENCES
        cons_y = debt_y + gap_y
        cons_label = font.render("Spoons Debt Consequences", True, font_color)
        sub = small_font.render("Negative spoons roll over to next day", True, sub_color)
        screen.blit(cons_label, (text_x, cons_y))
        screen.blit(sub, (text_x, cons_y + 28))
        _spoons_debt_cons_rect = pygame.Rect(left_x, cons_y, box_size, box_size)
        pygame.draw.rect(screen, (180, 180, 180), _spoons_debt_cons_rect, width=3, border_radius=6)
        if spoons_debt_consequences_toggle:
            chk = pygame.transform.smoothscale(floppy_disk_checkmark, (box_size, box_size))
            screen.blit(chk, _spoons_debt_cons_rect.topleft)
        else:
            rx = pygame.transform.smoothscale(floppy_disk_redx, (box_size, box_size))
            screen.blit(rx, _spoons_debt_cons_rect.topleft)

    elif _active_settings_tab == "extensions":
        global _social_rect, _forks_rect, _knives_rect
        label = font.render("Social Features", True, WHITE)  # type: ignore
        sub = small_font.render("Enable leaderboards and friend stats", True, GRAY)  # type: ignore
        screen.blit(label, (text_x, start_y))
        screen.blit(sub, (text_x, start_y + 28))
        _social_rect = pygame.Rect(left_x, start_y, box_size, box_size)
        pygame.draw.rect(screen, (180, 180, 180), _social_rect, width=3, border_radius=6)
        if get_social_enabled_flag():
            chk = pygame.transform.smoothscale(floppy_disk_checkmark, (box_size, box_size))
            screen.blit(chk, _social_rect.topleft)
        else:
            rx = pygame.transform.smoothscale(floppy_disk_redx, (box_size, box_size))
            screen.blit(rx, _social_rect.topleft)

        f_y = start_y + gap_y
        label = font.render("Forks Extension", True, WHITE)  # type: ignore
        sub = small_font.render("Enable shopping list extension", True, GRAY)  # type: ignore
        screen.blit(label, (text_x, f_y))
        screen.blit(sub, (text_x, f_y + 28))
        _forks_rect = pygame.Rect(left_x, f_y, box_size, box_size)
        pygame.draw.rect(screen, (180, 180, 180), _forks_rect, width=3, border_radius=6)

        k_y = f_y + gap_y
        label = font.render("Knives Extension", True, WHITE)  # type: ignore
        sub = small_font.render("Enable workout tracker extension", True, GRAY)  # type: ignore
        screen.blit(label, (text_x, k_y))
        screen.blit(sub, (text_x, k_y + 28))
        _knives_rect = pygame.Rect(left_x, k_y, box_size, box_size)
        pygame.draw.rect(screen, (180, 180, 180), _knives_rect, width=3, border_radius=6)

    elif _active_settings_tab == "folders":
        sw, sh = screen.get_size()
        font_color = (255, 255, 255)
        box_w, box_h = 180, 40
        gap_y_small = 55
        days_box_size = 40
        days_box_gap = 120

        labels = [
            ("Folder 1", folder_one),
            ("Folder 2", folder_two),
            ("Folder 3", folder_three),
            ("Folder 4", folder_four),
            ("Folder 5", folder_five),
            ("Folder 6", folder_six),
        ]

        title = font.render("Folder Name      Summary Days Ahead", True, font_color)
        screen.blit(title, (text_x, start_y))

        folder_days_rects = []

        base_keys = ["folder_one", "folder_two", "folder_three", "folder_four", "folder_five", "folder_six"]

        for i, (label_text, folder_val) in enumerate(labels):
            y = start_y + 40 + i * gap_y_small
            base_key = base_keys[i]

            folder_rect = pygame.Rect(text_x, y, box_w, box_h)
            name_box = folders_input_boxes[base_key]
            name_box.rect = folder_rect
            if not name_box.initialized:
                name_box.text = str(folder_val)
                name_box.initialized = True
            name_box.active = (input_active == base_key)
            draw_input_box(screen, name_box, LIGHT_GRAY, DARK_SLATE_GRAY, background_color=background_color, infill="light")  # type: ignore

            days_rect = pygame.Rect(text_x + box_w + days_box_gap, y, days_box_size, days_box_size)
            folder_days_rects.append(days_rect)
            days_key = f"{base_key}_days"
            days_box = folders_input_boxes[days_key]
            days_box.rect = days_rect
            if not days_box.initialized:
                days_box.text = str(folder_days_ahead.get(base_key, 7))
                days_box.initialized = True
            days_box.active = (input_active == f"{base_key}_days")
            draw_input_box(screen, days_box, LIGHT_GRAY, DARK_SLATE_GRAY, background_color=background_color, infill="light")  # type: ignore

def logic_settings(event, page, daily_spoons, input_active, sound_toggle, spoons_debt_toggle, spoons_debt_consequences_toggle, rest_spoons, time_per_spoon, folder_days_ahead, manilla_folder_text_color, *inventory_args):
    """Handles tab switching and settings logic, using InputBox registries for Spoons and Folders tabs."""
    global _active_settings_tab
    global spoons_input_boxes, folders_input_boxes
    sh, sw = pygame.display.get_surface().get_size()

    updated = list(inventory_args)

    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        # let input boxes detect clicks for focusing/defocusing
        if _active_settings_tab == "spoons":
            for box in spoons_input_boxes.values():
                logic_input_box(event, box, pygame.display.get_surface())
                input_active = None

        elif _active_settings_tab == "folders":
            for box in folders_input_boxes.values():
                logic_input_box(event, box, pygame.display.get_surface())
                input_active = None

        # --- Tab clicks ---
        if _graphics_rect and _graphics_rect.collidepoint(event.pos):
            _active_settings_tab = "graphics"
        if _account_rect and _account_rect.collidepoint(event.pos):
            _active_settings_tab = "account"
        if _spoons_rect and _spoons_rect.collidepoint(event.pos):
            _active_settings_tab = "spoons"
        if _folders_rect and _folders_rect.collidepoint(event.pos):
            _active_settings_tab = "folders"
        if _extensions_rect and _extensions_rect.collidepoint(event.pos):
            _active_settings_tab = "extensions"

        # --- Folders tab input focus (names + days-ahead) ---
        if _active_settings_tab == "folders":
            sw, sh = pygame.display.get_surface().get_size()
            text_x = 150
            start_y = int(sh * 0.18)
            box_w, box_h = 180, 40
            gap_y_small = 55
            days_box_size = 40
            days_box_gap = 120

            name_rects = []
            for i in range(6):
                y = start_y + 40 + i * gap_y_small
                name_rects.append(pygame.Rect(text_x, y, box_w, box_h))

            try:
                _ = folder_days_rects
            except NameError:
                # fallback if draw_settings hasn't filled them yet
                folder_days_rects_local = []
                for i in range(6):
                    y = start_y + 40 + i * gap_y_small
                    folder_days_rects_local.append(pygame.Rect(text_x + box_w + days_box_gap, y, days_box_size, days_box_size))
                globals()["folder_days_rects"] = folder_days_rects_local
            folder_keys = ["folder_one", "folder_two", "folder_three", "folder_four", "folder_five", "folder_six"]

            clicked_any = False
            for i, r in enumerate(name_rects):
                if r.collidepoint(event.pos):
                    input_active = folder_keys[i]
                    for k, box in folders_input_boxes.items():
                        box.active = (k == input_active)
                    clicked_any = True
                    break

            if not clicked_any:
                for i, r in enumerate(folder_days_rects):
                    if r.collidepoint(event.pos):
                        input_active = f"{folder_keys[i]}_days"
                        for k, box in folders_input_boxes.items():
                            box.active = (k == input_active)
                        clicked_any = True
                        break

            if clicked_any:
                return (page, daily_spoons, input_active, sound_toggle, spoons_debt_toggle, spoons_debt_consequences_toggle, rest_spoons, time_per_spoon, folder_days_ahead, manilla_folder_text_color, *updated)

        # --- Global Sound toggle ---
        if _sound_rect and _sound_rect.collidepoint(event.pos):
            sound_toggle = not sound_toggle

        # --- Account tab logic ---
        username = get_current_user() or "(not signed in)"
        logged_in = username != "(not signed in)"
        if _active_settings_tab == "account":
            if not logged_in:
                set_auto_download_flag(False)
            if _auto_rect and _auto_rect.collidepoint(event.pos) and logged_in:
                new_val = not get_auto_download_flag()
                set_auto_download_flag(new_val)

            if _logout_rect and _logout_rect.collidepoint(event.pos):
                clear_credentials()
                return ("login", daily_spoons, input_active, sound_toggle, spoons_debt_toggle, spoons_debt_consequences_toggle, rest_spoons, time_per_spoon, folder_days_ahead, manilla_folder_text_color, *updated)

            if _upload_rect and _upload_rect.collidepoint(event.pos) and not _upload_state["uploading"] and logged_in:
                _upload_state["uploading"] = True
                _upload_state["done"] = False
                _upload_state["ok"] = False
                _upload_state["anim_step"] = 3
                _upload_state["next_tick_ms"] = pygame.time.get_ticks() + 500
                _upload_state["done_started_at"] = None
                _start_upload_thread()

            if _download_rect and _download_rect.collidepoint(event.pos) and logged_in:
                _download_state["downloading"] = True
                _download_state["done"] = False
                _download_state["ok"] = False
                _download_state["done_started_at"] = None
                from copyparty_sync import download_data_json_if_present
                download_data_json_if_present()
                _download_state["trigger_download"] = True

            if _git_rect and _git_rect.collidepoint(event.pos):
                import webbrowser
                try:
                    webbrowser.open("https://github.com/VladStol223/Spoons/tree/main")
                except Exception as e:
                    print(f"Could not open web browser: {e}")

        # Inventory logic on Graphics tab
        if _active_settings_tab == "graphics" and inventory_args:
            input_active, manilla_folder_text_color, *updated = logic_inventory(event, input_active, manilla_folder_text_color, *inventory_args)

        # --- Spoons tab toggles + focus ---
        if _active_settings_tab == "spoons":
            clicked_any = False
            # toggles
            if _spoons_debt_rect and _spoons_debt_rect.collidepoint(event.pos):
                spoons_debt_toggle = not spoons_debt_toggle
                clicked_any = True
            if _spoons_debt_cons_rect and _spoons_debt_cons_rect.collidepoint(event.pos):
                spoons_debt_consequences_toggle = not spoons_debt_consequences_toggle
                clicked_any = True

            # daily / rest / time inputs (rects must match draw_settings)
            sw, sh = pygame.display.get_surface().get_size()
            text_x = 150
            left_x = 575
            dy = int(sh * 0.18)
            box_w, box_h = int(sw * 0.04), 30
            input_gap_x = 10

            # daily
            for i, day in enumerate(days):
                rect = pygame.Rect(left_x + i * (box_w + input_gap_x), dy + 27, box_w, box_h)
                if rect.collidepoint(event.pos):
                    input_active = day
                    for k, box in spoons_input_boxes.items():
                        box.active = (k == input_active)
                    return (page, daily_spoons, input_active, sound_toggle, spoons_debt_toggle, spoons_debt_consequences_toggle, rest_spoons, time_per_spoon, folder_days_ahead, manilla_folder_text_color, *updated)

            # rest
            rest_y = dy + 65 + 5
            rest_box_w = int(sw * 0.08)
            rest_gap = 40
            for i, key in enumerate(["short", "half", "full"]):
                lx = left_x + i * (rest_box_w + rest_gap)
                rect = pygame.Rect(lx, rest_y + 27, rest_box_w, box_h)
                if rect.collidepoint(event.pos):
                    input_active = key
                    for k, box in spoons_input_boxes.items():
                        box.active = (k == input_active)
                    return (page, daily_spoons, input_active, sound_toggle, spoons_debt_toggle, spoons_debt_consequences_toggle, rest_spoons, time_per_spoon, folder_days_ahead, manilla_folder_text_color, *updated)

            # time per spoon
            tps_y = rest_y + 65
            input_w = int(sw * 0.08)
            rect_tps = pygame.Rect(left_x, tps_y + 20, input_w, box_h)
            if rect_tps.collidepoint(event.pos):
                input_active = "time_per_spoon"
                for k, box in spoons_input_boxes.items():
                    box.active = (k == input_active)
                return (page, daily_spoons, input_active, sound_toggle, spoons_debt_toggle, spoons_debt_consequences_toggle, rest_spoons, time_per_spoon, folder_days_ahead, manilla_folder_text_color, *updated)

        if _active_settings_tab == "extensions":
            if _social_rect and _social_rect.collidepoint(event.pos):
                new_val = not get_social_enabled_flag()
                set_social_enabled_flag(new_val)
            if _forks_rect and _forks_rect.collidepoint(event.pos):
                print("Forks toggle clicked (not implemented)")
            if _knives_rect and _knives_rect.collidepoint(event.pos):
                print("Knives toggle clicked (not implemented)")

    elif event.type == pygame.KEYDOWN:
        # Route typing into InputBoxes and then sync back to settings data
        surf = pygame.display.get_surface()

        if _active_settings_tab == "spoons":
            # Let InputBoxes update their text
            for box in spoons_input_boxes.values():
                logic_input_box(event, box, surf)

            # Sync daily spoons
            for day in days:
                txt = (spoons_input_boxes[day].text or "").strip()
                if txt.isdigit():
                    daily_spoons[day] = int(txt)
                elif txt == "":
                    daily_spoons[day] = 0

            # Sync rest spoons
            for key in ("short", "half", "full"):
                txt = (spoons_input_boxes[key].text or "").strip()
                if txt.isdigit():
                    rest_spoons[key] = int(txt)

            # Sync time_per_spoon (min 1)
            txt = (spoons_input_boxes["time_per_spoon"].text or "").strip()
            if txt.isdigit():
                val = int(txt)
                time_per_spoon = max(1, val)

        elif _active_settings_tab == "folders":
            for box in folders_input_boxes.values():
                logic_input_box(event, box, surf)

            idx_map = {
                "folder_one": 3,
                "folder_two": 4,
                "folder_three": 5,
                "folder_four": 6,
                "folder_five": 7,
                "folder_six": 8,
            }
            for key, idx in idx_map.items():
                updated[idx] = folders_input_boxes[key].text or ""

            for base_key in ("folder_one", "folder_two", "folder_three", "folder_four", "folder_five", "folder_six"):
                days_key = f"{base_key}_days"
                txt = (folders_input_boxes[days_key].text or "").strip()
                if txt.isdigit():
                    folder_days_ahead[base_key] = max(0, int(txt))

    if _active_settings_tab == "folders":
        updated[3:9] = [updated[3], updated[4], updated[5], updated[6], updated[7], updated[8]]

    return (page, daily_spoons, input_active, sound_toggle, spoons_debt_toggle, spoons_debt_consequences_toggle, rest_spoons, time_per_spoon, folder_days_ahead, manilla_folder_text_color, *updated)




select_folder_font = pygame.font.Font("fonts/Stardew_Valley.ttf", int(screen_height * 0.055))

folder_input_box_x = 750
folder_input_box_y = 145
folder_padding = 40

folder_one_name_input_box = pygame.Rect(folder_input_box_x, folder_input_box_y + folder_padding, 150, 40)
folder_two_name_input_box = pygame.Rect(folder_input_box_x , folder_input_box_y + folder_padding * 2, 150, 40)
folder_three_name_input_box = pygame.Rect(folder_input_box_x, folder_input_box_y + folder_padding * 3, 150, 40)
folder_four_name_input_box = pygame.Rect(folder_input_box_x, folder_input_box_y + folder_padding * 4, 150, 40)
folder_five_name_input_box = pygame.Rect(folder_input_box_x, folder_input_box_y + folder_padding * 5, 150, 40)
folder_six_name_input_box = pygame.Rect(folder_input_box_x, folder_input_box_y + folder_padding * 6, 150, 40)

folder_dropdown_rect   = pygame.Rect(folder_input_box_x, 145, 150, 40)
folders_dropdown_open  = False    # new state flag

icons_x = 120
inventory_tab_x = 210

icon_tab_box = pygame.Rect(icons_x, 145, 48, 48)
folder_tab_box = pygame.Rect(icons_x, 215, 48, 48)
theme_tab_box = pygame.Rect(icons_x, 285, 48, 48)
border_tab_box = pygame.Rect(icons_x, 355, 48, 48)
extra_tab_box = pygame.Rect(icons_x, 425, 48, 48)

#themes
aquatic_theme = pygame.Rect(290, 180, 40, 30)
foresty_theme = pygame.Rect(290, 220, 40, 30)
girly_pop_theme = pygame.Rect(290, 260, 40, 30)
vampire_goth_theme = pygame.Rect(290, 300, 40, 30)
sunset_glow_theme = pygame.Rect(290, 340, 40, 30)
#extra themes
light_academia_theme = pygame.Rect(230, 180, 40, 30)
retro_theme = pygame.Rect(230, 220, 40, 30)
minimalist_theme = pygame.Rect(230, 260, 40, 30)
cosmic_theme = pygame.Rect(230, 300, 40, 30)
autumn_harvest_theme = pygame.Rect(230, 340, 40, 30)
tropical_oasis_theme = pygame.Rect(230, 380, 40, 30)
pastel_dreams_theme = pygame.Rect(230, 420, 40, 30)
steampunk_theme = pygame.Rect(230, 460, 40, 30)

#settings page
spoon_name_input_box = pygame.Rect(750, 140, 150, 40)



icon_surfaces = [
    spoon_image,
    star_image,
    mike_image,
    minecraft_image,
    stardew_image,
    celeste_image,
    minecraft1_image,
    ]


theme_colors = [
    "aquatic",
    "foresty",
    "girly_pop",
    "vampire_goth",
    "sunset_glow",
    "light_academia",
    "retro",
    "minimalist",
    "cosmic",
    "autumn_harvest",
    "tropical_oasis",
    "pastel_dreams",
    "steampunk"
]

border_surfaces = [
    [defaultEdgeOne, 'default'],
    [oakWoodEdgeOne, 'oakWood'],
    [darkOakWoodEdgeOne, 'darkOakWood'],
    [metalEdgeOne, 'metal'],
    [birchWoodEdgeOne, 'birchWood'],
    [spruceWoodEdgeOne, 'spruceWood'],
    [grayWoodEdgeOne, 'grayWood'],
]

folder_surfaces = [
    [defaultManillaFolder, 'default'],
    [darkManillaFolder, 'dark'],
    [lightManillaFolder, 'light'],
    [blueManillaFolder, 'blue'],
    [greenManillaFolder, 'green'],
    [pinkManillaFolder, 'pink'],
    [lightBlueManillaFolder, 'light_blue'],
    [paleGreenManillaFolder, 'pale_green'],
]

def to_color(val):
    # 1) A tuple/list of ints?
    if isinstance(val, (list, tuple)):
        # if it’s the placeholder (negative or >255), treat as transparent
        if any((not isinstance(c, int) or c < 0 or c > 255) for c in val):
            return pygame.Color(0, 0, 0, 0)
        # otherwise it’s a valid RGB or RGBA
        if len(val) in (3, 4):
            return tuple(val)

    # 2) A string matching one of your named COLORS?
    if isinstance(val, str) and val in COLORS:
        return COLORS[val]

    # 3) A raw hex/CSS name or pygame.Color
    if isinstance(val, str):
        try:
            return pygame.Color(val)
        except Exception:
            raise ValueError(f"Cannot convert '{val}' to a color")

    if isinstance(val, pygame.Color):
        return val

    raise TypeError(f"Unsupported color format: {val!r}")

def draw_inventory(
    screen,
    icon_image,
    manillaFolder_name,
    input_active,
    spoon_name_input,
    inventory_tab,
    background_color,
    folder_one,
    folder_two,
    folder_three,
    folder_four,
    folder_five,
    folder_six,
    folders_dropdown_open
):

    r, g, b = background_color
    darker_background   = (max(r - 40, 0), max(g - 40, 0), max(b - 40, 0))
    light_background    = (min(r + 20, 255), min(g + 20, 255), min(b + 20, 255))
    lighter_background  = (min(r + 40, 255), min(g + 40, 255), min(b + 40, 255))

    # load & scale each icon
    icons_icon    = inventoryIcons['icons']
    scaled_icons  = pygame.transform.scale(icons_icon,   (48, 48))
    icons_folders = inventoryIcons['folders']
    scaled_folders = pygame.transform.scale(icons_folders, (48, 48))
    icons_themes  = inventoryIcons['themes']
    scaled_themes = pygame.transform.scale(icons_themes,  (48, 48))
    icons_borders = inventoryIcons['borders']
    scaled_borders = pygame.transform.scale(icons_borders, (48, 48))
    icons_extras  = inventoryIcons['extras']
    scaled_extras = pygame.transform.scale(icons_extras,  (48, 48))

    # each tab: (name, hit-box, surface)
    tabs = [
        ("Icons",   icon_tab_box,   scaled_icons),
        ("Folders", folder_tab_box, scaled_folders),
        ("Themes",  theme_tab_box,  scaled_themes),
        ("Borders", border_tab_box, scaled_borders),
        ("Extra",   extra_tab_box,  scaled_extras),
    ]

    circle_padding = 5

    square_width = 80

    Title_y = 100
    Box_start_y = 160

    for i in range(7):
        for j in range(3):
            pygame.draw.rect(screen, lighter_background, (220 + 100 * i, Box_start_y + 100 * j, square_width, square_width))
            pygame.draw.rect(screen, darker_background, (220 + 100 * i, Box_start_y + 100 * j, square_width, square_width), 4)

    for name, rect, surf in tabs:
        center = rect.center
        radius = surf.get_width() // 2 + circle_padding
        is_sel = (inventory_tab == name)

        # draw selection circle if needed
        if is_sel:
            pygame.draw.circle(screen, lighter_background, center, radius)

        # pick tint
        tint = darker_background if is_sel else lighter_background

        # tint the white icon, preserve per-pixel alpha
        icon_t = surf.copy()
        icon_t.fill(tint, special_flags=pygame.BLEND_RGBA_MULT)

        # blit tinted icon
        screen.blit(icon_t, icon_t.get_rect(center=center))


    if inventory_tab == "Icons":
        inventory_icon_buttons.clear()

        icon_prompt = bigger_font.render("ICONS", True, BLACK)# type: ignore
        screen.blit(icon_prompt, (inventory_tab_x, Title_y))

        #icon_name_prompt = font.render("Icon Name:", True, BLACK)# type: ignore
        #screen.blit(icon_name_prompt, (spoon_name_input_box.left - icon_name_prompt.get_width() - 5, 145))
        #draw_input_box(screen, spoon_name_input_box, input_active == "spoon_name", spoon_name_input, LIGHT_GRAY, DARK_SLATE_GRAY, False, background_color, "light", 5)#type: ignore


        icon_width = square_width - 15

        for idx, icon in enumerate(icon_surfaces):
            col = idx % 7
            row = idx // 7
            if row >= 3:
                break

            cell_x = 220 + 100 * col
            cell_y = Box_start_y + 100 * row
            outline = pygame.Rect(cell_x, cell_y, square_width, square_width)

            # store for the click logic
            inventory_icon_buttons.append((outline, icon))

            # draw the button
            draw_rounded_button(
                screen,
                outline,
                background_color if icon_image == icon else lighter_background,
                darker_background,
                1, 2
            )

            # scale & blit the icon
            scaled_icon = pygame.transform.scale(icon, (icon_width, icon_width))
            icon_rect   = scaled_icon.get_rect(center=outline.center)
            screen.blit(scaled_icon, icon_rect)

    elif inventory_tab == "Folders":
        inventory_folder_buttons.clear()
        rename_folders_text = bigger_font.render("FOLDERS", True, BLACK)# type: ignore
        screen.blit(rename_folders_text, (inventory_tab_x,Title_y))

        icon_width = square_width - 15

        for idx, (surface, name) in enumerate(folder_surfaces):
            col = idx % 7
            row = idx // 7
            if row >= 3:
                break
            cell_x = 220 + 100 * col
            cell_y = Box_start_y + 100 * row
            outline = pygame.Rect(cell_x, cell_y, square_width, square_width)
            inventory_folder_buttons.append((outline, surface, name))
            draw_rounded_button(screen, outline, background_color if manillaFolder_name == name else lighter_background, darker_background, 1, 2)
            scaled  = pygame.transform.scale(surface, (icon_width, (icon_width//5)*3))
            rect    = scaled.get_rect(center=outline.center)
            screen.blit(scaled, rect)

    elif inventory_tab == "Themes":
        inventory_themes_buttons.clear()
        rename_folders_text = bigger_font.render("THEMES", True, BLACK)# type: ignore
        screen.blit(rename_folders_text, (inventory_tab_x,Title_y))

        for idx, theme_key in enumerate(theme_colors):
            col = idx % 7
            row = idx // 7
            # stop after two rows of 7 (you have 13 themes)
            if row >= 2:
                break

            cell_x = 220 + 100 * col
            cell_y = Box_start_y + 100 * row
            cell_rect = pygame.Rect(cell_x, cell_y, square_width, square_width)
            inventory_themes_buttons.append((cell_rect, theme_key))

        # — In your draw pass, render each theme-swatch
        for cell_rect, theme_key in inventory_themes_buttons:
            # draw the outline/frame
            draw_rounded_button(
                screen,
                cell_rect,
                lighter_background,
                darker_background,  # type: ignore
                1, 2
            )

            # grab the four quarter-colors from your THEMES dict
            theme_dict = THEMES[theme_key]
            tl = to_color(theme_dict["background_color"])
            tr = to_color(theme_dict["calendar_current_day_color"])
            bl = to_color(theme_dict["calendar_previous_day_color"])
            br = to_color(theme_dict["calendar_next_day_color"])

            # compute halves
            padding = 8
            hw = cell_rect.width // 2 - (padding * 2)
            hh = cell_rect.height // 2 - (padding * 2)
            

            # top-left quarter
            pygame.draw.rect(screen, tl, pygame.Rect(cell_rect.x + (padding*2),         cell_rect.y + (padding*2),          hw, hh))
            # top-right quarter
            pygame.draw.rect(screen, tr, pygame.Rect(cell_rect.x + hw + (padding*2),    cell_rect.y + (padding*2),          hw, hh))
            # bottom-left quarter
            pygame.draw.rect(screen, bl, pygame.Rect(cell_rect.x + (padding*2),         cell_rect.y + hh + (padding*2),     hw, hh))
            # bottom-right quarter
            pygame.draw.rect(screen, br, pygame.Rect(cell_rect.x + hw + (padding*2),    cell_rect.y + hh + (padding*2),     hw, hh))


    elif inventory_tab == "Borders":
        inventory_border_buttons.clear()
        rename_folders_text = bigger_font.render("BORDERS", True, BLACK)# type: ignore
        screen.blit(rename_folders_text, (inventory_tab_x,Title_y))

        icon_width = square_width - 15

        for idx, (surface, name) in enumerate(border_surfaces):
            col = idx % 7
            row = idx // 7
            if row >= 3:
                break
            cell_x = 220 + 100 * col
            cell_y = Box_start_y + 100 * row
            outline = pygame.Rect(cell_x, cell_y, square_width, square_width)
            inventory_border_buttons.append((outline, surface, name))
            draw_rounded_button(screen, outline, lighter_background, darker_background, 1, 2)
            rotated = pygame.transform.rotate(surface, 90)
            scaled  = pygame.transform.scale(rotated, (icon_width, icon_width//3))
            rect    = scaled.get_rect(center=outline.center)
            screen.blit(scaled, rect)


def logic_inventory(event,
                    input_active,
                    manilla_folder_text_color,
                    inventory_tab,
                    spoon_name_input,
                    icon_image,
                    folder_one,
                    folder_two,
                    folder_three,
                    folder_four,
                    folder_five,
                    folder_six,
                    folders_dropdown_open,
                    border, border_name,
                    manillaFolder, manillaFolder_name,
                    current_theme):

    if event.type == pygame.MOUSEBUTTONDOWN:
        mx, my = event.pos
        clicked_any = False

        # 1) Tab switching first
        if icon_tab_box.collidepoint(mx, my):
            inventory_tab = "Icons"; clicked_any = True
        elif folder_tab_box.collidepoint(mx, my):
            inventory_tab = "Folders"; clicked_any = True
        elif theme_tab_box.collidepoint(mx, my):
            inventory_tab = "Themes"; clicked_any = True
        elif border_tab_box.collidepoint(mx, my):
            inventory_tab = "Borders"; clicked_any = True
        elif extra_tab_box.collidepoint(mx, my):
            inventory_tab = "Extras"; clicked_any = True

        # 2) Per-tab interactions & focus (AFTER tab state updates)
        # Icons tab
        if inventory_tab == "Icons":
            global spoon_name_input_box
            if spoon_name_input_box.collidepoint(mx, my):
                #input_active = "spoon_name"
                clicked_any = True
            for outline, icon in inventory_icon_buttons:
                if outline.collidepoint(mx, my):
                    icon_image = icon
                    clicked_any = True
                    break

        # Folders tab
        if inventory_tab == "Folders":
            for outline, surface, name in inventory_folder_buttons:
                if outline.collidepoint(mx, my):
                    manillaFolder, manillaFolder_name = set_image('manillaFolder', name)
                    manilla_folder_text_color = get_image_brightness_color(manillaFolder["manilla_folder"])
                    clicked_any = True
                    break

            # when open, focus the appropriate input box
            if folders_dropdown_open:
                global folder_one_name_input_box, folder_two_name_input_box, folder_three_name_input_box
                global folder_four_name_input_box, folder_five_name_input_box, folder_six_name_input_box
                if folder_one_name_input_box.collidepoint(mx, my):
                    input_active = "folder_one"
                    clicked_any = True
                elif folder_two_name_input_box.collidepoint(mx, my):
                    input_active = "folder_two"
                    clicked_any = True
                elif folder_three_name_input_box.collidepoint(mx, my):
                    input_active = "folder_three"
                    clicked_any = True
                elif folder_four_name_input_box.collidepoint(mx, my):
                    input_active = "folder_four"
                    clicked_any = True
                elif folder_five_name_input_box.collidepoint(mx, my):
                    input_active = "folder_five"
                    clicked_any = True
                elif folder_six_name_input_box.collidepoint(mx, my):
                    input_active = "folder_six"
                    clicked_any = True

        # Themes tab
        if inventory_tab == "Themes":
            for cell_rect, theme_key in inventory_themes_buttons:
                if cell_rect.collidepoint(mx, my):
                    current_theme = switch_theme(theme_key, globals())
                    clicked_any = True
                    break

        # Borders tab
        if inventory_tab == "Borders":
            for outline, surface, name in inventory_border_buttons:
                if outline.collidepoint(mx, my):
                    border, border_name = set_image('border', name)
                    clicked_any = True
                    break

        # 3) If this click didn't hit any actionable control, clear focus
        if not clicked_any:
            input_active = ""


    return (input_active,
            manilla_folder_text_color,
            inventory_tab,
            spoon_name_input,
            icon_image,
            folder_one,
            folder_two,
            folder_three,
            folder_four,
            folder_five,
            folder_six,
            folders_dropdown_open,
            border, border_name,
            manillaFolder, manillaFolder_name,
            current_theme)