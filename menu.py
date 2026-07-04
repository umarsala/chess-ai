

import pygame
import sys
from config import settings
from settings_menu import run_settings
from audio import play_click

pygame.init()
pygame.mixer.init()

#FONTS
TITLE_FONT = pygame.font.Font("fonts/Cinzel-Bold.ttf", 96)
SUBTITLE_FONT = pygame.font.Font("fonts/Cinzel-Regular.ttf", 36)
BUTTON_FONT = pygame.font.Font("fonts/Cinzel-Regular.ttf", 40)

WIDTH, HEIGHT = 1600, 900
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("CHESS - The Final Gambit")

#load menu background
menu_bg = pygame.image.load("images/menu_bg.png").convert_alpha()
img_w, img_h = menu_bg.get_size()
stretch_factor = HEIGHT / img_h
new_width = int(img_w * stretch_factor)
menu_bg = pygame.transform.smoothscale(menu_bg, (new_width , HEIGHT)) 

bg_x = (WIDTH - new_width) // 2
bg_y = 0

#button settings
Font = pygame.font.Font(None, 50)
white = (255, 255, 255)
BUTTON_COLOUR = (20, 30, 40)
BUTTON_HOVER = (40, 60, 80)

class Button:
    def __init__(self, text, x, y, width, height):
        self.text = text
        self.color = BUTTON_COLOUR
        self.rect = pygame.Rect(x, y, width, height)
       

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect, border_radius = 12)
        text_surface = BUTTON_FONT.render(self.text, True, white)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

        if self.is_hovered(pygame.mouse.get_pos()):
            glow = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
            glow.fill((120, 180, 255, 50))
            screen.blit(glow, (self.rect.x, self.rect.y))
    
    def is_hovered(self, pos):
        return self.rect.collidepoint(pos)
    
    def update(self, mouse_pos):
        if self.is_hovered(mouse_pos):
            self.color = BUTTON_HOVER
        else:
            self.color = BUTTON_COLOUR
    
    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)
    

    #create buttons
single_btn = Button("Single Player Mode", 137, 335, 525, 71)
two_btn = Button("Two Player Mode", 137, 428, 525, 70)
settings_btn = Button("Settings", 137, 522, 525, 70)
quit_width = 260
quit_x = 137 + (525 - quit_width) // 2 # centre quit button
quit_btn = Button("Quit", quit_x, 616, quit_width, 70)

def run_menu(screen, WIDTH, HEIGHT):
    while True:
        mouse_pos = pygame.mouse.get_pos()
        screen.fill((0, 0, 0))
        screen.blit(menu_bg, (bg_x, bg_y))

        #Title and subtitle
        title_surface = TITLE_FONT.render("CHESS", True, (220, 240, 255))
        title_rect = title_surface.get_rect(center=(WIDTH // 2, 120))
        screen.blit(title_surface, title_rect)

        subtitle_surface = SUBTITLE_FONT.render("THE FINAL GAMBIT", True, (180, 200, 220))
        subtitle_rect = subtitle_surface.get_rect(center=(WIDTH // 2, 180))
        screen.blit(subtitle_surface, subtitle_rect)

        for btn in [single_btn, two_btn, settings_btn, quit_btn]:
                btn.update(mouse_pos)
                btn.draw(screen)

            #event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if single_btn.is_clicked(event.pos):
                        play_click()
                        from pregame_menu import run_single_player_setup
                        result = run_single_player_setup(screen, menu_bg, bg_x, bg_y)
                        return result

                if two_btn.is_clicked(event.pos):
                        play_click()
                        from pregame_menu import run_two_player_setup
                        result = run_two_player_setup(screen, menu_bg, bg_x, bg_y)
                        return result
                
                if settings_btn.is_clicked(event.pos):
                        play_click()    
                        from settings_menu import run_settings
                        result = run_settings(screen, menu_bg, bg_x, bg_y)
                        if result == "quit":
                            return "quit"
        
                if quit_btn.is_clicked(event.pos):
                        play_click()
                        return "quit"
                
        print(mouse_pos[0], mouse_pos[1])
        pygame.display.update()
