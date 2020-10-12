import pygame
import os
import random
import time

pygame.font.init()
pygame.mixer.init()

pygame.mixer.music.load(os.path.join("assets" , "sounds" , "bcg.wav"))
pygame.mixer.music.play(-1)


WIDTH , HEIGHT = 850 , 700

WIN = pygame.display.set_mode((WIDTH , HEIGHT))
monitor_size = [pygame.display.Info().current_w, pygame.display.Info().current_h]

pygame.display.set_caption("Space Shooter")

# opponment ships
RED_SHIP = pygame.image.load(os.path.join("assets" , "pixel_ship_red_small.png"))
BLUE_SHIP = pygame.image.load(os.path.join("assets" , "pixel_ship_blue_small.png"))
GREEN_SHIP = pygame.image.load(os.path.join("assets" , "pixel_ship_green_small.png"))

MID_SHIP = pygame.transform.scale(pygame.image.load(
    os.path.join("assets" , "pixel_ship_green_small.png"))
    , (GREEN_SHIP.get_width()*2 , GREEN_SHIP.get_height()*2))

# player ship
YELLOW_SHIP = pygame.image.load(os.path.join("assets" , "pixel_ship_yellow.png"))

# opponment bullets
RED_LASER = pygame.image.load(os.path.join("assets" , "pixel_laser_red.png"))
BLUE_LASER = pygame.image.load(os.path.join("assets" , "pixel_laser_blue.png"))
GREEN_LASER = pygame.image.load(os.path.join("assets" , "pixel_laser_green.png"))

MID_LASER = pygame.transform.scale(pygame.image.load(os.path.join("assets" , "pixel_laser_green.png")), (GREEN_LASER.get_width()*2 , GREEN_LASER.get_height()*2))

# player buller
YELLOW_LASER = pygame.image.load(os.path.join("assets" , "pixel_laser_yellow.png"))

# background
BG = pygame.transform.scale(pygame.image.load(
    os.path.join("assets" , "background-black.png"))
     , (WIDTH , HEIGHT))


SHOOT_EFFECT = pygame.mixer.Sound(os.path.join("assets" , "sounds" , "shoot.wav"))
ENEMY_DIE_EFFECT = pygame.mixer.Sound(os.path.join("assets" , "sounds" , "invaderkilled.wav"))

def collide(obj1 , obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask , (offset_x,offset_y)) != None

class Laser:
    def __init__(self, x , y ,img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self , window):
        window.blit(self.img, (self.x , self.y))

    def move(self , vel):
        self.y += vel

    def offscreen(self , height):
        return not(self.x <= height and self.y >= 0)

    def collision(self,obj):
        return collide(self , obj)


