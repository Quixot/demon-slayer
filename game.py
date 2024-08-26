import pygame
import random
from pygame_emojis import load_emoji


# https://github.com/ScienceGamez/pygame_emojis
# https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer?tab=readme-ov-file
# https://openmoji.org/library


# Инициализация pygame
pygame.init()

# Настройки уровня
LEVEL_WIDTH = 2000  # Ширина уровня
WIDTH, HEIGHT = 1150, 600  # Размеры окна
# Настройки экрана
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Platformer")

# Загрузка изображения фона
background = pygame.image.load('background.png')
# Получение размеров изображения фона
bg_width, bg_height = background.get_size()
background_x1 = 0  # Начальная позиция первой копии фона
background_x2 = bg_width  # Начальная позиция второй копии фона (чтобы зацикливать фон)

background_speed = 0.5  # Скорость перемещения фона



# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK_BLUE = (10, 10, 50)
BROWN = (128, 0, 0)  # Цвет земли
RED = (128, 0, 0)

# Частота кадров
FPS = 60
clock = pygame.time.Clock()


# Загрузка изображения эмодзи
player_image =  load_emoji("😼", (64, 64))
enemy_image =   load_emoji("👾", (64, 64))
box_image =     load_emoji("🧱", (128, 128))
bonus_image =   load_emoji("💎", (64, 64))
bullet_image =  load_emoji("🥎", (16,16))


class Camera:
    def __init__(self, width, height):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height

    def apply(self, entity):
        return entity.rect.move(self.camera.topleft)

    def update(self, target):
        x = -target.rect.centerx + WIDTH // 2
        x = min(0, x)  # Левую границу фиксируем
        x = max(-(self.width - WIDTH), x)  # Правую границу ограничиваем уровнем
        self.camera = pygame.Rect(x, 0, self.width, self.height)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_image
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH // 2, HEIGHT - 150)
        self.speed_x = 0
        self.speed_y = 0
        self.on_ground = False
        self.lives = 3
        self.last_direction = 'right'  # В какую сторону смотрел плеер до остановки

    def update(self):
        self.gravity()

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
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
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

    def shoot(self):
        if self.last_direction == 'right':
            bullet = Bullet(self.rect.right, self.rect.centery, 5)
        else:
            bullet = Bullet(self.rect.left, self.rect.centery, -5)
        all_sprites.add(bullet)
        bullets.add(bullet)

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
                    print(hits[0].rect.top)
                    self.on_ground = False
                    self.on_platform = True
                    self.speed_y = 0
                elif self.speed_y < 0:
                    self.rect.top = hits[0].rect.bottom
                    self.speed_y = 0

    # def is_on_edge(self):
    #     hits = pygame.sprite.spritecollide(self, boxes, False)
    #     if hits:
    #         if self.rect.right <= hits[0].rect.left + 5 or self.rect.left >= hits[0].rect.right - 5:
    #             return True
    #     return False


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, speed_x):
        super().__init__()
        # self.image = pygame.Surface((10, 5))
        # self.image.fill(WHITE)
        self.image = bullet_image
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed_x = speed_x

    def update(self):
        self.rect.x += self.speed_x
        if self.rect.right < 0 or self.rect.left > LEVEL_WIDTH:
            self.kill()           


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = enemy_image
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed_x = random.choice([-2, 2])

    def update(self):
        self.rect.x += self.speed_x
        if self.rect.right > WIDTH or self.rect.left < 0:
            self.speed_x = -self.speed_x

class Box(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = box_image
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

class Bonus(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = bonus_image
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

class Terrain(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((WIDTH, 50))
        self.image.fill(BROWN)
        self.rect = self.image.get_rect()
        self.rect.x = 0
        self.rect.y = HEIGHT - 50

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
for _ in range(5):
    enemy = Enemy(random.randint(50, LEVEL_WIDTH - 50), HEIGHT - 100)
    all_sprites.add(enemy)
    enemies.add(enemy)

for _ in range(3):
    box = Box(random.randint(50, LEVEL_WIDTH - 50), HEIGHT - 100)
    all_sprites.add(box)
    boxes.add(box)

for _ in range(2):
    bonus = Bonus(random.randint(50, LEVEL_WIDTH - 50), HEIGHT - 100)
    all_sprites.add(bonus)
    bonuses.add(bonus)


camera = Camera(LEVEL_WIDTH, HEIGHT)  # Создаем камеру    

# Основной игровой цикл
running = True
score = 0


def update_background(player_velocity):
    global background_x1, background_x2

    background_x1 -= background_speed * player_velocity
    background_x2 -= background_speed * player_velocity


    print(player.rect.left)
    print(player.rect)
    if player.rect.left > 300:  # Если игрок не у левого края экрана
        background_x1 -= background_speed * player_velocity
        background_x2 -= background_speed * player_velocity

        if background_x1 <= -bg_width:
            background_x1 = background_x2 + bg_width

        if background_x2 <= -bg_width:
            background_x2 = background_x1 + bg_width
    else: 
        background_x1 = 0
        background_x2 = 1150


# def draw_background():
#     if player.rect.left > 300:
#         screen.blit(background, (background_x1, 0))
#         screen.blit(background, (background_x2, 0))
#     else:
#         screen.blit(background, (0, 0))
#         screen.blit(background, (1150, 0))

def draw_background():
    for i in range((LEVEL_WIDTH // bg_width) + 1):
        screen.blit(background, (i * bg_width - camera.camera.x * background_speed, 0))



while running:
    clock.tick(FPS)
    draw_background() # Отрисовываем фон
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                player.speed_x = -5
            elif event.key == pygame.K_RIGHT:
                player.speed_x = 5
            elif event.key == pygame.K_SPACE:
                player.jump()
            elif event.key == pygame.K_LCTRL:
                player.shoot()
        elif event.type == pygame.KEYUP:
            if event.key in [pygame.K_LEFT, pygame.K_RIGHT]:
                player.speed_x = 0

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
            running = True  # Игра заканчивается при отсутствии жизней

    # Проверка соприкосновений игрока с бонусами
    collected_bonuses = pygame.sprite.spritecollide(player, bonuses, True)
    if collected_bonuses:
        player.lives += len(collected_bonuses)
        print(f"Player lives: {player.lives}")


    for sprite in all_sprites:
        screen.blit(sprite.image, camera.apply(sprite))

    # screen.fill(DARK_BLUE)
    all_sprites.draw(screen)

    
    

    pygame.display.flip()

pygame.quit()