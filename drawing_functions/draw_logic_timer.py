import pygame
import math
from datetime import datetime, timedelta
from config import *


class TimerEngine:
    """
    Centralized timer engine with two modes:
        "rest"   (Input Spoons Page)
        "focus"  (Manage Tasks Page — later)
    """

    def __init__(self):
        # Config
        self.deg_per_spoon = time_per_spoon * 6

        # State
        self.timer_active = False
        self.intro_anim_active = False

        self.timer_start_time = None
        self.timer_end_time = None
        self.intro_start_time = None
        self.next_spoon_time = None

        # Freeze bookkeeping
        self.timer_frozen = False
        self.frozen_remaining_secs = None
        self.frozen_intro_progress = None
        self.frozen_angle = None
        self.freeze_timestamp = None

        # Amounts
        self.total_spoons_to_recover = 0
        self.spoons_to_recover = 0
        self.intro_duration = 1.0

        # Visual
        self.timer_angle = 45
        self.timer_background = avatarBackgrounds["timer_background"]
        self.timer_hand = avatarBackgrounds["timer_hand"]
        self.timer_top = avatarBackgrounds["timer_top"]
        self.timer_toggle_button = toggleButtons["timerButton"]

    # ==========================================================
    # TOOLTIP
    # ==========================================================
    def _tooltip(self, screen, rect, text):
        font_tip = pygame.font.Font("fonts/Stardew_Valley.ttf", 22)
        surf = font_tip.render(text, True, (255,255,255))
        padding = 6
        box = pygame.Rect(rect.right+12, rect.y,
                          surf.get_width()+padding*2,
                          surf.get_height()+padding*2)
        pygame.draw.rect(screen, (30,30,30), box, border_radius=6)
        pygame.draw.rect(screen, (220,220,220), box, 2, border_radius=6)
        screen.blit(surf, (box.x+padding, box.y+padding))

    # ==========================================================
    # LOGIC
    # ==========================================================
    def logic(self, mode, event, timer_toggle_on, rest_spoons, spoons, rest_icon_rects):
        """
        Called from logic_input_spoons().
        rest_icon_rects MUST be passed from draw_input_spoons().
        """
        if mode != "rest":
            return timer_toggle_on, spoons

        # -------------------------------------------------------
        # CLICK TIMER TOGGLE
        # -------------------------------------------------------
        toggle_rect = pygame.Rect(
            120, 100,
            self.timer_toggle_button.get_width(),
            self.timer_toggle_button.get_height()
        )

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

            # ========== Toggle clicked ==========
            if toggle_rect.collidepoint(event.pos):

                # TURNING OFF → FREEZE EVERYTHING
                if timer_toggle_on:
                    self._freeze_timer()
                else:
                    # TURNING ON → UNFREEZE EVERYTHING
                    self._unfreeze_timer()

                timer_toggle_on = not timer_toggle_on
                return timer_toggle_on, spoons

            # ---------------------------------------------------
            # CLICK REST BUTTONS
            # ---------------------------------------------------
            for name, rect in rest_icon_rects.items():
                if rect.collidepoint(event.pos):

                    rest_amt = rest_spoons[name]

                    if timer_toggle_on:
                        # If currently frozen, unfreeze first
                        if self.timer_frozen:
                            self._unfreeze_timer()

                        # Start intro animation
                        self.total_spoons_to_recover = rest_amt
                        self.spoons_to_recover = rest_amt
                        self.intro_anim_active = True
                        self.intro_start_time = datetime.now()
                        self.intro_duration = 0.4 + 0.2 * rest_amt
                        self.timer_active = False
                        self.timer_angle = 45
                    else:
                        # Instant classic recovery
                        spoons += rest_amt
                        spoons = min(spoons, 99)

                    return timer_toggle_on, spoons

        return timer_toggle_on, spoons

    # ==========================================================
    # FREEZE LOGIC
    # ==========================================================
    def _freeze_timer(self):
        """Freeze intro OR countdown state completely."""

        if self.timer_frozen:
            return

        now = datetime.now()
        self.freeze_timestamp = now
        self.timer_frozen = True
        self.frozen_angle = self.timer_angle

        # Freeze in intro stage
        if self.intro_anim_active and self.intro_start_time:
            elapsed_intro = (now - self.intro_start_time).total_seconds()
            self.frozen_intro_progress = elapsed_intro / max(0.0001, self.intro_duration)

        # Freeze in countdown stage
        elif self.timer_active and self.timer_start_time and self.timer_end_time:
            remaining = (self.timer_end_time - now).total_seconds()
            self.frozen_remaining_secs = max(0, remaining)

    def _unfreeze_timer(self):
        """Resume timer after toggle ON again."""
        if not self.timer_frozen:
            return

        now = datetime.now()

        # Restore intro animation
        if self.intro_anim_active and self.frozen_intro_progress is not None:
            self.intro_start_time = now - timedelta(seconds=self.frozen_intro_progress * self.intro_duration)

        # Restore countdown
        elif self.timer_active and self.frozen_remaining_secs is not None:
            self.timer_start_time = now - timedelta(seconds=self.total_spoons_to_recover * time_per_spoon * 60 - self.frozen_remaining_secs)
            self.timer_end_time = now + timedelta(seconds=self.frozen_remaining_secs)
            self.next_spoon_time = now + timedelta(minutes=time_per_spoon)

        # Restore angle
        self.timer_angle = self.frozen_angle

        # Clear freeze state
        self.timer_frozen = False
        self.frozen_intro_progress = None
        self.frozen_remaining_secs = None
        self.frozen_angle = None
        self.freeze_timestamp = None

    # ==========================================================
    # DRAW
    # ==========================================================
    def draw(self, screen, mode, timer_toggle_on, spoons, time_per_spoon):
        if mode != "rest":
            return spoons

        sw, sh = screen.get_size()
        sw -= 200
        mouse_x, mouse_y = pygame.mouse.get_pos()

        # -------------------------------------------------------
        # ALWAYS DRAW TOGGLE BUTTON FIRST (fixed)
        # -------------------------------------------------------
        toggle_rect = pygame.Rect(
            120, 100,
            self.timer_toggle_button.get_width(),
            self.timer_toggle_button.get_height()
        )

        if timer_toggle_on:
            t = pygame.time.get_ticks() / 1000
            alpha = int(150 + 105 * (0.5 * (1 + math.sin(t*4))))
            r = int(self.timer_toggle_button.get_width() * 0.7)
            aura = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
            pygame.draw.circle(aura,(255,255,150,alpha),(r,r),r)
            screen.blit(aura,(toggle_rect.centerx-r, toggle_rect.centery-r))

        screen.blit(self.timer_toggle_button, toggle_rect)

        if toggle_rect.collidepoint(mouse_x, mouse_y):
            self._tooltip(screen, toggle_rect, "Recover spoons over time")

        # -------------------------------------------------------
        # PAUSED MODE (toggle OFF)
        # -------------------------------------------------------
        if not timer_toggle_on:
            return spoons  # Toggle drawn, but no timer drawn

        # -------------------------------------------------------
        # DRAW TIMER BACKGROUND
        # -------------------------------------------------------
        tw, th = self.timer_background.get_size()
        timer_x = (sw - tw) // 2 + 135
        timer_y = int(sh * 0.18)
        screen.blit(self.timer_background, (timer_x, timer_y))

        total_rotation = self.total_spoons_to_recover * self.deg_per_spoon
        total_secs = self.total_spoons_to_recover * time_per_spoon * 60
        font = pygame.font.Font("fonts/Stardew_Valley.ttf", int(sh*0.047))

        # -------------------------------------------------------
        # FROZEN — DO NOT UPDATE ANYTHING
        # -------------------------------------------------------
        if self.timer_frozen:
            # Draw the frozen time text
            if self.frozen_remaining_secs is not None:
                h = int(self.frozen_remaining_secs//3600)
                m = int((self.frozen_remaining_secs%3600)//60)
                s = int(self.frozen_remaining_secs%60)
                text = f"{h}:{m:02}:{s:02}"
            elif self.frozen_intro_progress is not None:
                intro_elapsed = int(self.frozen_intro_progress * total_secs)
                h = intro_elapsed // 3600
                m = (intro_elapsed % 3600) // 60
                s = intro_elapsed % 60
                text = f"{h}:{m:02}:{s:02}"
            else:
                text = "0:00:00"

            surf = font.render(text, True, BLACK) #type: ignore
            rect = surf.get_rect(center=(timer_x+tw//2, timer_y+th//2-42))
            screen.blit(surf, rect)

            # Frozen hand
            frozen_rot = pygame.transform.rotate(self.timer_hand, -self.frozen_angle)
            rrect = frozen_rot.get_rect(center=(timer_x+tw//2, timer_y+th//2))
            screen.blit(frozen_rot, rrect)

            screen.blit(self.timer_top, (timer_x, timer_y))
            return spoons

        # -------------------------------------------------------
        # INTRO ANIMATION
        # -------------------------------------------------------
        if self.intro_anim_active:
            p = (datetime.now() - self.intro_start_time).total_seconds() / max(0.0001, self.intro_duration)
            p = max(0, min(1,p))

            self.timer_angle = 45 + p * total_rotation

            t_elapsed = int(p * total_secs)
            h = t_elapsed // 3600
            m = (t_elapsed % 3600) // 60
            s = t_elapsed % 60
            text = f"{h}:{m:02}:{s:02}"

            surf = font.render(text, True, BLACK) #type: ignore
            rect = surf.get_rect(center=(timer_x+tw//2, timer_y+th//2-42))
            screen.blit(surf, rect)

            if p >= 1.0:
                self.intro_anim_active = False
                self.timer_active = True
                self.timer_start_time = datetime.now()
                self.timer_end_time = self.timer_start_time + timedelta(seconds=total_secs)
                self.next_spoon_time = self.timer_start_time + timedelta(minutes=time_per_spoon)

        # -------------------------------------------------------
        # COUNTDOWN
        # -------------------------------------------------------
        elif self.timer_active and self.timer_start_time and self.timer_end_time:
            now = datetime.now()
            remaining = max(0,(self.timer_end_time-now).total_seconds())
            elapsed = total_secs - remaining
            prog = 0 if total_secs<=0 else elapsed/total_secs
            prog = max(0, min(1,prog))

            self.timer_angle = 45 + (1-prog)*total_rotation

            while self.spoons_to_recover>0 and now>=self.next_spoon_time:
                spoons += 1
                spoons = min(spoons,99)
                self.spoons_to_recover -=1
                self.next_spoon_time += timedelta(minutes=time_per_spoon)
                if self.spoons_to_recover<=0:
                    self.timer_active=False
                    break

            h = int(remaining//3600)
            m = int((remaining%3600)//60)
            s = int(remaining%60)
            text = f"{h}:{m:02}:{s:02}"
            surf = font.render(text,True,BLACK) #type: ignore
            rect = surf.get_rect(center=(timer_x+tw//2, timer_y+th//2-42))
            screen.blit(surf,rect)

        # -------------------------------------------------------
        # IDLE
        # -------------------------------------------------------
        else:
            self.timer_angle = 45
            surf = font.render("0:00:00",True,BLACK) #type: ignore
            rect = surf.get_rect(center=(timer_x+tw//2, timer_y+th//2-42))
            screen.blit(surf,rect)

        # -------------------------------------------------------
        # DRAW HAND
        # -------------------------------------------------------
        rotated = pygame.transform.rotate(self.timer_hand, -self.timer_angle)
        rrect = rotated.get_rect(center=(timer_x+tw//2, timer_y+th//2))
        screen.blit(rotated, rrect)

        screen.blit(self.timer_top,(timer_x,timer_y))

        return spoons
