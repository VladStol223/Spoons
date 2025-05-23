import pygame

# Global list of clickable folder rects
folder_rects = []

def draw_complete_tasks_folders(screen, selected_folder, active_color, inactive_color,
                                 folder_one, folder_two, folder_three,
                                 folder_four, folder_five, folder_six):
    global folder_rects
    folder_rects = []

    # === CONFIGURABLE LAYOUT ===
    folder_width = 300
    folder_height = 200
    tab_width = 120
    tab_height = 26
    tab_offset_x = 0
    tab_indent = 15
    slide_offset = 20
    folder_spacing = 20

    start_x = screen.get_width() - folder_width + slide_offset + 140
    start_y = 120

    folder_names = [
        ("homework", folder_one),
        ("chores", folder_two),
        ("important", folder_three),
        ("work", folder_four),
        ("exams", folder_five),
        ("projects", folder_six)
    ]

    font = pygame.font.SysFont("arial", 18, bold=True)

    for i, (folder_key, folder_name) in enumerate(folder_names):
        overlap_px = 130   # how many pixels each folder should overlap the one above
        vertical_step = folder_height - overlap_px
        y = start_y + i * vertical_step

        x = start_x - slide_offset if folder_key == selected_folder else start_x

        color = active_color if folder_key == selected_folder else inactive_color

        # --- Tab Polygon ---
        tab_points = [
            (x + tab_offset_x, y),
            (x + tab_offset_x + tab_indent, y - tab_height),
            (x + tab_offset_x + tab_width - tab_indent, y - tab_height),
            (x + tab_offset_x + tab_width, y)
        ]
        pygame.draw.polygon(screen, color, tab_points)
        pygame.draw.polygon(screen, (0, 0, 0), tab_points, width=2)

        # --- Folder Body Rectangle ---
        folder_rect = pygame.Rect(x, y, folder_width, folder_height)
        pygame.draw.rect(screen, color, folder_rect)
        pygame.draw.rect(screen, (0, 0, 0), folder_rect, width=2)

        # --- Folder Name inside the tab ---
        text_surf = font.render(folder_name, True, (0, 0, 0))
        text_rect = text_surf.get_rect(center=(x + tab_offset_x + tab_width // 2, y - tab_height // 2 + 2))
        screen.blit(text_surf, text_rect)

        # Full clickable area includes tab and body
        click_rect = pygame.Rect(x, y - tab_height, folder_width, folder_height + tab_height)
        folder_rects.append((folder_key, click_rect))

    # Debug: visualize clickable zones (optional)
    # for _, r in folder_rects:
    #     pygame.draw.rect(screen, (255, 0, 0), r, 1)
