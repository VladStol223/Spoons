from config import *
import pygame
from drawing_functions.draw_rounded_button import draw_rounded_button

def draw_stats(screen, font, big_font, personal_stats, global_leaderboard):
    global hub_buttons_showing
    draw_rounded_button(screen,hub_toggle,LIGHT_GRAY,BLACK,0,2)# type: ignore
    y_offset = 40
    section_spacing = 60

    # Section: Personal Stats
    draw_section_title(screen, big_font, "Your Stats", y_offset)
    y_offset += section_spacing
    draw_text_line(screen, font, f"Total Tasks Completed: {personal_stats.get('tasks_completed', '—')}", y_offset)
    y_offset += 30
    draw_text_line(screen, font, f"Spoons Earned: {personal_stats.get('spoons_earned', '—')}", y_offset)
    y_offset += 30
    draw_text_line(screen, font, f"Spoons Spent: {personal_stats.get('spoons_spent', '—')}", y_offset)
    y_offset += 30
    draw_text_line(screen, font, f"Current Streak: {personal_stats.get('current_streak', '—')} days", y_offset)
    y_offset += 30
    draw_text_line(screen, font, f"Longest Streak: {personal_stats.get('longest_streak', '—')} days", y_offset)
    y_offset += section_spacing

    # Section: Folder Breakdown
    draw_section_title(screen, big_font, "Folder Breakdown", y_offset)
    y_offset += section_spacing
    for folder_name, count in personal_stats.get("folder_breakdown", {}).items():
        draw_text_line(screen, font, f"{folder_name.title()}: {count} tasks", y_offset)
        y_offset += 25
    y_offset += section_spacing

    # Section: Global Leaderboard (placeholder)
    draw_section_title(screen, big_font, "Global Leaderboard (Coming Soon)", y_offset)
    y_offset += section_spacing
    for i, user in enumerate(global_leaderboard):
        draw_text_line(screen, font,
                       f"{i+1}. {user['username']} - Tasks: {user['tasks']}, Spoons: {user['spoons']}, Badges: {user['badges']}",
                       y_offset)
        y_offset += 25


def draw_section_title(screen, font, text, y):
    rendered = font.render(text, True, (255, 255, 255))
    screen.blit(rendered, (40, y))


def draw_text_line(screen, font, text, y):
    rendered = font.render(text, True, (200, 200, 200))
    screen.blit(rendered, (60, y))


def logic_stats(event):
    # Placeholder for any interactive elements you add later (e.g., tabs, sorting)
    pass
