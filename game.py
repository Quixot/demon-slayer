import pygame
import random
from pygame_emojis import load_emoji
import json
import time


# LEVELS
with open("levels.json", "r") as file:
    LEVELS = json.load(file)

# print(len(LEVELS))
# time.sleep(100)


# https://github.com/ScienceGamez/pygame_emojis
# https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer?tab=readme-ov-file
# https://openmoji.org/library


# Инициализация pygame
pygame.init()

# Настройки уровня
LEVEL = 1
print(LEVELS[LEVEL-1]['level_width'])
LEVEL_WIDTH = LEVELS[LEVEL-1]['level_width']  # Ширина уровня
WIDTH, HEIGHT = 1150, 600  # Размеры окна
# Настройки экрана
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Platformer")




# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


# Частота кадров
FPS = 60
clock = pygame.time.Clock()







# Загрузка изображений врагов
enemy_images = [
    pygame.image.load("daemon1.png"),
    pygame.image.load("daemon2.png"),
    pygame.image.load("daemon3.png")
]
# Масштабирование изображений врагов
enemy_images = [pygame.transform.scale(img, (120, 120)) for img in enemy_images]



# box_image = pygame.image.load('rock.png').convert_alpha()
# box_image = pygame.transform.scale(box_image, (128, 128))
# Загрузка изображений преград
# rock1 = pygame.image.load("rock1.png")
# rock1 = pygame.transform.scale(rock1, (128, 128))

rock2 = pygame.image.load("rock2.png")
rock2 = pygame.transform.scale(rock2, (300, 150))

# rock3 = pygame.image.load("rock3.png")
# rock3 = pygame.transform.scale(rock3, (400, 266))

box_images = [
    rock2
]
# Масштабирование изображений врагов
# box_images = [pygame.transform.scale(img, (random.randint(128, 200), random.randint(128, 200))) for img in box_images]


bonus_image = pygame.image.load('bonus.png').convert_alpha()
bonus_image = pygame.transform.scale(bonus_image, (48, 48))


bullet_image =  load_emoji("⭐", (16,16))

# player_image_right = pygame.image.load('player_right.png').convert_alpha()  # Изображение для движения вправо
# player_image_left = pygame.image.load('player_left.png').convert_alpha()    # Изображение для движения влево
# # Изменение размера изображений
# player_image_right = pygame.transform.scale(player_image_right, (128, 128))  # Задайте нужный размер
# player_image_left = pygame.transform.scale(player_image_left, (128, 128))    # Задайте нужный размер


# Загрузка изображений для анимации бега
run_frames_right = [
    pygame.image.load('run_right_1.png').convert_alpha(),
    pygame.image.load('run_right_2.png').convert_alpha(),
    pygame.image.load('run_right_3.png').convert_alpha()
]

run_frames_left = [
    pygame.image.load('run_left_1.png').convert_alpha(),
    pygame.image.load('run_left_2.png').convert_alpha(),
    pygame.image.load('run_left_3.png').convert_alpha()
]

# Загрузка изображений для анимации стрельбы
shoot_frames_right = [
    pygame.image.load('shoot_right_1.png').convert_alpha(),
    pygame.image.load('shoot_right_1.png').convert_alpha()
]

shoot_frames_left = [
    pygame.image.load('shoot_left_1.png').convert_alpha(),
    pygame.image.load('shoot_left_1.png').convert_alpha()
]

# Опционально: изменение размера изображений
run_frames_right = [pygame.transform.scale(frame, (128, 128)) for frame in run_frames_right]
run_frames_left = [pygame.transform.scale(frame, (128, 128)) for frame in run_frames_left]
shoot_frames_right = [pygame.transform.scale(frame, (128, 128)) for frame in shoot_frames_right]
shoot_frames_left = [pygame.transform.scale(frame, (128, 128)) for frame in shoot_frames_left]



