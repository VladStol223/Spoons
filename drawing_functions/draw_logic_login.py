import pygame
import os, json, time
from config import *
from drawing_functions.draw_input_box import draw_input_box
from copyparty_sync import (
    put_user_json, set_credentials, set_user_folder,
    download_data_json_if_present, put_new_user_cred, upload_data_json,
    verify_credentials_and_access, probe_login_status, set_stay_offline_flag
)

# Globals for UI hitboxes so logic() can read what draw() laid out
_main_choice_rects = {}
_form_rects = {}
_title_cache = None
_status_msg = ""   # <-- NEW: shows errors to the user (e.g., registration failed)

def _font(size): return pygame.font.Font("fonts/Stardew_Valley.ttf", size)


def draw_login(screen, login_mode, username_text, password_text, input_active, background_color):
    global _main_choice_rects, _form_rects, _title_cache, _status_msg
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
    title_surf = label_font.render(form_title, True, (255, 255, 255))
    screen.blit(title_surf, ((screen_w - title_surf.get_width()) // 2, int(screen_h * 0.30)))

    # --- NEW: error/status banner ---
    if _status_msg:
        err_font = _font(int(screen_h * 0.04))
        err_surf = err_font.render(_status_msg, True, (230, 80, 80))
        screen.blit(err_surf, ((screen_w - err_surf.get_width()) // 2, int(screen_h * 0.36)))

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
    btn_size = (120, 40)
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
    global _status_msg
    page = "login"
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        # choice buttons
        if not login_mode and _main_choice_rects:
            if _main_choice_rects.get("register") and _main_choice_rects["register"].collidepoint(event.pos):
                _status_msg = ""  # clear any old errors on mode switch
                return "register", username_text, password_text, None, page
            if _main_choice_rects.get("login") and _main_choice_rects["login"].collidepoint(event.pos):
                _status_msg = ""  # clear any old errors on mode switch
                return "login", username_text, password_text, None, page
            if _main_choice_rects.get("offline") and _main_choice_rects["offline"].collidepoint(event.pos):
                _status_msg = ""
                set_stay_offline_flag(True)
                return login_mode, username_text, password_text, None, "input_spoons"

        # form
        if login_mode and _form_rects:
            if _form_rects.get("user") and _form_rects["user"].collidepoint(event.pos):
                return login_mode, username_text, password_text, "username", page
            if _form_rects.get("pass") and _form_rects["pass"].collidepoint(event.pos):
                return login_mode, username_text, password_text, "password", page
            if _form_rects.get("back") and _form_rects["back"].collidepoint(event.pos):
                _status_msg = ""  # clear error when backing out
                return None, "", "", None, page

            if _form_rects.get("confirm") and _form_rects["confirm"].collidepoint(event.pos):
                set_stay_offline_flag(False)
                u, p = username_text.strip(), password_text
                if not u:
                    _status_msg = "Please enter a username."
                    return login_mode, username_text, password_text, "username", page

                ok = True
                if login_mode == "register":
                    # 1) ask backend to create the account
                    ok = put_new_user_cred(u, u, p)  # file_stem = username
                    # 2) if that worked, save credentials locally so future DAV calls can auth
                    if ok:
                        set_credentials(u, p)

                elif login_mode == "login":
                    # Store typed creds locally (so later code can use them if probe succeeds)
                    set_credentials(u, p)

                    # NEW: precise probe to distinguish wrong username vs wrong password
                    status = probe_login_status(u, p)

                    from state_data import _download_state

                    if status == "ok":
                        set_user_folder(u)
                        _status_msg = ""
                        _download_state["trigger_download"] = True
                        return login_mode, username_text, password_text, None, "input_spoons"

                    if status == "wrong_password":
                        _status_msg = "Wrong password. Please try again."
                        return login_mode, username_text, "", "password", page  # clear/focus password

                    if status == "no_such_user":
                        _status_msg = "Cannot find Username. Please try again."
                        return login_mode, username_text, password_text, "username", page

                    # Any other HTTP / network issue
                    _status_msg = "Couldn’t reach the server. Please try again."
                    return login_mode, username_text, password_text, input_active, page

                if ok:
                    set_user_folder(u)  # make sure sync uses this user

                    if login_mode == "register":
                        # Ensure the new home dir is reachable before first upload
                        access_ok = verify_credentials_and_access()
                        if not access_ok:
                            pygame.time.wait(1000)  # pause 1s then retry
                            access_ok = verify_credentials_and_access()

                        if not access_ok:
                            print("registration failed")
                            _status_msg = "Registration failed. Please choose a different username and password."
                            return login_mode, username_text, password_text, "username", page

                        # home is reachable -> push local data to the cloud
                        try:
                            upload_data_json()
                            _status_msg = ""  # success
                        except Exception as e:
                            _status_msg = "Upload failed after registration. Try again from Settings later."
                            print(f"[copyparty] initial upload after register failed: {e}")
                            # still move on to the app
                    else:
                        # login path keeps the existing behavior (pull if present)
                        _status_msg = ""
                        download_data_json_if_present()

                    return login_mode, username_text, password_text, None, "input_spoons"

                # Backend said “no” (e.g., dup username/password or other issue)
                _status_msg = "Registration failed. Please choose a different username and password."
                return login_mode, username_text, password_text, "username", page

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
                _status_msg = ""
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
