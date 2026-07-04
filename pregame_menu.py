import pygame
from config import settings
from audio import play_click

pygame.init()

WIDTH = 1600
HEIGHT = 900

SECTION_FONT = pygame.font.Font("fonts/Cinzel-Regular.ttf", 48)
LABEL_FONT = pygame.font.Font("fonts/Cinzel-Regular.ttf", 32)

WHITE = (255, 255, 255)
GREY = (120, 120, 120)
BLUE = (120, 180, 255)
 
def draw_button(screen, rect, text, selected=False):
    mouse_pos = pygame.mouse.get_pos()

    if rect.collidepoint(mouse_pos):
        colour = BLUE
    else:
        colour = BLUE if selected else GREY

    pygame.draw.rect(screen, colour, rect, border_radius=10)
    label = LABEL_FONT.render(text, True, WHITE)
    screen.blit(label, label.get_rect(center=rect.center))


def run_single_player_setup(screen, menu_bg, bg_x, bg_y):

        difficulty = "easy"
        time_control = 5

        BUTTON_WIDTH = 200
        BUTTON_HEIGHT = 60
        SPACING = 60

        total_width = (BUTTON_WIDTH * 3) + (SPACING * 2)
        start_x = (WIDTH - total_width) // 2
        y_pos = 300

        easy_rect = pygame.Rect(start_x, y_pos, BUTTON_WIDTH, BUTTON_HEIGHT)
        medium_rect = pygame.Rect(start_x + BUTTON_WIDTH + SPACING, y_pos, BUTTON_WIDTH, BUTTON_HEIGHT)
        hard_rect = pygame.Rect(start_x + 2 * (BUTTON_WIDTH + SPACING), y_pos, BUTTON_WIDTH, BUTTON_HEIGHT)
        
        time_total_width = (BUTTON_WIDTH * 2) + SPACING
        time_start_x = (WIDTH - time_total_width) // 2
        time_y = 450

        time_5 = pygame.Rect(time_start_x, time_y, BUTTON_WIDTH, BUTTON_HEIGHT)
        time_10 = pygame.Rect(time_start_x + BUTTON_WIDTH + SPACING, time_y, BUTTON_WIDTH, BUTTON_HEIGHT)

        # start button dimensions
        START_WIDTH = 300 
        START_HEIGHT = 70
        start_y = 600

        start_x = (WIDTH - START_WIDTH) // 2
        start_rect = pygame.Rect(start_x, start_y, START_WIDTH, START_HEIGHT)

        back_rect = pygame.Rect(50, 50, 140, 50)

        while True:
            screen.blit(menu_bg, (bg_x, bg_y))

            title = SECTION_FONT.render("Single Player Mode", True, WHITE)
            screen.blit(title, title.get_rect(center=(WIDTH//2, 150)))

            # Difficulty
            diff_text = LABEL_FONT.render("AI Difficulty", True, WHITE)
            screen.blit(diff_text, (WIDTH//2 - diff_text.get_width()//2, 240))

            draw_button(screen, easy_rect, "Easy", difficulty == "easy")
            draw_button(screen, medium_rect, "Medium", difficulty == "medium")
            draw_button(screen, hard_rect, "Hard", difficulty == "hard")

            # Time
            time_text = LABEL_FONT.render("Time Control", True, WHITE)
            screen.blit(time_text, (WIDTH//2 - time_text.get_width()//2, 390))

            draw_button(screen, time_5, "5 Min", time_control == 5)
            draw_button(screen, time_10, "10 Min", time_control == 10)

            draw_button(screen, start_rect, "Start Game")
            draw_button(screen, back_rect, "Back")

            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    return "quit"

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return "menu"

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if back_rect.collidepoint(event.pos):
                        play_click()
                        return "menu"

                    if easy_rect.collidepoint(event.pos):
                        play_click()
                        difficulty = "easy"

                    elif medium_rect.collidepoint(event.pos):
                        play_click()
                        difficulty = "medium"

                    elif hard_rect.collidepoint(event.pos):
                        play_click()
                        difficulty = "hard"

                    elif time_5.collidepoint(event.pos):
                        play_click()
                        time_control = 5

                    elif time_10.collidepoint(event.pos):
                        play_click()
                        time_control = 10

                    elif start_rect.collidepoint(event.pos):
                        play_click()
                        return {"mode": "single","difficulty": difficulty,"time": time_control}
                    
            pygame.display.update()

def run_two_player_setup(screen, menu_bg, bg_x, bg_y):

    time_control = 5

    BUTTON_WIDTH = 200
    BUTTON_HEIGHT = 60
    SPACING = 60

    time_total_width = (BUTTON_WIDTH * 2) + SPACING
    time_start_x = (WIDTH - time_total_width) // 2
    time_y = 330

    time_5 = pygame.Rect(time_start_x, time_y, BUTTON_WIDTH, BUTTON_HEIGHT)
    time_10 = pygame.Rect(time_start_x + BUTTON_WIDTH + SPACING, time_y, BUTTON_WIDTH, BUTTON_HEIGHT)

    START_WIDTH = 300
    START_HEIGHT = 70
    start_y = 520
    start_x = (WIDTH - START_WIDTH) // 2
    start_rect = pygame.Rect(start_x, start_y, START_WIDTH, START_HEIGHT)

    back_rect = pygame.Rect(50, 50, 140, 50)

    while True:
        screen.blit(menu_bg, (bg_x, bg_y))

        time_text = LABEL_FONT.render("Time Control", True, WHITE)
        screen.blit(time_text, (WIDTH//2 - time_text.get_width()//2, 250))

        title = SECTION_FONT.render("Two Player Mode", True, WHITE)
        screen.blit(title, title.get_rect(center=(WIDTH//2, 130)))

        draw_button(screen, time_5, "5 Min", time_control == 5)
        draw_button(screen, time_10, "10 Min", time_control == 10)

        draw_button(screen, start_rect, "Start Game")
        draw_button(screen, back_rect, "Back")

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                return "quit"

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "menu"

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

                if back_rect.collidepoint(event.pos):
                    play_click()
                    return "menu"

                elif time_5.collidepoint(event.pos):
                    play_click()
                    time_control = 5

                elif time_10.collidepoint(event.pos):
                    play_click()
                    time_control = 10

                elif start_rect.collidepoint(event.pos):
                    play_click()
                    return {"mode": "two","time": time_control}
        pygame.display.update()
