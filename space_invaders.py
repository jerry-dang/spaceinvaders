import pygame
import os
import time
import random

pygame.font.init()

WIDTH, HEIGHT = 800, 800
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Missile Dodger")

# Images
BLUE_MISSILE = pygame.transform.scale(pygame.image.load(os.path.join("assets", "blue_missile.png")), (60, 60))
PURPLE_MISSILE = pygame.transform.scale(pygame.image.load(os.path.join("assets", "purple_missile.png")), (60, 60))
GREEN_MISSILE = pygame.transform.scale(pygame.image.load(os.path.join("assets", "green_missile.png")), (60, 60))
RED_MISSILE = pygame.transform.scale(pygame.image.load(os.path.join("assets", "red_missile.png")), (60, 60))
PINK_MISSILE = pygame.transform.scale(pygame.image.load(os.path.join("assets", "pink_missile.png")), (60, 60))
LEVEL10_BOSS = pygame.transform.scale(pygame.image.load(os.path.join("assets", "lvl10_boss.png")), (60, 60))
LEVEL20_BOSS = pygame.transform.scale(pygame.image.load(os.path.join("assets", "lvl20_boss.png")), (60, 60))

# Player Ship/Boat
ORANGE_SHIP = pygame.transform.scale(pygame.image.load(os.path.join("assets", "orange_spaceship.png")), (80, 80))

# Small Missiles
BLUE_SMISSILE = pygame.transform.scale(pygame.image.load(os.path.join("assets", "blue_smissile.png")), (10, 30))
PURPLE_SMISSILE = pygame.transform.scale(pygame.image.load(os.path.join("assets", "purple_smissile.png")), (10, 30))
GREEN_SMISSILE = pygame.transform.scale(pygame.image.load(os.path.join("assets", "green_smissile.png")), (10, 30))
ORANGE_SMISSILE = pygame.transform.scale(pygame.image.load(os.path.join("assets", "orange_smissile.png")), (10, 30))
PINK_SMISSILE = pygame.transform.scale(pygame.image.load(os.path.join("assets", "pink_smissile.png")), (60, 60))

# Power-Ups
HEALTH_PACK = pygame.transform.scale(pygame.image.load(os.path.join("assets", "health_pack.png")), (60, 60))
SPEED_BOOST = pygame.transform.scale(pygame.image.load(os.path.join("assets", "speed_boost.png")), (60, 60))

# Background
BACKGROUND = pygame.image.load(os.path.join("assets", "black_background.png"))


class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, velocity):
        self.y += velocity

    def off_screen(self, height):
        return not (height >= self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)


class Ship:
    COOLDOWN = 45

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, velocity, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(velocity)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x + 30, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()


