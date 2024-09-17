import pygame
import random
from pygame_emojis import load_emoji
import json
import time
from helpers import *

# Инициализация pygame
pygame.init()

# LEVELS
with open("levels.json", "r") as file:
    LEVELS = json.load(file)




# Настройки уровня
LEVEL = 1
print(LEVELS[LEVEL-1]['level_width'])
LEVEL_WIDTH = LEVELS[LEVEL-1]['level_width']  # Ширина уровня
WIDTH, HEIGHT = 1150, 600  # Размеры окна
# Настройки экрана
screen = pygame.display.set_mode((WIDTH, HEIGHT))
# screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption("Platformer")



# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


# Частота кадров
FPS = 60
clock = pygame.time.Clock()



# Загрузка изображений врагов
enemy_images = [
    pygame.image.load(img("daemon1.png")),
    pygame.image.load(img("daemon2.png")),
    pygame.image.load(img("daemon3.png"))
]
enemy_images = [pygame.transform.scale(img, (200, 220)) for img in enemy_images]

# Загрузка изображений камней
rock = pygame.image.load(img("rock2.png"))
rock = pygame.transform.scale(rock, (300, 150))
rock_right_1 = pygame.image.load(img("rock_right_3.png"))
rock_right_1 = pygame.transform.scale(rock_right_1, (300, 150))
rock_right_2 = pygame.image.load(img("rock_right_2.png"))
rock_right_2 = pygame.transform.scale(rock_right_2, (300, 150))
rock_left_1 = pygame.image.load(img("rock_left_3.png"))
rock_left_1 = pygame.transform.scale(rock_left_1, (300, 150))
rock_left_2 = pygame.image.load(img("rock_left_2.png"))
rock_left_2 = pygame.transform.scale(rock_left_2, (300, 150))

box_images = [
    rock_right_1, rock_right_2, rock, rock_left_1, rock_left_2
]

bonus_image = pygame.image.load(img('bonus.png')).convert_alpha()
bonus_image = pygame.transform.scale(bonus_image, (64, 64))

life_image = pygame.image.load(img('life.png')).convert_alpha()
life_image = pygame.transform.scale(life_image, (64, 64))

ammunition_image = pygame.image.load(img('ammunition.png')).convert_alpha()
ammunition_image = pygame.transform.scale(ammunition_image, (100, 64))

# Изображение пули
bullet_image =  load_emoji("⭐", (16,16))

# Загрузка изображений для анимации бега
run_frames_right = [
    pygame.image.load(img('run_right_1.png')).convert_alpha(),
    pygame.image.load(img('run_right_2.png')).convert_alpha(),
    pygame.image.load(img('run_right_3.png')).convert_alpha()
]

run_frames_left = [
    pygame.image.load(img('run_left_1.png')).convert_alpha(),
    pygame.image.load(img('run_left_2.png')).convert_alpha(),
    pygame.image.load(img('run_left_3.png')).convert_alpha()
]

# Загрузка изображений для анимации стрельбы
shoot_frames_right = [
    pygame.image.load(img('shoot_right_1.png')).convert_alpha(),
    pygame.image.load(img('shoot_right_1.png')).convert_alpha()
]

shoot_frames_left = [
    pygame.image.load(img('shoot_left_1.png')).convert_alpha(),
    pygame.image.load(img('shoot_left_1.png')).convert_alpha()
]

# Опционально: изменение размера изображений
run_frames_right = [pygame.transform.scale(frame, (128, 138)) for frame in run_frames_right]
run_frames_left = [pygame.transform.scale(frame, (128, 138)) for frame in run_frames_left]
shoot_frames_right = [pygame.transform.scale(frame, (128, 138)) for frame in shoot_frames_right]
shoot_frames_left = [pygame.transform.scale(frame, (128, 138)) for frame in shoot_frames_left]