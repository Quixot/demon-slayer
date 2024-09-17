from config.config import *


# https://github.com/ScienceGamez/pygame_emojis
# https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer?tab=readme-ov-file
# https://openmoji.org/library


class Camera:
    def __init__(self, width, height):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height

    def apply(self, entity):
        return entity.rect.move(self.camera.topleft)

    def update(self, target):
        x = -target.rect.centerx + WIDTH // 2 - 100
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
        global weapons 

        if weapons > 0:
            self.is_shooting = True
            if self.last_direction == 'right':
                bullet = Bullet(self.rect.right, self.rect.centery, 5)
            else:
                bullet = Bullet(self.rect.left, self.rect.centery, -5)
            all_sprites.add(bullet)
            bullets.add(bullet)
            weapons -= 1

    def stop_shooting(self):
        self.is_shooting = False        

    def collide_with_boxes(self, direction):
        if direction == 'x':
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
        self.lifetime = 1000  # Время жизни пули в миллисекундах
        self.spawn_time = pygame.time.get_ticks()  # Время создания пули

    def update(self):
        self.rect.x += self.speed_x

        # Проверка времени жизни
        current_time = pygame.time.get_ticks()

        if self.rect.right < 0 or self.rect.left > LEVEL_WIDTH or current_time - self.spawn_time > self.lifetime:
            self.kill()           



class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = random.choice(enemy_images)  # Случайный выбор изображения врага
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed_x = random.choice(LEVELS[LEVEL-1]['enemy_speed_range'])
        self.speed_y = 0
        self.attack_speed = 7  # Скорость движения врага к игроку
        self.attack_distance = 550  # Расстояние, на котором враг начинает атаковать
        self.visibility = 0
        self.image.set_alpha(self.visibility)    # Полная прозрачность

    def update(self):
        # Проверяем расстояние до игрока
        distance_to_player = self.rect.centerx - player.rect.centerx

        if abs(distance_to_player) < self.attack_distance:
            self.visibility += 15
            if self.visibility > 255:
                self.visibility = 255
            self.image.set_alpha(self.visibility)  # Полная видимость
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
        self.image = box_images[2]
        self.rect = self.image.get_rect()
        # Сколько раз попали
        self.hit_cout = 3
        # Размещение коробки на земле
        self.rect.x = x
        self.rect.y = HEIGHT - 40 - self.rect.height  # Вычисление Y-координаты для того, чтобы объект стоял на земле
        

