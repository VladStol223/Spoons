import pygame
import os, json, time
from config import *
from drawing_functions.draw_input_box import draw_input_box, InputBox, logic_input_box
from copyparty_sync import (
    put_user_json, set_credentials, set_user_folder,
    download_data_json_if_present, put_new_user_cred, upload_data_json,
    verify_credentials_and_access, probe_login_status, set_stay_offline_flag
)

input_boxes_login = {
    "username": InputBox(None, text="", multiline=False, fontsize=0.055, box_type="text"),
    "password": InputBox(None, text="", multiline=False, fontsize=0.055, box_type="password")
}

# Globals for UI hitboxes so logic() can read what draw() laid out
_main_choice_rects = {}
_form_rects = {}
_title_cache = None
_status_msg = ""   # <-- NEW: shows errors to the user (e.g., registration failed)

def _font(size): return pygame.font.Font("fonts/Stardew_Valley.ttf", size)

def draw_login(screen, login_mode, input_boxes_login, input_active, background_color):
    global _main_choice_rects, _form_rects, _status_msg

    sw, sh = screen.get_size()
    screen_w, screen_h = sw, sh

    title_font  = _font(int(screen_h * 0.08))
    label_font  = _font(int(screen_h * 0.045))
    button_font = _font(int(screen_h * 0.05))

    # =============== MAIN CHOICE PAGE ===============
    if not login_mode:
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
            ts = button_font.render(text, True, WHITE) #type: ignore
            screen.blit(ts, ts.get_rect(center=r.center))

        return

    # =============== LOGIN / REGISTER FORM ===============
    # Title
    form_title = "Register New Account" if login_mode == "regist #type: ignoreer" else "Login to Your Account"
    title_surf = title_font.render(form_title, True, WHITE) #type: ignore
    screen.blit(title_surf, ((screen_w - title_surf.get_width()) // 2, int(screen_h * 0.20)))

    # Status line
    if _status_msg:
        err_font = _font(int(screen_h * 0.04))
        err_surf = err_font.render(_status_msg, True, (230, 80, 80))
        screen.blit(err_surf, ((screen_w - err_surf.get_width()) // 2, int(screen_h * 0.28)))

    # Layout
    field_w = int(screen_w * 0.40)
    field_h = int(screen_h * 0.07)
    cx = (screen_w - field_w) // 2

    user_y = int(screen_h * 0.40)
    pass_y = user_y + field_h + int(screen_h * 0.06)

    # Labels
    user_label = label_font.render("Username:", True, WHITE) #type: ignore
    pass_label = label_font.render("Password:", True, WHITE) #type: ignore
    screen.blit(user_label, (cx, user_y - int(screen_h * 0.055)))
    screen.blit(pass_label, (cx, pass_y - int(screen_h * 0.055)))

    # Assign rects to input boxes
    input_boxes_login["username"].rect = pygame.Rect(cx, user_y, field_w, field_h)
    input_boxes_login["password"].rect = pygame.Rect(cx, pass_y, field_w, field_h)

    # Mask password
    input_boxes_login["password"].display_text = "*" * len(input_boxes_login["password"].text)

    # Draw input boxes
    draw_input_box(screen, input_boxes_login["username"], LIGHT_GRAY, DARK_SLATE_GRAY, background_color=background_color, infill="light") #type: ignore
    draw_input_box(screen, input_boxes_login["password"], LIGHT_GRAY, DARK_SLATE_GRAY, background_color=background_color, infill="light") #type: ignore

    # Buttons (Existing images)
    btn_size = (160, 50)
    gap = int(screen_w * 0.02)
    total_w = btn_size[0] * 2 + gap
    start_x = (screen_w - total_w) // 2
    btn_y = pass_y + field_h + int(screen_h * 0.08)

    confirm_rect = pygame.Rect(start_x, btn_y, *btn_size)
    back_rect    = pygame.Rect(start_x + btn_size[0] + gap, btn_y, *btn_size)

    confirm_img = pygame.transform.smoothscale(confirm_edit_button, btn_size)
    back_img    = pygame.transform.smoothscale(cancel_edit_button, btn_size)

    # Draw button backgrounds
    screen.blit(confirm_img, confirm_rect)
    screen.blit(back_img, back_rect)

    # --- ADD TEXT ON TOP OF BUTTONS ---
    confirm_text = "Register" if login_mode == "register" else "Login"
    back_text    = "Cancel"

    btn_font = _font(int(screen_h * 0.045))

    # Confirm button text
    c_surf = btn_font.render(confirm_text, True, WHITE) #type: ignore
    c_rect = c_surf.get_rect(center=confirm_rect.center)
    screen.blit(c_surf, c_rect)

    # Back button text
    b_surf = btn_font.render(back_text, True, WHITE) #type: ignore
    b_rect = b_surf.get_rect(center=back_rect.center)
    screen.blit(b_surf, b_rect)

    _form_rects = {
        "confirm": confirm_rect,
        "back": back_rect,
        "username": input_boxes_login["username"].rect,
        "password": input_boxes_login["password"].rect
    }


def logic_login(event, login_mode, input_boxes_login, input_active):
    global _status_msg

    page = "login"

    # ====================== CLICK HANDLING ======================
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

        # -------- main menu buttons --------
        if not login_mode and _main_choice_rects:
            if _main_choice_rects["register"].collidepoint(event.pos):
                _status_msg = ""
                return "register", input_boxes_login, "username", page

            if _main_choice_rects["login"].collidepoint(event.pos):
                _status_msg = ""
                return "login", input_boxes_login, "username", page

            if _main_choice_rects["offline"].collidepoint(event.pos):
                set_stay_offline_flag(True)
                _status_msg = ""
                return login_mode, input_boxes_login, None, "input_spoons"

        # -------- form mode --------
        if login_mode:

            # Focus username
            if _form_rects["username"].collidepoint(event.pos):
                input_active = "username"
                input_boxes_login["username"].active = True
                input_boxes_login["password"].active = False
                return login_mode, input_boxes_login, input_active, page

            # Focus password
            if _form_rects["password"].collidepoint(event.pos):
                input_active = "password"
                input_boxes_login["username"].active = False
                input_boxes_login["password"].active = True
                return login_mode, input_boxes_login, input_active, page

            # Back button
            if _form_rects["back"].collidepoint(event.pos):
                _status_msg = ""
                return None, input_boxes_login, None, page

            # Confirm button
            if _form_rects["confirm"].collidepoint(event.pos):
                u = input_boxes_login["username"].text.strip()
                p = input_boxes_login["password"].text

                if not u:
                    _status_msg = "Please enter a username."
                    return login_mode, input_boxes_login, "username", page

                set_stay_offline_flag(False)

                # ---- Register ----
                if login_mode == "register":
                    ok = put_new_user_cred(u, u, p)
                    if ok:
                        set_credentials(u, p)
                        set_user_folder(u)
                        if verify_credentials_and_access():
                            upload_data_json()
                        return login_mode, input_boxes_login, None, "input_spoons"

                    _status_msg = "Registration failed. Try a different username."
                    return login_mode, input_boxes_login, "username", page

                # ---- Login ----
                set_credentials(u, p)
                status = probe_login_status(u, p)

                if status == "ok":
                    set_user_folder(u)
                    from state_data import _download_state
                    _download_state["trigger_download"] = True
                    _status_msg = ""
                    return login_mode, input_boxes_login, None, "input_spoons"

                if status == "wrong_password":
                    _status_msg = "Wrong password. Try again."
                    input_boxes_login["password"].text = ""
                    return login_mode, input_boxes_login, "password", page

                if status == "no_such_user":
                    _status_msg = "Username not found."
                    return login_mode, input_boxes_login, "username", page

                _status_msg = "Could not reach server."
                return login_mode, input_boxes_login, input_active, page

    # ====================== KEY HANDLING ======================
    if event.type == pygame.KEYDOWN and login_mode:

        # Let InputBox handle typing
        logic_input_box(event, input_boxes_login["username"], pygame.display.get_surface())
        logic_input_box(event, input_boxes_login["password"], pygame.display.get_surface())

        # Tab swapping
        if event.key == pygame.K_TAB:
            input_active = "password" if input_active == "username" else "username"
            input_boxes_login["username"].active = (input_active == "username")
            input_boxes_login["password"].active = (input_active == "password")
            return login_mode, input_boxes_login, input_active, page

        # ESC to exit
        if event.key == pygame.K_ESCAPE:
            _status_msg = ""
            return None, input_boxes_login, None, page

    return login_mode, input_boxes_login, input_active, page