class Camera:
    def __init__(self, width, height):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height

    def apply(self, entity):
        return entity.rect.move(self.camera.topleft)

    def update(self, target):
        x = -target.rect.centerx + WIDTH // 2
        # Ограничение движения камеры
        x = min(0, x)  # Левую границу фиксируем
        max_x = -(self.width - WIDTH)  # Правую границу фиксируем, но делаем корректировку
        x = max(max_x, x)  # Останавливаем камеру на правой границе
        
        self.camera = pygame.Rect(x, 0, self.width, self.height)

    def is_at_right_edge(self):
        return self.camera.x <= -(self.width - WIDTH)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # self.image = player_image_right
        self.run_frames_right = run_frames_right
        self.run_frames_left = run_frames_left
        self.shoot_frames_right = shoot_frames_right
        self.shoot_frames_left = shoot_frames_left  
        self.current_frame = 0
        self.frame_delay = 5  # Количество обновлений до смены кадра
        self.frame_counter = 0  # Счетчик обновлений
        self.image = self.run_frames_right[self.current_frame]
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH // 2, HEIGHT - 150)
        self.speed_x = 0
        self.speed_y = 0
        self.on_ground = False
        self.lives = 3
        self.last_direction = 'right'  # В какую сторону смотрел плеер до остановки
        self.is_shooting = False

    def update(self):
        self.gravity()
        self.animate()  # Вызов функции для анимации

        # Изменение изображения при смене направления
        if self.speed_x > 0 and self.last_direction != 'right':
            self.image = self.run_frames_right[self.current_frame % len(self.run_frames_right)]  # Эмодзи для движения вправо
            self.last_direction = 'right'
        elif self.speed_x < 0 and self.last_direction != 'left':
            self.image = self.run_frames_left[self.current_frame % len(self.run_frames_left)]  # Эмодзи для движения влево
            self.last_direction = 'left'


        self.rect.x += self.speed_x
        self.collide_with_boxes('x')  # Проверка столкновений по оси X

        self.rect.y += self.speed_y
        self.collide_with_boxes('y')  # Проверка столкновений по оси Y

        if self.speed_x > 0:
            self.last_direction = 'right'
        elif self.speed_x < 0:
            self.last_direction = 'left'

        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > LEVEL_WIDTH:
            self.rect.right = LEVEL_WIDTH
        if self.rect.bottom > HEIGHT - 50:
            self.rect.bottom = HEIGHT - 50
            self.on_ground = True
            self.speed_y = 0

    def jump(self):
        # if self.on_ground:
        self.speed_y = -15
        self.on_ground = False

    def gravity(self):
        if not self.on_ground:
            self.speed_y += 0.5

    def animate(self):
        self.frame_counter += 1  # Увеличиваем счетчик обновлений

        if self.frame_counter >= self.frame_delay:  # Если счетчик достиг порога
            self.current_frame += 1  # Переход на следующий кадр
            self.frame_counter = 0  # Сброс счетчика

            # Анимация стрельбы
            if self.is_shooting:
                if self.last_direction == 'right':
                    self.image = self.shoot_frames_right[self.current_frame % len(self.shoot_frames_right)]
                else:
                    self.image = self.shoot_frames_left[self.current_frame % len(self.shoot_frames_left)]
            # Анимация бега
            elif self.speed_x != 0:
                if self.last_direction == 'right':
                    self.image = self.run_frames_right[self.current_frame % len(self.run_frames_right)]
                else:
                    self.image = self.run_frames_left[self.current_frame % len(self.run_frames_left)]
            else:
                if self.last_direction == 'right':
                    self.image = self.run_frames_right[0]  # Статичная поза
                else:
                    self.image = self.run_frames_left[0]  # Статичная поза

    def shoot(self):
        self.is_shooting = True
        if self.last_direction == 'right':
            bullet = Bullet(self.rect.right, self.rect.centery, 5)
        else:
            bullet = Bullet(self.rect.left, self.rect.centery, -5)
        all_sprites.add(bullet)
        bullets.add(bullet)

    def stop_shooting(self):
        self.is_shooting = False        

    def collide_with_boxes(self, direction):
        if direction == 'x':
            # smaller_rect = self.rect.inflate(-10, 0)  # Уменьшаем ширину на 10 пикселей (по 5 с каждой стороны)
            # hits = [box for box in boxes if box.rect.colliderect(smaller_rect)]
            hits = pygame.sprite.spritecollide(self, boxes, False)
            
            if hits:
                if self.speed_x > 0:
                    self.rect.right = hits[0].rect.left
                elif self.speed_x < 0:
                    self.rect.left = hits[0].rect.right

        if direction == 'y':
            hits = pygame.sprite.spritecollide(self, boxes, False)
            if hits:
                if self.speed_y > 0:
                    self.rect.bottom = hits[0].rect.top
                    self.on_ground = False
                    self.on_platform = True
                    self.speed_y = 0
                elif self.speed_y < 0:
                    self.rect.top = hits[0].rect.bottom
                    self.speed_y = 0



class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, speed_x):
        super().__init__()
        # self.image = pygame.Surface((10, 5))
        # self.image.fill(WHITE)
        self.image = bullet_image
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed_x = speed_x*1.5

    def update(self):
        self.rect.x += self.speed_x
        if self.rect.right < 0 or self.rect.left > LEVEL_WIDTH:
            self.kill()           



class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = random.choice(enemy_images)  # Случайный выбор изображения врага
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed_x = random.choice(LEVELS[LEVEL-1]['enemy_speed_range'])
        self.speed_y = 0
        self.attack_speed = 3  # Скорость движения врага к игроку
        self.attack_distance = 300  # Расстояние, на котором враг начинает атаковать

    def update(self):
        # Проверяем расстояние до игрока
        distance_to_player = self.rect.centerx - player.rect.centerx

        if abs(distance_to_player) < self.attack_distance:
            # Если враг близко к игроку, он движется к игроку
            if self.rect.centerx > player.rect.centerx:
                self.rect.x -= self.attack_speed
            else:
                self.rect.x += self.attack_speed

            if self.rect.centery > player.rect.centery:
                self.rect.y -= self.attack_speed
            else:
                self.rect.y += self.attack_speed
        else:
            # Обычное движение врага, если игрок далеко
            self.rect.x += self.speed_x
            if self.rect.right > WIDTH or self.rect.left < 0:
                self.speed_x = -self.speed_x