class Bonus(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = bonus_image
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

class Life(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = life_image
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

class Ammunition(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = ammunition_image
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)            


class Terrain(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((LEVEL_WIDTH, 50)) # , pygame.SRCALPHA
        self.rect = self.image.get_rect()
        self.rect.x = 0
        self.rect.y = HEIGHT - 50

score = 0
bonus = 0
weapons = 50
lives_score = 3

# Функция отрисовки текста
def draw_text(text, font, color, surface, x, y):
    text_obj = font.render(text, True, color)
    text_rect = text_obj.get_rect()
    text_rect.center = (x, y)
    surface.blit(text_obj, text_rect)
# Настройки
def main_menu():
    screen.fill(WHITE)
    # draw_text("Main Menu", font, BLACK, screen, WIDTH // 2, HEIGHT // 2 - 100)
    # draw_text("1. Start Game", font, BLACK, screen, WIDTH // 2, HEIGHT // 2)
    # draw_text("2. Settings", font, BLACK, screen, WIDTH // 2, HEIGHT // 2 + 50)
    # draw_text("3. Quit", font, BLACK, screen, WIDTH // 2, HEIGHT // 2 + 100)
    # Отображение изображения в меню
    # Загрузка изображения
    bonus_pict = pygame.image.load(img("bonus.png")) 
    bonus_pict = pygame.transform.scale(bonus_pict, (200, 200))  # Изменение размера изображения (опционально)

    screen.blit(bonus_pict, (WIDTH // 2 - 100, HEIGHT // 2 - 200))  # Центрирование изображения
    draw_text(f"weapons: {weapons}", font, BLACK, screen, WIDTH // 2, HEIGHT // 2)
    draw_text(f"bonuses: {bonus}", font, BLACK, screen, WIDTH // 2, HEIGHT // 2 + 50)
    pygame.display.flip()


def load_level(level_number):
    global all_sprites, enemies, boxes, bonuses, weapons, lives, ammunitions, bullets, player, terrain, camera, background, bg_width, bg_height, background_speed

    # Загрузка изображения фона
    background = pygame.image.load(img(LEVELS[LEVEL-1]['background']))

    bg_width, bg_height = background.get_size()
    background_speed = 0.5  # Скорость перемещения фона

    # Группы спрайтов
    all_sprites = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    boxes = pygame.sprite.Group()
    bonuses = pygame.sprite.Group()
    lives = pygame.sprite.Group()
    ammunitions = pygame.sprite.Group()
    bullets = pygame.sprite.Group()

    # Создание объектов
    player = Player()
    terrain = Terrain()
    all_sprites.add(player, terrain)



    # Создаем врагов
    for _ in range(LEVELS[level_number]['num_enemies']):
        enemy = Enemy(random.randint(1200, LEVEL_WIDTH - 50), random.randint(10, 400))
        all_sprites.add(enemy)
        enemies.add(enemy)


    # Создаем бонусы
    for _ in range(LEVELS[level_number]['num_bonuses']):
        bonus = Bonus(random.randint(1200, LEVEL_WIDTH - 50), random.randint(10, 550))
        all_sprites.add(bonus)
        bonuses.add(bonus)   


    # Создаем аптечки
    for _ in range(LEVELS[level_number]['num_lives']):
        life = Life(random.randint(1200, LEVEL_WIDTH - 50), random.randint(10, 550))
        all_sprites.add(life)
        lives.add(life)           


    # Создаем боеприпасы
    for _ in range(LEVELS[level_number]['num_ammunition']):
        ammunition = Ammunition(random.randint(1200, LEVEL_WIDTH - 50), random.randint(10, 550))
        all_sprites.add(ammunition)
        ammunitions.add(ammunition)       


    # Создаем камни
    for _ in range(LEVELS[level_number]['num_boxes']):
        box = Box(random.randint(800, LEVEL_WIDTH - 50), HEIGHT - 100)
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
# Игровое состояние
game_state = "menu"  # Возможные состояния: "menu", "settings", "game"

# Инициализация шрифта
font = pygame.font.Font(None, 34)  # None - шрифт по умолчанию, 74 - размер


while running:
    clock.tick(FPS)
    
    
    if game_state == "menu": # Если меню
        main_menu()
    else: # Если игра

        all_sprites.update()
        camera.update(player)
        draw_background() # Отрисовываем фон


        # Проверка попаданий пуль во врагов
        hits = pygame.sprite.groupcollide(enemies, bullets, True, True)
        if hits:
            score += len(hits)  # Очки за уничтожение врагов

        # Проверка соприкосновений игрока с врагами
        if pygame.sprite.spritecollideany(player, enemies):
            lives_score -= 1
            print(f"Player lives: {lives_score}")
            
            if lives_score <= 0:
                running = False  # Игра заканчивается при отсутствии жизней
            else: 
                load_level(LEVEL-1)

        # Проверка соприкосновений игрока с бонусами
        collected_bonuses = pygame.sprite.spritecollide(player, bonuses, True)
        if collected_bonuses:
            print(f"Bonus: {bonus}")
            bonus += 1
            if bonus == 10:
                weapons 
                
                bonus = 0

        # Проверка соприкосновений игрока с аптечками
        collected_lives = pygame.sprite.spritecollide(player, lives, True)
        if collected_lives:
            print(f"Player lives: {lives_score}")
            lives_score += 1 # len(collected_bonuses)
            

        # Проверка соприкосновений игрока с аптечками
        collected_ammunitions = pygame.sprite.spritecollide(player, ammunitions, True)
        if collected_ammunitions:
            print(f"Player ammunitions: {weapons}")
            weapons += 10 # len(collected_bonuses)


        # Проверка соприкосновений пуль с камнями
        hits = pygame.sprite.groupcollide(bullets, boxes, True, False)
        if hits:
            for obj_bullet, obj_box in hits.items():

                print(player.last_direction, obj_box[0], obj_box[0].hit_cout, end="\r")
                
                if obj_box[0].hit_cout == 1:
                    obj_box[0].kill()
                if player.last_direction == "right":
                    
                    obj_box[0].image = box_images[obj_box[0].hit_cout - 2]   
                    obj_box[0].hit_cout -= 1 
                else:
                    obj_box[0].image = box_images[obj_box[0].hit_cout + 1]
                    obj_box[0].hit_cout -= 1 

        # Отображение текста на экране 
        score_text = font.render(f"Score: {score}", True, (255, 153, 0))  # Цвет текста
        screen.blit(score_text, (10, 10))  # Позиция текста (10, 10)

        bonus_text = font.render(f"Bonuses: {bonus}", True, (255, 204, 0))  # Цвет текста
        screen.blit(bonus_text, (10, 40))  # Позиция текста (10, 10)

        lives_text = font.render(f"Lives: {lives_score}", True, (0, 204, 102))  # Цвет текста
        screen.blit(lives_text, (10, 70))  # Позиция текста (10, 10)

        weapons_text = font.render(f"Weapons: {weapons}", True, (153, 0, 0))  # Цвет текста
        screen.blit(weapons_text, (10, 100))  # Позиция текста (10, 10)

        for sprite in all_sprites:
            screen.blit(sprite.image, camera.apply(sprite))


        # Если игрок достиг правого края уровня, остановите камеру
        if camera.is_at_right_edge() and player.rect.right < LEVELS[LEVEL-1]['level_width']:
            # player.speed_x = 5  # Задайте скорость игрока

            # Если игрок достиг правого края уровня, загружается следующий уровень
            if player.rect.right >= LEVEL_WIDTH - 5:
                
                if LEVEL < len(LEVELS):
                    LEVEL += 1
                    print(f"Next level! {LEVEL}")
                    load_level(LEVEL-1)
                else:
                    print("Вы прошли все уровни!")
                    # running = False
                    LEVEL = 1
                    load_level(LEVEL-1)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if game_state == "menu":
                if event.key == pygame.K_1:
                    game_state = "game"
                elif event.key == pygame.K_2:
                    game_state = "settings"
                elif event.key == pygame.K_3:
                    running = False
            elif game_state == "game":
                if event.key == pygame.K_2:
                    game_state = "menu"
                elif event.key == pygame.K_a:  # Движение назад
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

    pygame.display.flip()

pygame.quit()