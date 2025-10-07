import pygame
import os, json
from config import *
from drawing_functions.draw_input_box import draw_input_box
from copyparty_sync import put_user_json, set_credentials, set_user_folder, download_data_json_if_present, put_new_user_cred

# Globals for UI hitboxes so logic() can read what draw() laid out
_main_choice_rects = {}
_form_rects = {}
_title_cache = None

def _font(size): return pygame.font.Font("fonts/Stardew_Valley.ttf", size)


def draw_login(screen, login_mode, username_text, password_text, input_active, background_color):
    global _main_choice_rects, _form_rects, _title_cache
    sw, sh = screen.get_size()
    screen_w, screen_h = sw, sh
    screen_w -= 0  # keep parity with other draw fns

    title_font = _font(int(screen_h * 0.08))
    label_font = _font(int(screen_h * 0.045))
    button_font = _font(int(screen_h * 0.05))

    if not login_mode:
        # Main choice buttons
        btn_w, btn_h, gap = int(screen_w * 0.35), int(screen_h * 0.10), int(screen_h * 0.03)
        start_y = int(screen_h * 0.35)
        cx = (screen_w - btn_w) // 2
        colors = [(70, 90, 120), (70, 120, 90), (120, 90, 70)]
        labels = [("Register", "register"), ("Login", "login"), ("Stay Offline", "offline")]
        _main_choice_rects = {}
        for i, (text, key) in enumerate(labels):
            r = pygame.Rect(cx, start_y + i * (btn_h + gap), btn_w, btn_h)
            _main_choice_rects[key] = r
            pygame.draw.rect(screen, colors[i], r, border_radius=14)
            txt = button_font.render(text, True, (255, 255, 255))
            screen.blit(txt, (r.centerx - txt.get_width() // 2, r.centery - txt.get_height() // 2))
        return login_mode, username_text, password_text, input_active

    # Form mode (register or login)
    form_title = "Register New Account" if login_mode == "register" else "Login to Your Account"
    form_title_surf = label_font.render(form_title, True, (255, 255, 255))
    screen.blit(form_title_surf, ((screen_w - form_title_surf.get_width()) // 2, int(screen_h * 0.36)))

    # Labels
    field_w, field_h = int(screen_w * 0.40), int(screen_h * 0.07)
    cx = (screen_w - field_w) // 2
    user_y = int(screen_h * 0.48)
    pass_y = user_y + field_h + int(screen_h * 0.06)

    user_label = label_font.render("Username:", True, (255, 255, 255))
    pass_label = label_font.render("Password:", True, (255, 255, 255))
    screen.blit(user_label, (cx, user_y - int(screen_h * 0.055)))
    screen.blit(pass_label, (cx, pass_y - int(screen_h * 0.055)))

    # Inputs
    user_rect = pygame.Rect(cx, user_y, field_w, field_h)
    pass_rect = pygame.Rect(cx, pass_y, field_w, field_h)
    masked = "*" * len(password_text)

    draw_input_box(screen, user_rect, input_active == "username", username_text, LIGHT_GRAY, DARK_SLATE_GRAY, True, background_color, "light", 12, 0.050) #type: ignore
    draw_input_box(screen, pass_rect, input_active == "password", masked, LIGHT_GRAY, DARK_SLATE_GRAY, True, background_color, "light", 12, 0.050) #type: ignore

    # Buttons (Confirm / Back) as images from config
    btn_size = (int(screen_h * 0.10), int(screen_h * 0.10))
    gap = int(screen_w * 0.02)
    confirm_img = pygame.transform.smoothscale(confirm_edit_button, btn_size)
    back_img = pygame.transform.smoothscale(cancel_edit_button, btn_size)
    total_w = btn_size[0] * 2 + gap
    start_x = (screen_w - total_w) // 2
    btn_y = pass_y + field_h + int(screen_h * 0.06)

    confirm_rect = pygame.Rect(start_x, btn_y, btn_size[0], btn_size[1])
    back_rect = pygame.Rect(start_x + btn_size[0] + gap, btn_y, btn_size[0], btn_size[1])
    screen.blit(confirm_img, confirm_rect.topleft)
    screen.blit(back_img, back_rect.topleft)

    _form_rects = {"user": user_rect, "pass": pass_rect, "confirm": confirm_rect, "back": back_rect}
    return login_mode, username_text, password_text, input_active

def logic_login(event, login_mode, username_text, password_text, input_active):
    page = "login"
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        # choice buttons
        if not login_mode and _main_choice_rects:
            if _main_choice_rects.get("register") and _main_choice_rects["register"].collidepoint(event.pos):
                return "register", username_text, password_text, None, page
            if _main_choice_rects.get("login") and _main_choice_rects["login"].collidepoint(event.pos):
                return "login", username_text, password_text, None, page
            if _main_choice_rects.get("offline") and _main_choice_rects["offline"].collidepoint(event.pos):
                return login_mode, username_text, password_text, None, "input_spoons"

        # form
        if login_mode and _form_rects:
            if _form_rects.get("user") and _form_rects["user"].collidepoint(event.pos):
                return login_mode, username_text, password_text, "username", page
            if _form_rects.get("pass") and _form_rects["pass"].collidepoint(event.pos):
                return login_mode, username_text, password_text, "password", page
            if _form_rects.get("back") and _form_rects["back"].collidepoint(event.pos):
                return None, "", "", None, page
            if _form_rects.get("confirm") and _form_rects["confirm"].collidepoint(event.pos):
                u, p = username_text.strip(), password_text
                if not u:
                    return login_mode, username_text, password_text, "username", page

                ok = True
                if login_mode == "register":
                    # 1) ask backend to create the account
                    ok = put_new_user_cred(u, u, p)  # file_stem = username
                    # 2) if that worked, save credentials locally so future DAV calls can auth
                    if ok:
                        set_credentials(u, p)

                elif login_mode == "login":
                    # For login, just store typed creds locally
                    set_credentials(u, p)

                if ok:
                    set_user_folder(u)  # future syncs go to /spoons/<u>
                    try:
                        import os
                        os.makedirs("spoons", exist_ok=True)
                        with open("spoons/active_user.txt", "w", encoding="utf-8") as f:
                            f.write(u)
                    except Exception:
                        pass
                    download_data_json_if_present()  # pull user's data.json if present
                    return login_mode, username_text, password_text, None, "input_spoons"

                # failed; stay on the login page
                return login_mode, username_text, password_text, input_active, page


        if login_mode:
            return login_mode, username_text, password_text, None, page

    elif event.type == pygame.KEYDOWN and login_mode:
        target = "username" if input_active == "username" else ("password" if input_active == "password" else None)
        if target:
            if event.key == pygame.K_TAB:
                next_field = "password" if input_active == "username" else "username"
                return login_mode, username_text, password_text, next_field, page
            elif event.key == pygame.K_RETURN:
                # let the mouse path handle confirm; do nothing here
                return login_mode, username_text, password_text, None, page
            elif event.key == pygame.K_ESCAPE:
                return None, "", "", None, page
            else:
                if target == "username":
                    if event.key == pygame.K_BACKSPACE: username_text = username_text[:-1]
                    else:
                        ch = event.unicode
                        if ch and ch.isprintable() and len(username_text) < 32: username_text += ch
                else:
                    if event.key == pygame.K_BACKSPACE: password_text = password_text[:-1]
                    else:
                        ch = event.unicode
                        if ch and ch.isprintable() and len(password_text) < 64: password_text += ch
                return login_mode, username_text, password_text, input_active, page

    return login_mode, username_text, password_text, input_active, page