
import pygame
import sys
from config import settings
from audio import play_click



pygame.init()


# Display dimensions
WIDTH = 1600
HEIGHT = 900

# Theme buttons
THEME_Y = 300
classic_rect = pygame.Rect((WIDTH - 200) // 2, THEME_Y, 200, 50)

# style buttons
STYLE_Y = 480
STYLE_WIDTH = 220
STYLE_HEIGHT = 55
STYLE_SPACING = 80

total_width = (STYLE_WIDTH * 3) + (STYLE_SPACING * 2)
start_x = (WIDTH - total_width) // 2

classic_style_rect = pygame.Rect(start_x, STYLE_Y, STYLE_WIDTH, STYLE_HEIGHT)
gothic_style_rect = pygame.Rect(start_x + STYLE_WIDTH + STYLE_SPACING, STYLE_Y, STYLE_WIDTH, STYLE_HEIGHT)
wood_style_rect = pygame.Rect(start_x + 2 * (STYLE_WIDTH + STYLE_SPACING), STYLE_Y, STYLE_WIDTH, STYLE_HEIGHT)


# font
TITLE_FONT = pygame.font.Font("fonts/Cinzel-Bold.ttf", 60)
SECTION_FONT = pygame.font.Font("fonts/Cinzel-Regular.ttf", 36)
LABEL_FONT = pygame.font.Font("fonts/Cinzel-Regular.ttf", 30)
WHITE = (255, 255, 255)
GREY = (120, 120, 120)
BLUE = (120, 180, 255)
DARK = (20, 20, 20)

# slider properties
SLIDER_X = 100
SLIDER_Y = HEIGHT - 120
SLIDER_WIDTH = 300
SLIDER_HEIGHT = 8
KNOB_RADIUS = 12





def draw_slider(screen, x, y, volume):
    pygame.draw.rect(screen, GREY, (x, y, SLIDER_WIDTH, SLIDER_HEIGHT))
    knob_x = x + int(volume * SLIDER_WIDTH)
    pygame.draw.circle(screen, BLUE, (knob_x, y + SLIDER_HEIGHT // 2), KNOB_RADIUS)

def run_settings(screen, menu_bg, bg_x, bg_y):
    dragging = False

    classic_rect = pygame.Rect((WIDTH - 200) // 2, 300, 200, 50)

    back_rect = pygame.Rect(50, 50, 120, 45)

    while True:
            screen.blit(menu_bg, (bg_x, bg_y))  
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))  # semi-transparent
            screen.blit(overlay, (0, 0))

            title = TITLE_FONT.render("SETTINGS", True, WHITE)
            title_rect = title.get_rect(center=(WIDTH // 2, 130))
            screen.blit(title, title_rect)
            underline_width = title.get_width() + 20
            underline_rect = pygame.Rect(title_rect.centerx - underline_width //2, title_rect.bottom + 5, underline_width, 3)
            pygame.draw.rect(screen, BLUE, underline_rect)

            # Volume Panel Background (for both sliders)
            panel_width = 360
            panel_height = 120
            panel_x = SLIDER_X - 30
            panel_y = SLIDER_Y - 70

            panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
            panel_surface.fill((30, 30, 30, 170))
            screen.blit(panel_surface, (panel_x, panel_y))


             # Sfx volume slider
            sfx_text = LABEL_FONT.render("SFX Volume", True, WHITE)
            screen.blit(sfx_text, (SLIDER_X, SLIDER_Y - 40))
            draw_slider(screen, SLIDER_X, SLIDER_Y, settings["sfx_volume"])

            mode_text = SECTION_FONT.render("Mode", True, WHITE)
            screen.blit(mode_text, (WIDTH // 2 - mode_text.get_width() // 2, 250))

            draw_toggle_button(screen, classic_rect, "Classic", settings["mode"] == "classic")
           
            style_text = SECTION_FONT.render("Style", True, WHITE)
            screen.blit(style_text, (WIDTH // 2 - style_text.get_width() // 2, 400))
            draw_toggle_button(screen, classic_style_rect, "Classic", settings["style"] == "classic")
            draw_toggle_button(screen, gothic_style_rect, "Gothic", settings["style"] == "gothic")
            draw_toggle_button(screen, wood_style_rect, "Wood", settings["style"] == "wood")

            back_rect = pygame.Rect(50, 50, 140, 50)
            mouse_pos = pygame.mouse.get_pos()
            if back_rect.collidepoint(mouse_pos):
                pygame.draw.rect(screen, BLUE, back_rect, border_radius=8)
            else:
                pygame.draw.rect(screen, GREY, back_rect, border_radius=8)

            back_text = LABEL_FONT.render("Back", True, WHITE)
            back_text_rect = back_text.get_rect(center=back_rect.center)
            screen.blit(back_text, back_text_rect)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return "menu"

                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = event.pos
                    if back_rect.collidepoint(event.pos):
                        play_click()
                        return "menu"

                    #SFX slider
                    if SLIDER_X <= mx <= SLIDER_X + SLIDER_WIDTH:
                        if SLIDER_Y - 15 <= my <= SLIDER_Y + 15:
                            dragging = "sfx"

                    if classic_style_rect.collidepoint(event.pos):
                        play_click()
                        settings["style"] = "classic"
                       

                    if gothic_style_rect.collidepoint(event.pos):
                        play_click()
                        settings["style"] = "gothic"
                        

                    if wood_style_rect.collidepoint(event.pos):
                        play_click()
                        settings["style"] = "wood"
                        
                if event.type == pygame.MOUSEBUTTONUP:
                    dragging = False

                if event.type == pygame.MOUSEMOTION and dragging:
                    mx = event.pos[0]
                    relative_x = max(SLIDER_X, min(mx, SLIDER_X + SLIDER_WIDTH))
                    new_volume = (relative_x - SLIDER_X) / SLIDER_WIDTH
                    if dragging == "sfx":
                        settings["sfx_volume"] = new_volume
                    pygame.mixer.music.set_volume(new_volume)

            pygame.display.update()
        

def draw_toggle_button(screen, rect, text, selected):
    mouse_pos = pygame.mouse.get_pos()

    # Base colour logic
    if selected:
        colour = BLUE
    else:
        colour = GREY

    # Hover effect (only if not selected)
    if rect.collidepoint(mouse_pos) and not selected:
        colour = (160, 160, 160)  # lighter grey for hover

    pygame.draw.rect(screen, colour, rect, border_radius=10)

    label = LABEL_FONT.render(text, True, WHITE)
    label_rect = label.get_rect(center=rect.center)
    screen.blit(label, label_rect)
