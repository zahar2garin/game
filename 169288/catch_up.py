import pygame
import math
import random
import time
import sys

# Инициализация Pygame
pygame.init()

# Константы
WIDTH, HEIGHT = 800, 600
FPS = 60
MOVE_SPEED = 4
ENEMY_SPEED = 2
MAX_ENEMIES = 7
TIMER_LIMIT = 60
ENEMY_SIZE = 50
BONUS_SIZE = 30  # Размер бонуса
BONUS_DURATION = 5  # Время неуязвимости в секундах
BONUS_INTERVAL = 15  # Интервал между бонусами в секундах

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Создаем экран
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Выживание")

# Загружаем изображения
background_image = pygame.image.load('2.jpg').convert()
background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))
character_image = pygame.image.load('ва-removebg-preview.png').convert_alpha()
character_image = pygame.transform.scale(character_image, (int(character_image.get_width() * 0.3), int(character_image.get_height() * 0.3)))

# Загружаем изображение врага
enemy_image = pygame.image.load('тварь.png').convert_alpha()
enemy_image = pygame.transform.scale(enemy_image, (ENEMY_SIZE, ENEMY_SIZE))

# Загружаем изображение бонуса
bonus_image = pygame.image.load('гщо.png').convert_alpha()
bonus_image = pygame.transform.scale(bonus_image, (BONUS_SIZE, BONUS_SIZE))  # Измените размер при необходимости

# Загружаем изображение фона для меню
menu_background = pygame.image.load('фон.jpg').convert()
menu_background = pygame.transform.scale(menu_background, (WIDTH, HEIGHT))

# Класс для пуль
class Bullet:
    def __init__(self, x, y, angle):
        self.image = pygame.Surface((10, 5))
        self.image.fill(BLACK)
        self.rect = self.image.get_rect(center=(x, y))
        self.angle = angle
        self.speed = 10

    def update(self):
        self.rect.x += self.speed * math.cos(math.radians(self.angle))
        self.rect.y -= self.speed * math.sin(math.radians(self.angle))

    def draw(self, surface):
        surface.blit(self.image, self.rect.topleft)

# Класс для бонуса
class Bonus:
    def __init__(self):
        self.rect = pygame.Rect(random.randint(0, WIDTH - BONUS_SIZE), random.randint(0, HEIGHT - BONUS_SIZE), BONUS_SIZE, BONUS_SIZE)
    
    def draw(self, surface):
        surface.blit(bonus_image, self.rect.topleft)

# Функция для отображения текста
def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect(center=(x, y))
    surface.blit(textobj, textrect)
    return textrect  # Возвращаем прямоугольник текста для проверки нажатия

# Функция для спавна врагов
def spawn_enemy():
    side = random.choice(['top', 'bottom', 'left', 'right'])
    if side == 'top':
        x = random.randint(0, WIDTH - ENEMY_SIZE)
        y = 0
    elif side == 'bottom':
        x = random.randint(0, WIDTH - ENEMY_SIZE)
        y = HEIGHT - ENEMY_SIZE
    elif side == 'left':
        x = 0
        y = random.randint(0, HEIGHT - ENEMY_SIZE)
    elif side == 'right':
        x = WIDTH - ENEMY_SIZE
        y = random.randint(0, HEIGHT - ENEMY_SIZE)
    return enemy_image.get_rect(topleft=(x, y))

