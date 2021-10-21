import pygame
import os
import time
import random

pygame.font.init()
pygame.init()

levelSound = pygame.mixer.Sound('level_sound.mp3')
explode_sound = pygame.mixer.Sound('explode_music.mp3')
Hitsound = pygame.mixer.Sound('hit_sound.mp3')
Lose_sound = pygame.mixer.Sound('gamelosing_music.wav')

music_on = True

musics = ["tetris-gameboy-01.mp3", "tetris-gameboy-02.mp3", "tetris-gameboy-03.mp3", "tetris-gameboy-04.mp3"]


if music_on:
    music = pygame.mixer.music.load(musics[1])
    pygame.mixer.music.play(-1)


WIDTH, HEIGHT = 800, 750
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('EARTH PROTECTOR')

icon = pygame.image.load('Earth_protectericon.png')
pygame.display.set_icon(icon)


# Images
UFO_SPACE_SHIP = pygame.image.load(os.path.join("images/ufo.png"))
ENEMYl1_SPACE_SHIP = pygame.image.load(os.path.join("images/enemyship_l1.png"))
ENEMYl2_SPACE_SHIP = pygame.image.load(os.path.join("images/enemyship_l2.png"))

# Player
Car1 = pygame.image.load(os.path.join("images/car1.png"))
Car3 = pygame.image.load(os.path.join("images/car3.png"))
Car2 = pygame.image.load(os.path.join("images/car4.png"))
Car4 = pygame.image.load(os.path.join("images/car5.png"))
Car5 = pygame.image.load(os.path.join("images/car6.png"))
Car6 = pygame.image.load(os.path.join("images/car7.png"))
spaceship = pygame.image.load(os.path.join("images/space-ship.png"))

# Lasers
RED_LASER = pygame.image.load(os.path.join("images/pixel_laser_red.png"))
GREEN_LASER = pygame.image.load(os.path.join("images/bullet_up.png"))

# BACKGROUNDS
BG = pygame.transform.scale(pygame.image.load(os.path.join("images/BG.png")), (WIDTH, HEIGHT))
BG1 = pygame.transform.scale(pygame.image.load(os.path.join("images/BG_1.png")), (WIDTH, HEIGHT))
BG2 = pygame.transform.scale(pygame.image.load(os.path.join("images/BG_2.png")), (WIDTH, HEIGHT))
BGS = pygame.transform.scale(pygame.image.load(os.path.join("images/background-starter.png")), (WIDTH, HEIGHT))



class Laser:
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

range_ =  2
level = 0

class Ship:
    COOLDOWN = 35

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

    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)

            if laser.off_screen(HEIGHT):
               self.lasers.remove(laser)
            elif laser.collision(obj):
                explode_sound.play()
                obj.health -= range_
                self.lasers.remove(laser)


    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()


class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = Car1
        self.laser_img = GREEN_LASER
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        obj.health -= 100
                        explode_sound.play()
                        if laser in self.lasers:
                            self.lasers.remove(laser)
                        if obj.health <= 0:
                            objs.remove(obj)


    def draw(self, window):
        super().draw(window)
        self.healthbar(window)


    def healthbar(self, window):
        pygame.draw.rect(window, (255, 0, 0), (self.x, self.y - self.ship_img.get_height() + 50, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0, 255, 0), (self.x, self.y - self.ship_img.get_height() + 50, self.ship_img.get_width() * (self.health / self.max_health), 10))