class Box(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = random.choice(box_images)
        self.rect = self.image.get_rect()
        # Размещение коробки на земле
        self.rect.x = x
        self.rect.y = HEIGHT - 40 - self.rect.height  # Вычисление Y-координаты для того, чтобы объект стоял на земле
        

class Bonus(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = bonus_image
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

class Terrain(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((LEVEL_WIDTH, 50))
        self.rect = self.image.get_rect()
        self.rect.x = 0
        self.rect.y = HEIGHT - 50

def load_level(level_number):
    global all_sprites, enemies, boxes, bonuses, bullets, player, terrain, camera, background, bg_width, bg_height, background_speed

    # Загрузка изображения фона
    background = pygame.image.load(LEVELS[LEVEL-1]['background'])
    bg_width, bg_height = background.get_size()
    background_speed = 0.5  # Скорость перемещения фона

    # Группы спрайтов
    all_sprites = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    boxes = pygame.sprite.Group()
    bonuses = pygame.sprite.Group()
    bullets = pygame.sprite.Group()

    # Создание объектов
    player = Player()
    terrain = Terrain()
    all_sprites.add(player, terrain)



    # Создаем врагов, коробки и бонусы
    for _ in range(LEVELS[LEVEL-1]['num_enemies']):
        enemy = Enemy(random.randint(1200, LEVEL_WIDTH - 50), random.randint(10, 400))
        all_sprites.add(enemy)
        enemies.add(enemy)

    for _ in range(LEVELS[LEVEL-1]['num_bonuses']):
        bonus = Bonus(random.randint(50, LEVEL_WIDTH - 50), random.randint(10, 550))
        all_sprites.add(bonus)
        bonuses.add(bonus)        

    for _ in range(LEVELS[LEVEL-1]['num_boxes']):
        box = Box(random.randint(50, LEVEL_WIDTH - 50), HEIGHT - 150)
        all_sprites.add(box)
        boxes.add(box)



    camera = Camera(LEVEL_WIDTH, HEIGHT)  # Создаем камеру    



def draw_background():
    for i in range((LEVEL_WIDTH // bg_width) + 1):
        # Фон движется в противоположную сторону движения камеры
        screen.blit(background, (i * bg_width + camera.camera.x * background_speed, 0))


load_level(LEVEL-1)

# Основной игровой цикл
running = True
score = 0

while running:
    clock.tick(FPS)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:  # Движение назад
                player.speed_x = -5
            elif event.key == pygame.K_d:  # Движение вперед
                player.speed_x = 5
            elif event.key == pygame.K_w:  # Прыжок
                player.jump()
            elif event.key == pygame.K_SPACE:  # Выстрел
                player.shoot()
        elif event.type == pygame.KEYUP:
            if event.key in [pygame.K_a, pygame.K_d]:
                player.speed_x = 0
            if event.key == pygame.K_SPACE:
                player.stop_shooting()

    # if player.speed_x != 0:
    #     update_background(player.speed_x / abs(player.speed_x))  # Обновляем положение фона


    all_sprites.update()
    camera.update(player)
    draw_background() # Отрисовываем фон


    # Проверка попаданий пуль во врагов
    hits = pygame.sprite.groupcollide(enemies, bullets, True, True)
    if hits:
        score += len(hits) * 100  # Очки за уничтожение врагов

    # Проверка соприкосновений игрока с врагами
    if pygame.sprite.spritecollideany(player, enemies):
        player.lives -= 1
        print(f"Player lives: {player.lives}")
        if player.lives <= 0:
            # running = False  # Игра заканчивается при отсутствии жизней
            load_level(LEVEL-1)

    # Проверка соприкосновений игрока с бонусами
    collected_bonuses = pygame.sprite.spritecollide(player, bonuses, True)
    if collected_bonuses:
        player.lives += len(collected_bonuses)
        print(f"Player lives: {player.lives}")


    for sprite in all_sprites:
        screen.blit(sprite.image, camera.apply(sprite))


    # Если игрок достиг правого края уровня, остановите камеру
    if camera.is_at_right_edge() and player.rect.right < LEVELS[LEVEL-1]['level_width']:
        # player.speed_x = 5  # Задайте скорость игрока

        # Если игрок достиг правого края уровня, загружается следующий уровень
        if player.rect.right >= LEVEL_WIDTH - 5:
            
            if LEVEL < len(LEVELS):
                LEVEL += 1
                print("Next level!")
                load_level(LEVEL-1)
            else:
                print("Вы прошли все уровни!")
                # running = False
                LEVEL = 1
                load_level(LEVEL-1)

    pygame.display.flip()

pygame.quit()