# Функция для меню
def menu():
    while True:
        screen.blit(menu_background, (0, 0))  # Отображаем фон меню
        play_button_rect = draw_text('Играть (Нажмите Enter)', pygame.font.Font(None, 36), BLACK, screen, WIDTH // 2, HEIGHT // 2)
        exit_button_rect = draw_text('Выход (Нажмите Escape)', pygame.font.Font(None, 36), BLACK, screen, WIDTH // 2, HEIGHT // 2 + 40)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:  # Играть
                    return
                if event.key == pygame.K_ESCAPE:  # Выход
                    pygame.quit()
                    sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Левая кнопка мыши
                    mouse_pos = pygame.mouse.get_pos()
                    if play_button_rect.collidepoint(mouse_pos):  # Проверка нажатия на кнопку "Играть"
                        return
                    if exit_button_rect.collidepoint(mouse_pos):  # Проверка нажатия на кнопку "Выход"
                        pygame.quit()
                        sys.exit()

        pygame.display.flip()

# Основная функция игры
def game():
    global kill_count
    bullets = []
    enemies = [spawn_enemy() for _ in range(MAX_ENEMIES)]
    character_rect = character_image.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    kill_count = 0
    game_over = False
    victory = False
    invincible = False
    invincible_start_time = 0
    clock = pygame.time.Clock()
    start_time = pygame.time.get_ticks()
    last_bonus_time = 0  # Время последнего использования бонуса
    bonus_available = True  # Бонус доступен для использования

    # Создаем бонус
    bonus = Bonus()
    
    # Запуск музыки при начале игры
    pygame.mixer.music.load('muzyka-apokalipsisa-muzyka-apokalipsisa.mp3')
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 3:  # Правая кнопка мыши
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    angle = math.degrees(math.atan2(character_rect.centery - mouse_y, mouse_x - character_rect.centerx))
                    bullets.append(Bullet(character_rect.centerx, character_rect.centery, angle))

        if not game_over and not victory:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_w]: character_rect.y -= MOVE_SPEED
            if keys[pygame.K_s]: character_rect.y += MOVE_SPEED
            if keys[pygame.K_a]: character_rect.x -= MOVE_SPEED
            if keys[pygame.K_d]: character_rect.x += MOVE_SPEED

            for bullet in bullets[:]:
                bullet.update()
                if bullet.rect.x < 0 or bullet.rect.x > WIDTH or bullet.rect.y < 0 or bullet.rect.y > HEIGHT:
                    bullets.remove(bullet)

                for enemy in enemies[:]:
                    if bullet.rect.colliderect(enemy):
                        bullets.remove(bullet)
                        enemies.remove(enemy)
                        enemies.append(spawn_enemy())
                        kill_count += 1
                        break

            # Проверка на столкновение с бонусом
            if character_rect.colliderect(bonus.rect):
                invincible = True
                invincible_start_time = time.time()  # Запоминаем время активации
                last_bonus_time = time.time()  # Запоминаем время использования бонуса
                bonus_available = False  # Бонус больше недоступен
                bonus = Bonus()  # Спавним новый бонус

            for enemy_rect in enemies:
                if not invincible and character_rect.colliderect(enemy_rect):
                    game_over = True

            for enemy_rect in enemies:
                enemy_dx = character_rect.centerx - enemy_rect.centerx
                enemy_dy = character_rect.centery - enemy_rect.centery
                distance = math.hypot(enemy_dx, enemy_dy)
                if distance > 0:
                    enemy_rect.x += ENEMY_SPEED * (enemy_dx / distance)
                    enemy_rect.y += ENEMY_SPEED * (enemy_dy / distance)

            mouse_x, mouse_y = pygame.mouse.get_pos()
            angle = math.degrees(math.atan2(character_rect.centery - mouse_y, mouse_x - character_rect.centerx))
            rotated_image = pygame.transform.rotate(character_image, angle)
            rotated_rect = rotated_image.get_rect(center=character_rect.center)

            # Проверка временной неуязвимости
            if invincible and (time.time() - invincible_start_time > BONUS_DURATION):
                invincible = False  # Сброс неуязвимости
                bonus_available = True  # Бонус снова доступен после использования

            elapsed_time = (pygame.time.get_ticks() - start_time) // 1000
            if elapsed_time >= TIMER_LIMIT:
                victory = True

            # Проверка времени после использования бонуса
            if not bonus_available and (time.time() - last_bonus_time >= BONUS_INTERVAL):
                bonus = Bonus()  # Спавним новый бонус
                bonus_available = True  # Теперь бонус доступен

            screen.blit(background_image, (0, 0))
            screen.blit(rotated_image, rotated_rect.topleft)

            for enemy_rect in enemies:
                screen.blit(enemy_image, enemy_rect.topleft)

            for bullet in bullets:
                bullet.draw(screen)

            # Рисуем бонус
            bonus.draw(screen)

            timer_text = f"Время: {TIMER_LIMIT - elapsed_time} сек"
            kill_text = f"Убито врагов: {kill_count}"
            if invincible:
                remaining_time = BONUS_DURATION - (time.time() - invincible_start_time)
                invincibility_text = f"Неуязвимость: {int(remaining_time)} сек"
            else:
                invincibility_text = ""

            font = pygame.font.Font(None, 36)
            screen.blit(font.render(timer_text, True, WHITE), (10, 10))
            screen.blit(font.render(kill_text, True, WHITE), (10, 50))
            screen.blit(font.render(invincibility_text, True, GREEN), (10, 90))

        elif victory:
            draw_text("Вы победили", pygame.font.Font(None, 74), RED, screen, WIDTH // 2, HEIGHT // 2)
            pygame.display.flip()
            time.sleep(5)
            return

        elif game_over:
            draw_text("Вы проиграли", pygame.font.Font(None, 74), RED, screen, WIDTH // 2, HEIGHT // 2)
            pygame.display.flip()
            time.sleep(5)
            return

        pygame.display.flip()
        clock.tick(FPS)

# Запуск меню и игры
menu()
game()

# Завершение Pygame
pygame.quit()