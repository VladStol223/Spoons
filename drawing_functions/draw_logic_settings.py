import os
import threading
import pygame

from state_data import _download_state

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
_sound_rect = None
_spoons_debt_rect = None
_spoons_debt_cons_rect = None

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

def draw_settings(screen, font, daily_spoons, input_active, sound_toggle, spoons_debt_toggle, spoons_debt_consequences_toggle, icon_image, manillaFolder_name, *inventory_args):
    """
    Draws the Settings screen, which now contains two tabs:
    'Graphics Settings' (shows Inventory UI)
    'Account Settings' (shows current Settings UI)
    """
    sw, sh = screen.get_size()
    prompt_font = pygame.font.Font("fonts/Stardew_Valley.ttf", int(sh * 0.055))
    day_font = pygame.font.Font("fonts/Stardew_Valley.ttf",  int(sh * 0.045))
    global _logout_rect, _upload_rect, _upload_pos, _download_rect, _download_pos, _auto_rect, _social_rect
    global _active_settings_tab

    spoon_name_input, inventory_tab, background_color, folder_one, folder_two, folder_three, folder_four, folder_five, folder_six, folders_dropdown_open = inventory_args

    sw, sh = screen.get_size()

    # --- Tab buttons ---
    tab_font = bigger_font
    btn_w = 250
    btn_h = 60
    spacing = 20
    top_y = int(sh * 0.05)

    left_offset = 90

    graphics_rect = pygame.Rect(((sw//2) - btn_w - spacing//2 - left_offset), top_y, btn_w, btn_h)
    account_rect  = pygame.Rect(((sw//2) + spacing//2 - left_offset), top_y, btn_w, btn_h)
    spoons_rect  = pygame.Rect(((sw//2) + spacing//2 + btn_w - left_offset), top_y, btn_w, btn_h)
    sound_button_rect = pygame.Rect(sw - 100, 30, 60, 60)

    # Draw tabs
    for rect, text, active in [
        (graphics_rect, "Customization", _active_settings_tab == "graphics"),
        (account_rect,  "Account",  _active_settings_tab == "account"),
        (spoons_rect,   "Spoons",   _active_settings_tab == "spoons")
    ]:
        color = (40, 40, 40) if not active else (0, 0, 0)
        pygame.draw.rect(screen, background_color, rect, border_radius=10)
        label = tab_font.render(text, True, color)
        screen.blit(label, (rect.centerx - label.get_width() // 2, rect.centery - label.get_height() // 2))

    # --- Sound toggle button ---
    screen.blit(sound_button, sound_button_rect)
    if not sound_toggle:
        sx, sy = sound_button.get_size()
        redx = pygame.transform.smoothscale(floppy_disk_redx, (sx, sy))
        screen.blit(redx, sound_button_rect)

    # Store rects for click logic
    global _graphics_rect, _account_rect, _spoons_rect, _sound_rect
    _graphics_rect = graphics_rect
    _account_rect = account_rect
    _spoons_rect = spoons_rect
    _sound_rect = sound_button_rect


    # --- Separator line below tabs ---
    pygame.draw.line(screen, (0, 0, 0), (int(sw*0.15), top_y + btn_h), (int(sw*0.85), top_y + btn_h), 4)

    # --- Active tab content ---
    if _active_settings_tab == "graphics":
        if inventory_args:
            # inventory_args begins with: spoon_name_input, inventory_tab, background_color, folder_one.., folders_dropdown_open
            draw_inventory(screen, icon_image, manillaFolder_name, input_active, *inventory_args)
    elif _active_settings_tab == "account":
        # draw account settings (existing content)
        # reuse your original UI section
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
        inner = pygame.Rect(_auto_rect.x, _auto_rect.y, _auto_rect.w, _auto_rect.h)
        if get_auto_download_flag():
            chk = pygame.transform.smoothscale(floppy_disk_checkmark, (inner.w, inner.h))
            screen.blit(chk, inner.topleft)
        else:
            rx = pygame.transform.smoothscale(floppy_disk_redx, (inner.w, inner.h))
            screen.blit(rx, inner.topleft)

        # Toggle: Social Features Enabled
        label = font.render("Social Features", True, (200, 200, 200))
        screen.blit(label, (sw*0.17, toggle_y))
        box_size = int(sh * 0.06)
        _social_rect = pygame.Rect(sw * 0.13, toggle_y, box_size, box_size)
        pygame.draw.rect(screen, (180, 180, 180), _social_rect, width=3, border_radius=6)
        inner = pygame.Rect(_social_rect.x, _social_rect.y, _social_rect.w, _social_rect.h)
        if get_social_enabled_flag():
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

        # Upload & download floppies (as before)
        _upload_pos = (int(sw * 0.90), int(sh * 0.90 - 75))
        screen.blit(floppy_disk_upload, _upload_pos)
        uw, uh = floppy_disk_upload.get_size()
        _upload_rect = pygame.Rect(_upload_pos[0], _upload_pos[1], uw, uh)

        now = pygame.time.get_ticks()
        if _upload_state["uploading"]:
            _update_upload_anim(now)
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

        _download_pos = (int(sw * 0.80), int(sh * 0.90 - 75))
        screen.blit(floppy_disk_download, _download_pos)
        dw, dh = floppy_disk_download.get_size()
        _download_rect = pygame.Rect(_download_pos[0], _download_pos[1], dw, dh)
        if _download_state["done"]:
            _draw_result_overlay(screen, _download_state["ok"], _download_pos, "download")
    
    elif _active_settings_tab == "spoons":
        prompts = [
            prompt_font.render(f"Daily Wake-up {spoon_name}", True, (255,255,255)),
        ]

        # --- Spoons-related toggles ---
        global _spoons_debt_rect
        global _spoons_debt_cons_rect
        box_size = int(sh * 0.06)

        toggle_start_y = int(sh * 0.8)
        toggle_gap = int(sh * 0.1)

        # Spoons Debt toggle
        debt_label = font.render("Enable Spoons Debt", True, (255,255,255))
        screen.blit(debt_label, (sw*0.17, toggle_start_y))
        _spoons_debt_rect = pygame.Rect(sw*0.13, toggle_start_y, box_size, box_size)
        pygame.draw.rect(screen, (180,180,180), _spoons_debt_rect, width=3, border_radius=6)
        if spoons_debt_toggle:
            chk = pygame.transform.smoothscale(floppy_disk_checkmark, (box_size, box_size))
            screen.blit(chk, _spoons_debt_rect.topleft)
        else:
            rx = pygame.transform.smoothscale(floppy_disk_redx, (box_size, box_size))
            screen.blit(rx, _spoons_debt_rect.topleft)

        # Spoons Debt Consequences toggle
        cons_label = font.render("Spoons Debt Consequences", True, (255,255,255))
        screen.blit(cons_label, (sw*0.17, toggle_start_y + toggle_gap))
        _spoons_debt_cons_rect = pygame.Rect(sw*0.13, toggle_start_y + toggle_gap, box_size, box_size)
        pygame.draw.rect(screen, (180,180,180), _spoons_debt_cons_rect, width=3, border_radius=6)
        if spoons_debt_consequences_toggle:
            chk = pygame.transform.smoothscale(floppy_disk_checkmark, (box_size, box_size))
            screen.blit(chk, _spoons_debt_cons_rect.topleft)
        else:
            rx = pygame.transform.smoothscale(floppy_disk_redx, (box_size, box_size))
            screen.blit(rx, _spoons_debt_cons_rect.topleft)

        px1 = 130
        py = int(sh * layout_heights["daily_prompt"])
        for surf in prompts:
            screen.blit(surf, (px1, py))
            py += surf.get_height()

        # — daily input labels & boxes —
        dx = px1
        dy = int(sh * layout_heights["daily_prompt"]) + 40
        box_w, box_h = int(sw * 0.06), 30

        for i, day in enumerate(days):
            label = day_font.render(f"{day}:", True, (255,255,255))
            screen.blit(label, (dx + 10 + i * (box_w + 10), dy))

            input_rect = pygame.Rect(dx + i * (box_w + 10), dy + 30, box_w, box_h)
            value = str(daily_spoons.get(day, ""))
            active = input_active == day
            draw_input_box(screen, input_rect, active, value, LIGHT_GRAY, DARK_SLATE_GRAY, True, background_color, "light", 9, 0.045) #type: ignore


def logic_settings(event, page, daily_spoons, input_active, sound_toggle, spoons_debt_toggle, spoons_debt_consequences_toggle, *inventory_args):
    """Handles tab switching and normal settings logic."""
    global _active_settings_tab

    sh, sw = pygame.display.get_surface().get_size()

    updated = list(inventory_args)

    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        # --- Tab clicks ---
        if _graphics_rect and _graphics_rect.collidepoint(event.pos):
            _active_settings_tab = "graphics"
        if _account_rect and _account_rect.collidepoint(event.pos):
            _active_settings_tab = "account"
        if _spoons_rect and _spoons_rect.collidepoint(event.pos):
            _active_settings_tab = "spoons"
        
        # --- Global Sound toggle ---
        if _sound_rect and _sound_rect.collidepoint(event.pos):
            sound_toggle = not sound_toggle

        # --- Account tab logic (only if visible) ---
        if _active_settings_tab == "account":
            if _auto_rect and _auto_rect.collidepoint(event.pos):
                new_val = not get_auto_download_flag()
                set_auto_download_flag(new_val)
            
            if _social_rect and _social_rect.collidepoint(event.pos):
                new_val = not get_social_enabled_flag()
                set_social_enabled_flag(new_val)

            if _logout_rect and _logout_rect.collidepoint(event.pos):
                clear_credentials()
                return ("login", daily_spoons, input_active, sound_toggle, spoons_debt_toggle, spoons_debt_consequences_toggle, *updated)

            if _upload_rect and _upload_rect.collidepoint(event.pos) and not _upload_state["uploading"]:
                _upload_state["uploading"] = True
                _upload_state["done"] = False
                _upload_state["ok"] = False
                _upload_state["anim_step"] = 3
                _upload_state["next_tick_ms"] = pygame.time.get_ticks() + 500
                _upload_state["done_started_at"] = None
                _start_upload_thread()

            if _download_rect and _download_rect.collidepoint(event.pos):
                _download_state["downloading"] = True
                _download_state["done"] = False
                _download_state["ok"] = False
                _download_state["done_started_at"] = None
                from copyparty_sync import download_data_json_if_present
                download_data_json_if_present()
                _download_state["trigger_download"] = True  # just a flag

        # Always pass events to the inventory logic when the Graphics tab is active,
        if _active_settings_tab == "graphics" and inventory_args:
            input_active, *updated = logic_inventory(event, input_active, *inventory_args)

            
        # --- Spoons tab toggles ---
        if _active_settings_tab == "spoons":
            if _spoons_debt_rect and _spoons_debt_rect.collidepoint(event.pos):
                spoons_debt_toggle = not spoons_debt_toggle

            if _spoons_debt_cons_rect and _spoons_debt_cons_rect.collidepoint(event.pos):
                spoons_debt_consequences_toggle = not spoons_debt_consequences_toggle

                    # --- Spoons tab daily input box logic ---
        if _active_settings_tab == "spoons":
            dx = 130
            box_h = 30
            dy = int(sh * layout_heights["daily_prompt"])
            box_w = int(pygame.display.get_surface().get_width() * 0.06)

            # Handle clicks
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for i, day in enumerate(days):
                    rect = pygame.Rect(dx + i * (box_w + 10), dy, box_w, box_h)
                    if rect.collidepoint(event.pos):
                        input_active = day
                        return (page, daily_spoons, input_active, sound_toggle, spoons_debt_toggle, spoons_debt_consequences_toggle, *updated)
                input_active = ""

    # --- Handle all typing centrally ---
    elif event.type == pygame.KEYDOWN:
        # 1) If editing a day input
        if input_active in days:
            current_val = str(daily_spoons.get(input_active, ""))
            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                input_active = ""
            elif event.key == pygame.K_BACKSPACE:
                current_val = current_val[:-1]
            elif event.unicode.isdigit() and len(current_val) < 2:
                current_val += event.unicode
            daily_spoons[input_active] = int(current_val) if current_val else 0

        # 2) If editing spoon/folder names in graphics tab
        elif _active_settings_tab == "graphics" and input_active in ("spoon_name","folder_one","folder_two","folder_three","folder_four","folder_five","folder_six"):
            _measure_font = pygame.font.Font("fonts/Stardew_Valley.ttf", 24)
            buf = list(inventory_args)  # make editable copy of the tuple contents

            # index map based on your unpack order:
            # spoon_name_input(0), inventory_tab(1), background_color(2),
            # folder_one(3), folder_two(4), folder_three(5),
            # folder_four(6), folder_five(7), folder_six(8), folders_dropdown_open(9), ...
            idx_map = {"spoon_name": 0, "folder_one": 3, "folder_two": 4, "folder_three": 5, "folder_four": 6, "folder_five": 7, "folder_six": 8}
            idx = idx_map[input_active]
            current_text = str(buf[idx])

            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                input_active = ""  # defocus
            elif event.key == pygame.K_BACKSPACE:
                buf[idx] = current_text[:-1]
            elif len(event.unicode) == 1 and event.unicode.isprintable():
                candidate = current_text + event.unicode
                # enforce width only for spoon_name field
                if input_active != "spoon_name":
                    buf[idx] = candidate
                else:
                    text_width, _ = _measure_font.size(candidate)
                    if text_width <= spoon_name_input_box.width - 10:
                        buf[idx] = candidate

            # push modifications into "updated" so the return actually carries the typed value
            updated = buf
            
    return (page, daily_spoons, input_active, sound_toggle, spoons_debt_toggle, spoons_debt_consequences_toggle, *updated)




from drawing_functions.draw_rounded_button import draw_rounded_button
from drawing_functions.draw_input_box import draw_input_box
from themes import THEMES
from switch_themes import switch_theme

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

    for i in range(7):
        for j in range(3):
            pygame.draw.rect(screen, lighter_background, (220 + 100 * i, 190 + 100 * j, square_width, square_width))
            pygame.draw.rect(screen, darker_background, (220 + 100 * i, 190 + 100 * j, square_width, square_width), 4)

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
        screen.blit(icon_prompt, (inventory_tab_x, 145))

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
            cell_y = 190 + 100 * row
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
        screen.blit(rename_folders_text, (inventory_tab_x,145))
        # draw the dropdown header
        header_bg = lighter_background
        header_border = darker_background
        draw_rounded_button(
            screen,
            folder_dropdown_rect,
            header_bg,
            header_border,
            1, 2
        )

        icon_width = square_width - 15

        for idx, (surface, name) in enumerate(folder_surfaces):
            col = idx % 7
            row = idx // 7
            if row >= 3:
                break
            cell_x = 220 + 100 * col
            cell_y = 190 + 100 * row
            outline = pygame.Rect(cell_x, cell_y, square_width, square_width)
            inventory_folder_buttons.append((outline, surface, name))
            draw_rounded_button(screen, outline, background_color if manillaFolder_name == name else lighter_background, darker_background, 1, 2)
            scaled  = pygame.transform.scale(surface, (icon_width, (icon_width//5)*3))
            rect    = scaled.get_rect(center=outline.center)
            screen.blit(scaled, rect)

        folder_name_prompt = font.render("Folder Names:", True, BLACK)# type: ignore
        screen.blit(folder_name_prompt, (folder_dropdown_rect.left - folder_name_prompt.get_width() - 5, 145))

        # header text: either placeholder or first folder name
        header_txt = "Select Folder"
        txt_surf = select_folder_font.render(header_txt, True, BLACK) #type:ignore
        txt_pos  = (folder_dropdown_rect.x + 7,
                    folder_dropdown_rect.y + (folder_dropdown_rect.height - txt_surf.get_height())//2)
        screen.blit(txt_surf, txt_pos)

        # if open, draw the six input boxes underneath
        if folders_dropdown_open:
            draw_input_box(screen, folder_one_name_input_box, input_active == "folder_one", folder_one, LIGHT_GRAY, DARK_SLATE_GRAY, False, background_color, "light", 5)#type: ignore
            draw_input_box(screen, folder_two_name_input_box, input_active == "folder_two", folder_two, LIGHT_GRAY, DARK_SLATE_GRAY, False, background_color, "light", 5)#type: ignore
            draw_input_box(screen, folder_three_name_input_box, input_active == "folder_three", folder_three, LIGHT_GRAY, DARK_SLATE_GRAY, False, background_color, "light", 5)#type: ignore
            draw_input_box(screen, folder_four_name_input_box, input_active == "folder_four", folder_four, LIGHT_GRAY, DARK_SLATE_GRAY, False, background_color, "light", 5)#type: ignore
            draw_input_box(screen, folder_five_name_input_box, input_active == "folder_five", folder_five, LIGHT_GRAY, DARK_SLATE_GRAY, False, background_color, "light", 5)#type: ignore
            draw_input_box(screen, folder_six_name_input_box, input_active == "folder_six", folder_six, LIGHT_GRAY, DARK_SLATE_GRAY, False, background_color, "light", 5)#type: ignore

    elif inventory_tab == "Themes":
        inventory_themes_buttons.clear()
        rename_folders_text = bigger_font.render("THEMES", True, BLACK)# type: ignore
        screen.blit(rename_folders_text, (inventory_tab_x,145))

        for idx, theme_key in enumerate(theme_colors):
            col = idx % 7
            row = idx // 7
            # stop after two rows of 7 (you have 13 themes)
            if row >= 2:
                break

            cell_x = 220 + 100 * col
            cell_y = 190 + 100 * row
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
        screen.blit(rename_folders_text, (inventory_tab_x,145))

        icon_width = square_width - 15

        for idx, (surface, name) in enumerate(border_surfaces):
            col = idx % 7
            row = idx // 7
            if row >= 3:
                break
            cell_x = 220 + 100 * col
            cell_y = 190 + 100 * row
            outline = pygame.Rect(cell_x, cell_y, square_width, square_width)
            inventory_border_buttons.append((outline, surface, name))
            draw_rounded_button(screen, outline, lighter_background, darker_background, 1, 2)
            rotated = pygame.transform.rotate(surface, 90)
            scaled  = pygame.transform.scale(rotated, (icon_width, icon_width//3))
            rect    = scaled.get_rect(center=outline.center)
            screen.blit(scaled, rect)


def logic_inventory(event,
                    input_active,
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
            # toggle dropdown
            if folder_dropdown_rect.collidepoint(mx, my):
                folders_dropdown_open = not folders_dropdown_open
                clicked_any = True

            # choose folder art only when dropdown is closed
            if not folders_dropdown_open:
                for outline, surface, name in inventory_folder_buttons:
                    if outline.collidepoint(mx, my):
                        manillaFolder, manillaFolder_name = set_image('manillaFolder', name)
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