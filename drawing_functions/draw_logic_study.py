from config import *
import pygame
from datetime import timedelta
from drawing_functions.draw_rounded_button import draw_rounded_button

class Timer:
    def __init__(self):
        self.set_mode("Pomodoro (25/5)")
        self.is_running = False
        self.is_break = False
        self.last_tick = pygame.time.get_ticks()

    def set_mode(self, mode, custom_work=25, custom_break=5):
        self.mode = mode
        if mode == "Custom":
            self.work_minutes = custom_work
            self.break_minutes = custom_break
        else:
            self.work_minutes, self.break_minutes = TIMER_MODES[mode]
        self.reset()

    def start(self):
        self.is_running = True
        self.last_tick = pygame.time.get_ticks()

    def pause(self):
        self.is_running = False

    def reset(self):
        self.is_break = False
        self.remaining_seconds = self.work_minutes * 60
        self.is_running = False

    def update(self):
        if not self.is_running:
            return
        now = pygame.time.get_ticks()
        elapsed = (now - self.last_tick) // 1000
        if elapsed > 0:
            self.remaining_seconds -= elapsed
            self.last_tick = now
        if self.remaining_seconds <= 0:
            self.is_break = not self.is_break
            self.remaining_seconds = self.break_minutes * 60 if self.is_break else self.work_minutes * 60
            self.last_tick = pygame.time.get_ticks()

    def get_time_str(self):
        return str(timedelta(seconds=self.remaining_seconds))[:-3]

def draw_study(screen, timer, font, dropdown_open, available_modes):
    global hub_buttons_showing
    draw_rounded_button(screen,hub_toggle,LIGHT_GRAY,BLACK,0,2)# type: ignore
    timer.update()
    time_text = font.render(timer.get_time_str(), True, (255, 255, 255))
    screen.blit(time_text, (300, 150))

    # Buttons
    btn_labels = ["Start", "Pause", "Reset"]
    for i, label in enumerate(btn_labels):
        pygame.draw.rect(screen, (70, 130, 180), (150 + i * 160, 250, 120, 40))
        text = font.render(label, True, (255, 255, 255))
        screen.blit(text, (160 + i * 160, 255))

    # Dropdown
    pygame.draw.rect(screen, (50, 50, 50), (150, 320, 300, 40))
    mode_text = font.render(timer.mode, True, (255, 255, 255))
    screen.blit(mode_text, (160, 325))

    if dropdown_open:
        for i, mode in enumerate(available_modes):
            pygame.draw.rect(screen, (70, 70, 70), (150, 360 + i * 40, 300, 40))
            text = font.render(mode, True, (255, 255, 255))
            screen.blit(text, (160, 365 + i * 40))

def logic_study(event, timer, dropdown_open, available_modes):
    if event.type == pygame.MOUSEBUTTONDOWN:
        x, y = event.pos
        if 150 <= x <= 270 and 250 <= y <= 290:
            timer.start()
        elif 310 <= x <= 430 and 250 <= y <= 290:
            timer.pause()
        elif 470 <= x <= 590 and 250 <= y <= 290:
            timer.reset()
        elif 150 <= x <= 450 and 320 <= y <= 360:
            dropdown_open = not dropdown_open
        elif dropdown_open:
            for i, mode in enumerate(available_modes):
                if 150 <= x <= 450 and 360 + i * 40 <= y <= 400 + i * 40:
                    if mode == "Custom":
                        timer.set_mode("Custom", custom_work=30, custom_break=10)
                    else:
                        timer.set_mode(mode)
                    dropdown_open = False
                    break
    return dropdown_open
