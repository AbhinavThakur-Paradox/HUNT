import pygame

class Menu(object) :
    def __init__(self, resolution, path) :
        self.img = pygame.image.load(path).convert_alpha()
        self.resolution = resolution
        self.bg = pygame.transform.scale(self.img, self.resolution)
        self.active = False
    
    def render(self, window) :
        window.blit(self.bg,(0,0))