import pygame
import sys

# Инициализация pygame
pygame.init()

# Установить размер окна
screen_width = 1158
screen_height = 720
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Пример Pygame")

# Установить цвет фона
background_color = (128, 0, 0)  # Черный

# Установить цвет текста
text_color = (255, 255, 255)  # Белый

# Создать шрифт
font = pygame.font.Font(None, 74)

# Создать текст
text = font.render('Hello, Pygame!', True, text_color)

# Главный цикл
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Заполнить экран фоном
    screen.fill(background_color)

    # Отобразить текст
    screen.blit(text, (100, 200))

    # Обновить экран
    pygame.display.flip()
