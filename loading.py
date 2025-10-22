import pygame
import os

def load_images(folder, x, y):
    frames = []
    if os.path.isdir(folder):
        for file in sorted(os.listdir(folder)): 
            path = os.path.join(folder, file)
            if os.path.isfile(path):  
                img = pygame.image.load(path).convert_alpha()
                final = pygame.transform.scale(img, (x, y))
                frames.append(final)
    return frames


def load(folder, x, y):
    animations = {}
    if os.path.isdir(folder):
        for subfolder in os.listdir(folder):  
            primaryPath = os.path.join(folder, subfolder)
            if os.path.isdir(primaryPath):
                frames = load_images(primaryPath, x, y)
                animations[subfolder] = frames
    return animations

def loader_images(folder, resolution):
    frames = []
    if os.path.isdir(folder):
        for file in sorted(os.listdir(folder)): 
            path = os.path.join(folder, file)
            if os.path.isfile(path):  
                img = pygame.image.load(path).convert_alpha()
                final = pygame.transform.scale(img, resolution)
                frames.append(final)
    return frames


def loader(folder, resolution):
    animations = {}
    if os.path.isdir(folder):
        for subfolder in os.listdir(folder):  
            primaryPath = os.path.join(folder, subfolder)
            if os.path.isdir(primaryPath):
                frames = load_images(primaryPath, resolution)
                animations[subfolder] = frames
    return animations