class Enemy(Ship):
    COLOR_MAP = {
            "ufo": (UFO_SPACE_SHIP, RED_LASER),
            "enemy1": (ENEMYl1_SPACE_SHIP, RED_LASER),
            "enemy2": (ENEMYl2_SPACE_SHIP, RED_LASER)
    }


    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    def move(self, vel):
        self.y += vel

    def shoot(self):
        Hitsound.play()
        if self.cool_down_counter == 0:
            laser = Laser(self.x - 15, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(window, (255, 0, 0), (self.x, self.y - self.ship_img.get_height() + 50, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0, 255, 0), (self.x, self.y - self.ship_img.get_height() + 50, self.ship_img.get_width() * (self.health / self.max_health), 10))



def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None




def main():
    global level
    run = True
    FPS = 60
    lives = 10
    main_font = pygame.font.SysFont("comicsans", 40)
    sub_font = pygame.font.SysFont("comicsans", 32)
    lost_font = pygame.font.SysFont("comicsans", 60)
    big_font = pygame.font.SysFont("comicsans", 70)
    bigfont = pygame.font.SysFont("comicsans", 70)

    enemies = []
    wave_length = 2
    enemy_vel = 1

    player_vel = 2
    laser_vel = 4

    player = Player(300, 570)

    clock = pygame.time.Clock()

    lost = False
    lost_count = 0
    enemy1 = Enemy(random.randrange(50, WIDTH - 100), random.randrange(-1500, -100),
                   random.choice(["ufo", "enemy1", "enemy2"]))

    def redraw_window():
        global range_


        if level < 10:
            bg = BG
        if level >= 10 and level < 20:
            bg = BG2
        if level >= 20:
            bg = BG1


        WIN.blit(bg, (0, 0))
        # draw text
        lives_label = main_font.render(f"Lives: {lives}", 1, (255, 0, 0))
        level_label = main_font.render(f"Level: {level}", 1, (0, 255, 255))
        vel_label = sub_font.render(f"Speed: {player_vel}mph", 1, (0, 255, 255))
        bullet_label = sub_font.render(f"Bullet Speed: {laser_vel}miles/s", 1, (0, 255, 255))
        Reload_label = sub_font.render(f"Reload Speed: {Ship.COOLDOWN}/ms", 1, (0, 255, 255))
        Health__label = sub_font.render(f"Your-health: {player.health}%", 1, (0, 255, 0))
        range_l = sub_font.render(f"Damage: {range_}%", 1, (255, 0, 0))
        enemylife_l = sub_font.render(f"Enemy-health: {enemy1.health}%", 1, (255, 0, 0))


        WIN.blit(lives_label, (10, 10))
        WIN.blit(vel_label, (10, lives_label.get_height() + 10))
        WIN.blit(Reload_label, (10, vel_label.get_height() + lives_label.get_height() + 10))
        WIN.blit(range_l, (10, lives_label.get_height() + vel_label.get_height() + Reload_label.get_height() + 10))


        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))
        WIN.blit(bullet_label, (WIDTH - bullet_label.get_width() - 10, level_label.get_height() + 10))
        WIN.blit(Health__label, (WIDTH - Health__label.get_width() - 10, level_label.get_height() + bullet_label.get_height() + 10))
        WIN.blit(enemylife_l, (WIDTH - enemylife_l.get_width() - 10, level_label.get_height() + bullet_label.get_height() + Health__label.get_height() + 10))

        for enemy in enemies:
            enemy.draw(WIN)

        player.draw(WIN)

        if lost:
            Lose_sound.play()
            lost_label = lost_font.render("You Lost!", 1, (255, 0, 0))
            WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 350))
        if level == 10:
            boss_font = bigfont.render("BOSS FIGHT!", 1, (255, 0, 0))
            WIN.blit(boss_font, (WIDTH / 2 - boss_font.get_width() / 2, 350))



        pygame.display.update()

    while run:
        global range_
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


        # cars
        if level < 3:
            player.ship_img = Car1
        if level >= 3 and level < 5:
            player.ship_img = Car2
        if level >= 5 and level < 7:
            player.ship_img = Car3
        if level >= 7 and level < 10:
            player.ship_img = Car4
        if level >= 10 and level < 15:
            player.ship_img = Car5
        if level >= 15 and level < 20:
            player.ship_img = Car6
        if level >= 20:
            player.ship_img = spaceship



        if len(enemies) == 0:
            levelSound.play()
            level += 1
            range_ += 1
            if wave_length <= 10:
                wave_length += 1
            if player_vel <= 8:
                player_vel += 1
            laser_vel += 1
            if Ship.COOLDOWN >= 5:
                Ship.COOLDOWN -= 1


            # levels
            if level == 10:
                wave_length += 5
                player.health += 20
            if level == 11:
                wave_length -= 5

            if enemy_vel <= 3:
                if level % 20 == 0:
                    enemy_vel += 1
                    player.health += 25

            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, WIDTH - 100), random.randrange(-1500, -100), random.choice(["ufo", "enemy1", "enemy2"]))
                enemies.append(enemy)



        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player.x - player_vel > 0:
            player.x -= player_vel
        if keys[pygame.K_RIGHT] and player.x + player_vel + player.get_width() + 3 < WIDTH:
            player.x += player_vel
        if keys[pygame.K_UP] and player.y - player_vel > 560:
            player.y -= player_vel
        if keys[pygame.K_DOWN] and player.y + player_vel + player.get_height() < HEIGHT:
            player.y += player_vel
        if keys[pygame.K_SPACE]:
            player.shoot()

        for enemy in enemies:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)

            if random.randrange(0, 4*60) == 1:
                enemy.shoot()



            if collide(enemy, player):
                player.health -= 10
                explode_sound.play()
                enemies.remove(enemy)

            elif enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)

        player.move_lasers(-laser_vel, enemies)

def main_menu():
    title_font = pygame.font.SysFont("comicsans", 80)
    run = True
    while run:
        WIN.blit(BG, (0, 0))
        title_label = title_font.render("Press any key to begin!!!", 1, (255, 255, 255))
        WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 350))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                main()
    pygame.quit()

main_menu()


