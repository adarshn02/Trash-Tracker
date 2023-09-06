import pygame
import os
import random
pygame.font.init()

pygame.mixer.init()
pygame.mixer.music.load("back.mp3")
pygame.mixer.music.play(-1)

WIDTH, HEIGHT = 750, 750
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(
    "Traash Clash Ultimate - Spreading awareness about waste management")
icon = pygame.image.load(os.path.join(
    "assets", "01icon.png"))
pygame.display.set_icon(icon)

# Load images
RED_bin = pygame.image.load(os.path.join("assets", "pixel_bin_red_small.png"))
GREEN_bin = pygame.image.load(os.path.join(
    "assets", "pixel_bin_green_small.png"))
BLUE_bin = pygame.image.load(os.path.join(
    "assets", "pixel_bin_blue_small.png"))

# Player
YELLOW_bin = pygame.image.load(os.path.join("assets", "pixel_bin_yellow.png"))

# Wastes
RED_waste = pygame.image.load(os.path.join("assets", "pixel_waste_red.png"))
GREEN_waste = pygame.image.load(
    os.path.join("assets", "pixel_waste_green.png"))
BLUE_waste = pygame.image.load(os.path.join("assets", "pixel_waste_blue.png"))
YELLOW_waste = pygame.image.load(
    os.path.join("assets", "pixel_net_yellow.png"))

# Background
BG = pygame.transform.scale(pygame.image.load(
    os.path.join("assets", "backgroundMain.png")), (WIDTH, HEIGHT))
BG1 = pygame.transform.scale(pygame.image.load(
    os.path.join("assets", "backgroundIntro.png")), (WIDTH, HEIGHT))
BG2 = pygame.transform.scale(pygame.image.load(
    os.path.join("assets", "backgroundOutro.png")), (WIDTH, HEIGHT))

# Waste Class for enemy bins bullets


class Waste:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not(self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)

# Bin Class for enemy bins


class Bin:
    COOLDOWN = 30

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.bin_img = None
        self.waste_img = None
        self.wastes = []
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.bin_img, (self.x, self.y))
        for waste in self.wastes:
            waste.draw(window)

    def move_wastes(self, vel, obj):
        self.cooldown()
        for waste in self.wastes:
            waste.move(vel)
            if waste.off_screen(HEIGHT):
                self.wastes.remove(waste)
            elif waste.collision(obj):
                obj.health -= 10
                self.wastes.remove(waste)

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            waste = Waste(self.x, self.y, self.waste_img)
            self.wastes.append(waste)
            self.cool_down_counter = 1

    def get_width(self):
        return self.bin_img.get_width()

    def get_height(self):
        return self.bin_img.get_height()

# Player Class for Hero / Sprite


class Player(Bin):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.bin_img = YELLOW_bin
        self.waste_img = YELLOW_waste
        self.mask = pygame.mask.from_surface(self.bin_img)
        self.max_health = health

    def move_wastes(self, vel, objs):
        self.cooldown()
        for waste in self.wastes:
            waste.move(vel)
            if waste.off_screen(HEIGHT):
                self.wastes.remove(waste)
            else:
                for obj in objs:
                    if waste.collision(obj):
                        objs.remove(obj)
                        if waste in self.wastes:
                            self.wastes.remove(waste)

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(window, (255, 0, 0), (self.x, self.y +
                         self.bin_img.get_height() + 10, self.bin_img.get_width(), 10))
        pygame.draw.rect(window, (0, 255, 0), (self.x, self.y + self.bin_img.get_height() +
                         10, self.bin_img.get_width() * (self.health/self.max_health), 10))

# Enemy Class for all enemy


class Enemy(Bin):
    COLOR_MAP = {
        "red": (RED_bin, RED_waste),
        "green": (GREEN_bin, GREEN_waste),
        "blue": (BLUE_bin, BLUE_waste)
    }

    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.bin_img, self.waste_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.bin_img)

    def move(self, vel):
        self.y += vel

    def shoot(self):
        if self.cool_down_counter == 0:
            waste = Waste(self.x-20, self.y, self.waste_img)
            self.wastes.append(waste)
            self.cool_down_counter = 1


def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None

# main function for game


def main():
    run = True
    FPS = 60
    level = 0
    lives = 5
    main_font = pygame.font.SysFont("comicsans", 50)
    lost_font = pygame.font.SysFont("comicsans", 50)

    enemies = []
    wave_length = 5
    enemy_vel = 1

    player_vel = 5
    waste_vel = 5

    player = Player(300, 630)

    clock = pygame.time.Clock()

    lost = False
    lost_count = 0

    def redraw_window():

        WIN.blit(BG, (0, 0))
        # draw text
        lives_label = main_font.render(f"Health: {lives}", 1, (0, 255, 255))
        level_label = main_font.render(f"Level: {level}", 1, (0, 255, 255))

        WIN.blit(lives_label, (10, 10))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))

        for enemy in enemies:
            enemy.draw(WIN)

        player.draw(WIN)

        if lost:
            WIN.blit(BG2, (0, 0))
            lost_label = lost_font.render("You Lost!!", 1, (255, 255, 255))
            WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 350))

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
            wave_length += 5
            for i in range(wave_length):
                enemy = Enemy(random.randrange(
                    50, WIDTH-100), random.randrange(-1500, -100), random.choice(["red", "blue", "green"]))
                enemies.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player.x - player_vel > 0:  # left
            player.x -= player_vel
        if keys[pygame.K_d] and player.x + player_vel + player.get_width() < WIDTH:  # right
            player.x += player_vel
        if keys[pygame.K_w] and player.y - player_vel > 0:  # up
            player.y -= player_vel
        if keys[pygame.K_s] and player.y + player_vel + player.get_height() + 15 < HEIGHT:  # down
            player.y += player_vel
        if keys[pygame.K_SPACE]:
            player.shoot()

        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_wastes(waste_vel, player)

            if random.randrange(0, 2*60) == 1:
                enemy.shoot()

            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)
            elif enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)

        player.move_wastes(-waste_vel, enemies)

# Main menu


def main_menu():
    title_font = pygame.font.SysFont("comicsans", 50)
    run = True
    while run:
        WIN.blit(BG1, (0, 0))
        title_label = title_font.render(
            "Press the mouse to begin...", 1, (255, 255, 255))
        WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 350))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
    pygame.quit()


main_menu()
