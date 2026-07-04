import pygame
from config import settings

pygame.mixer.init()

click_sound = pygame.mixer.Sound("sounds/click.mp3")

def play_click():
    click_sound.set_volume(settings["sfx_volume"])
    click_sound.play()