class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = ORANGE_SHIP
        self.laser_img = ORANGE_SMISSILE
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    def move_lasers(self, velocity, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(velocity)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        obj.health -= 50
                        if obj.health == 0:
                            objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(window, (255, 0, 0), (self.x, self.y + self.ship_img.get_height() + 10,
                                               self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0, 255, 0), (self.x, self.y + self.ship_img.get_height() + 10,
                                               self.ship_img.get_width() * (self.health / self.max_health), 10))


class Enemy(Ship):
    COLOUR_CODE = {
        "green": (GREEN_MISSILE, GREEN_SMISSILE),
        "blue": (BLUE_MISSILE, BLUE_SMISSILE),
        "purple": (PURPLE_MISSILE, PURPLE_SMISSILE)
    }

    def __init__(self, x, y, colour, health=100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.COLOUR_CODE[colour]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x + 25, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def move(self, velocity):
        self.y += velocity


class PowerUp:
    TYPES = {
        "speed_boost": SPEED_BOOST,
        "health_pack": HEALTH_PACK
    }

    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def move(self, velocity):
        self.y += velocity


def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) is not None


def main():
    run = True
    lost = False
    lost_count = 0

    FPS = 120
    level = 0
    lives = 5
    player_velocity = 5
    main_font = pygame.font.SysFont("comicsans", 50)
    lost_font = pygame.font.SysFont("comicsans", 60)

    enemies = []
    wave_length = 5
    enemy_velocity = 1

    powerups = []
    num_of_powerups = 2
    powerup_velocity = 3

    laser_velocity = 5

    player = Player(300, 630)

    clock = pygame.time.Clock()

    def redraw_window():
        WIN.blit(BACKGROUND, (0, 0))
        # text
        level_label = main_font.render(f"Level: {level}", 1, (255, 255, 255))
        lives_label = main_font.render(f"Lives: {lives}", 1, (255, 255, 255))

        WIN.blit(level_label, (10, 10))
        WIN.blit(lives_label, (WIDTH - lives_label.get_width() - 10, 10))

        player.draw(WIN)

        for enemy in enemies:
            enemy.draw(WIN)

        if lost:
            lost_label = lost_font.render("You Lost!", 1, (255, 255, 255))
            WIN.blit(lost_label, (WIDTH / 2 - lost_label.get_width() / 2, 400))

        pygame.display.update()

    while run:
        clock.tick(FPS)

        redraw_window()

        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1

        if lost:
            if lost_count > FPS * 3:
                run = False
            else:
                continue

        if len(enemies) == 0:
            level += 1
            if 1 <= level <= 5:
                wave_length += 3
                # enemy_velocity += 2
                for i in range(wave_length):
                    enemy = Enemy(random.randrange(50, WIDTH - 100), random.randrange(-2000, -300),
                                  random.choice(["purple", "blue", "green"]))
                    enemies.append(enemy)
            if 6 <= level <= 7:
                wave_length += 5
                for i in range(wave_length):
                    enemy = Enemy(random.randrange(50, WIDTH - 100), random.randrange(-3000, -300),
                                  random.choice(["purple", "blue", "green"]))
                    enemies.append(enemy)
                for j in range(num_of_powerups):
                    powerup = PowerUp(random.randrange(50, WIDTH - 100), random.randrange(-3000, -300),
                                      random.choice(["speed_boost", "health_pack"]))
                    powerups.append(powerup)
            if 8 <= level <= 9:
                wave_length += 5
                for i in range(wave_length):
                    enemy = Enemy(random.randrange(50, WIDTH - 100), random.randrange(-3000, -300),
                                  random.choice(["purple", "blue", "green"]))  # need to add new enemy ship here
                    enemies.append(enemy)
            # boss level: if level == 10:
            wave_length = 10
            if 11 <= level <= 15:  # speed waves
                wave_length += 3
                enemy_velocity = 4
                for i in range(wave_length):
                    enemy = Enemy(random.randrange(50, WIDTH - 100), random.randrange(-5000, -300),
                                  random.choice(["purple", "blue", "green"]))  # need to add new enemy ship here
                    enemies.append(enemy)
                for j in range(num_of_powerups):
                    powerup = PowerUp(random.randrange(50, WIDTH - 100), random.randrange(-3000, -300),
                                      random.choice(["speed_boost", "health_pack"]))
                    powerups.append(powerup)
            wave_length = 30
            enemy_velocity = 1
            if 16 <= level <= 17:  # need to alternate speed of ships
                wave_length += 5
                for i in range(wave_length):
                    enemy = Enemy(random.randrange(50, WIDTH - 100), random.randrange(-5000, -300),
                                  random.choice(["purple", "blue", "green"]))
                    enemies.append(enemy)
            if 18 <= level <= 19:
                wave_length += 5
                for i in range(wave_length):
                    enemy = Enemy(random.randrange(50, WIDTH - 100), random.randrange(-5000, -300),
                                  random.choice(["purple", "blue", "green"]))  # need to add new enemy ship here
                    enemies.append(enemy)
                for j in range(num_of_powerups):
                    powerup = PowerUp(random.randrange(50, WIDTH - 100), random.randrange(-3000, -300),
                                      random.choice(["speed_boost", "health_pack"]))
                    powerups.append(powerup)
            # final boss level: if level == 20:

        # Check for an event every 60 frames per second (e.g. quit, health zero, win...)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player.x - player_velocity > 0:  # going left
            player.x -= player_velocity
        if keys[pygame.K_d] and player.x + player_velocity + player.get_width() < WIDTH:  # going right
            player.x += player_velocity
        if keys[pygame.K_w] and player.y - player_velocity > 0:  # going up
            player.y -= player_velocity
        if keys[pygame.K_s] and player.y + player_velocity + player.get_height() + 10 < HEIGHT:  # going down
            player.y += player_velocity
        if keys[pygame.K_SPACE]:
            player.shoot()

        for powerup in powerups[:]:
            powerup.move(powerup_velocity)

            if collide(powerup, player):
                if powerup.TYPES == "speed_boost":
                    player_velocity += 2  # for 5 seconds (need to implement)
                if powerup.TYPES == "health_pack":
                    player.health += 20

        for enemy in enemies[:]:
            enemy.move(enemy_velocity)
            enemy.move_lasers(laser_velocity, player)

            if random.randrange(0, 2 * 120) == 1:
                enemy.shoot()

            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)
            elif enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)

        player.move_lasers(-laser_velocity, enemies)


def main_menu():
    title_font = pygame.font.SysFont("comicsans", 70)
    run = True
    while run:
        WIN.blit(BACKGROUND, (0, 0))
        title_label = title_font.render("Press the mouse to begin...", 1, (255, 255, 255))
        WIN.blit(title_label, (WIDTH / 2 - title_label.get_width() / 2, 400))

        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
    pygame.quit()


main_menu()
main()