class Ship:
    DELAY = 30
    def __init__(self, x , y ,health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_image = None
        self.laser_image = None
        self.lasers = []
        self.delay = 0
        self.i = 0


    def draw(self , window):
        window.blit(self.ship_image, (self.x , self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self , vel , obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.offscreen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                if self.ship_image == MID_SHIP:
                    obj.health -= 8
                else:
                    obj.health -= 4
                self.lasers.remove(laser)


    def get_width(self):
        return self.ship_image.get_width()
    def cooldown(self):
        if self.delay >= self.DELAY:
            self.delay = 0
        elif self.delay > 0:
            self.delay += 1


    def get_height(self):
        return self.ship_image.get_height()

    def shoot(self):
        if self.delay == 0:
            laser = Laser(self.x, self.y, self.laser_image)
            self.lasers.append(laser)
            self.delay = 1




class Player(Ship):
    def __init__(self, x , y ,health=100):
        super().__init__(x , y ,health)
        self.ship_image = YELLOW_SHIP
        self.laser_image = YELLOW_LASER
        self.mask = pygame.mask.from_surface(self.ship_image)
        self.max_health = health

    def move_lasers(self , vel , objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.offscreen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        if obj.ship_image == MID_SHIP :
                            obj.i+=1
                            print(obj.i)
                            if obj.i == 5:
                                objs.remove(obj)
                                ENEMY_DIE_EFFECT.play()

                            if laser in self.lasers:
                                self.lasers.remove(laser)

                        else:
                            objs.remove(obj)
                            ENEMY_DIE_EFFECT.play()
                            if laser in self.lasers:
                                self.lasers.remove(laser)

    def draw(self , window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self , window):
        pygame.draw.rect(window , (255 , 0 , 0 ) ,(self.x ,self.y + self.ship_image.get_height() + 10 ,self.ship_image.get_width() , 10))
        pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.ship_image.get_height() + 10, self.ship_image.get_width() - (self.max_health - self.health), 10))




class Enemy(Ship):
    COLOR_MAP = {
                "red":(RED_SHIP,RED_LASER),
                "green":(GREEN_SHIP,GREEN_LASER),
                "blue":(BLUE_SHIP,BLUE_LASER),
                "mid":(MID_SHIP , MID_LASER)
                }

    def __init__(self, x , y , color ,health=100):
        super().__init__(x , y ,health=100)
        self.ship_image , self.laser_image = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_image)
        self.i = 0


    def move(self , vel):
        self.y += vel

    def shoot(self):
        if self.delay == 0:
            laser = Laser(self.x-20, self.y, self.laser_image)
            self.lasers.append(laser)
            self.delay = 1


def main():
    run = True
    FPS = 60

    level = 0
    lives = 5
    player_vel = 5
    enemy_vel = 1
    laser_vel = 4
    wave_length = 5
    enemies = []

    lost = False
    lost_count = 0

    player = Player(300 , 580)

    main_font = pygame.font.SysFont('comicsans', 50)
    lost_font = pygame.font.SysFont('comicsans', 70)
    clock = pygame.time.Clock()

    def redraw_win():
        WIN.blit(BG , (0,0))

        lives_label = main_font.render(f"Lives : {lives}", 1, (255,255,255))
        level_label = main_font.render(f"Level : {level}", 1, (255,255,255))

        WIN.blit(lives_label , (10,10))
        WIN.blit(level_label , (WIDTH - lives_label.get_width()-10 , 10))

        if lost:
            lost_label = lost_font.render("You lost!!!!!!", 1, (255,255,255))
            WIN.blit(lost_label , (WIDTH//2 - lost_label.get_width()//2, 350))

        for enemy in enemies:
            enemy.draw(WIN)

        player.draw(WIN)

        pygame.display.update()

    while run:
        clock.tick(FPS)
        redraw_win()

        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1

        if lost:
            # ENEMY_DIE_EFFECT.play()
            if lost_count > FPS*3:
                run = False
                break
            else:
                continue

        if len(enemies) == 0 :
            enemy_types = ['red','blue','green']
            level += 1
            if level < 3:
                wave_length += 4
            else:
                wave_length += 2
            if level == 3:
                enemy_types.append('mid')

            for i in range(wave_length):
                enemy = Enemy(random.randrange(50 , WIDTH - 200 )
                 , random.randrange(-1500 , -100) ,
                 random.choice(enemy_types))
                enemies.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        keys = pygame.key.get_pressed()

        if keys[pygame.K_a] and player.x - player_vel > 0:
            player.x -= player_vel
        if keys[pygame.K_d] and player.x + player_vel + player.get_width() < WIDTH :
            player.x += player_vel
        if keys[pygame.K_w] and player.y - player_vel > 0:
            player.y -= player_vel
        if keys[pygame.K_s] and player.y + player_vel + player.get_height()+20 <  HEIGHT:
            player.y += player_vel
        if keys[pygame.K_SPACE]:
            player.shoot()
            SHOOT_EFFECT.play()

        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)

            if random.randrange(0 , 3* FPS) == 1:
                enemy.shoot()
            if collide(enemy, player):
                if enemy.ship_image == MID_SHIP:
                    player.health -= 10
                else:
                    player.health -= 5

                enemies.remove(enemy)

            elif enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)

        player.move_lasers(-laser_vel, enemies)
    if lost == False:
        pygame.quit()

def main_menu():
    title_font = pygame.font.SysFont("comicsans", 70)
    run = True
    while run:
        WIN.blit(BG, (0,0))
        title_label = title_font.render("Press the mouse to begin...", 1, (255,255,255))
        WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 350))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
    pygame.quit()


main_menu()

