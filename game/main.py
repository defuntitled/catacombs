'''Hey, this is stane game *_* '''
import pygame
from math import tan, sqrt, radians, cos, floor, sin
import os
import numpy

pygame.init()
main_surface = pygame.display.set_mode((768, 512))
main_surface.fill((255, 255, 255))


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    image = pygame.image.load(fullname).convert()
    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


WALL = [load_image(f'peace{i}.png') for i in range(64)]
WALL = numpy.array(WALL)
# MOB = [[load_image(f'zilibobkaframe_{i}.png', -1) for i in range(64)],
#       [load_image(f'zilibobkafire_{i}.png', -1) for i in range(64)]]
MOB = [[load_image(f'zilibobkaframe_{i}.png', -1) for i in range(64)],
       [load_image(f'zilibobkafire_{i}.png', -1) for i in range(64)]]
MOB = numpy.array(MOB)


class Creature():
    '''сначала я хотел реализовывать через этот класс еще и врагов, но что-то пошло не так, и теперь этот класс не нужен,
    но исправлять слишком много'''

    def __init__(self, x, y, pov, area):
        self.x = x
        self.y = y
        self.pov = pov
        self.habitant = area
        self.view_up = None
        self.view_right = None
        if 0 <= self.pov <= 180:
            self.view_up = True
        else:
            self.view_up = False
        if 0 <= self.pov <= 90 or 270 <= self.pov < 360:
            self.view_right = True
        else:
            self.view_right = False


class Hand(pygame.sprite.Sprite):
    def __init__(self, group):
        super().__init__(group)
        self.hands = [load_image('kultyap.png', -1), load_image('crazykultyap.png', -1)]
        self.image = self.hands[0]
        self.rect = self.image.get_rect()
        self.rect.x = 170
        self.rect.y = 240

    def update(self, war_mode):
        if war_mode:
            self.image = self.hands[1]
        else:
            self.image = self.hands[0]


class Player(Creature):
    def __init__(self, x, y, pov, area, hand):
        super().__init__(x, y, pov, area)
        self.walk_speed_forward = 10
        self.walk_speed_back = 10
        self.walk_speed = 10
        self.rotate_speed = 4.111111
        self.fov = 60
        self.hand = hand
        self.hp = 100

    def rotate_left(self):
        if self.pov + self.rotate_speed >= 360:
            self.pov = (self.pov + self.rotate_speed) % 360
        else:
            self.pov += self.rotate_speed
        self.pov_cheker()

    def rotate_right(self):
        if self.pov - self.rotate_speed < 0:
            self.pov = (self.pov - self.rotate_speed) % 360
        else:
            self.pov -= self.rotate_speed
        self.pov_cheker()

    def walk_forward(self):
        sinus = sin(radians(self.pov))
        cosinus = cos(radians(self.pov))
        if self.habitant.map[int((self.y - sinus * self.walk_speed * 2) // 64)][int(
                (self.x + cosinus * self.walk_speed * 2) // 64)]:
            self.walk_speed_forward = 0
        else:
            if self.walk_speed_forward == 0:
                self.walk_speed_forward = 10
            self.x += cosinus * self.walk_speed_forward
            self.y -= sinus * self.walk_speed_forward

    def walk_back(self):
        sinus = sin(radians(self.pov))
        cosinus = cos(radians(self.pov))
        if self.habitant.map[int((self.y + sinus * self.walk_speed * 2) // 64)][int(
                (self.x - cosinus * self.walk_speed * 2) // 64)]:
            self.walk_speed_back = 0
        else:
            if self.walk_speed_back == 0:
                self.walk_speed_back = 10
        self.x -= cos(radians(self.pov)) * self.walk_speed_back
        self.y += sin(radians(self.pov)) * self.walk_speed_back

    def pov_cheker(self):
        if 0 <= self.pov <= 180:
            self.view_up = True
        else:
            self.view_up = False
        if 0 <= self.pov <= 90 or 270 <= self.pov < 360:
            self.view_right = True
        else:
            self.view_right = False

    def piw(self):
        pass

    def damage(self):
        self.hp -= 0.5
        # gameover(False)


class Mob(pygame.sprite.Sprite):
    def __init__(self, group, state, pic_index, x, y, high):
        super().__init__(group)
        global MOB
        if state:
            self.image = MOB[0][pic_index]
        else:
            self.image = MOB[1][pic_index]
        self.image = pygame.transform.scale(self.image, (1, high))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Wall(pygame.sprite.Sprite):
    def __init__(self, group, peace_index, high, y, x):
        global WALL
        super().__init__(group)
        self.image = WALL[peace_index]
        self.image = pygame.transform.scale(self.image, (1, high))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Area():
    def __init__(self, screen):
        self.map = numpy.array([[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                                [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 1],
                                [1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                                [1, 0, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                                [1, 0, 0, 1, 0, 1, 3, 0, 0, 0, 0, 0, 0, 0, 1],
                                [1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1],
                                [1, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 1],
                                [1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1],
                                [1, 3, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1, 1, 1],
                                [1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 0, 0, 0, 3, 1],
                                [1, 0, 3, 0, 0, 0, 0, 1, 0, 1, 0, 1, 1, 1, 1],
                                [1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1],
                                [1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 1],
                                [1, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 1],
                                [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]])
        self.player = None
        self.screen = screen
        self.sprite_high = None
        self.CAM_TO_PP = None
        self.mob_sprite_group = pygame.sprite.Group()

    def add_creature(self, creature):
        self.player = creature

    def show(self):
        wall_group = pygame.sprite.Group()
        self.mob_sprite_group = pygame.sprite.Group()
        coords_for_texturing = []
        PP = (768, 512)  # projection plane
        self.CAM_TO_PP = PP[0] / 2 / tan(
            radians(self.player.fov / 2))  # distance between ''camera'' and projection plane
        ANGLE_BETWEEN_RAYS = self.player.fov / PP[0]
        angle_bet = -30
        angle = self.player.pov + self.player.fov / 2
        draw_mob = False
        self.angle_cheker(angle)
        for i in range(PP[0]):

            mob_view_system = [[False], [False]]
            if self.player.view_up:
                intesection_yy = self.player.y // 64 * 64 - 1
                yy_next = -64
            else:
                intesection_yy = self.player.y // 64 * 64 + 64
                yy_next = 64
            if self.player.view_right:
                intesection_xx = self.player.x // 64 * 64 + 64
                xx_next = 64
            else:
                intesection_xx = self.player.x // 64 * 64 - 1
                xx_next = -64
            cosinus, tangens = cos(radians(angle)), tan(radians(angle))
            intesection_yx = self.player.x + (self.player.y - intesection_yy) / tangens
            if self.player.view_right and self.player.view_up:
                yx_next = 64 / tangens
                xy_next = 0 - 64 * tangens
            elif self.player.view_right and not self.player.view_up:
                yx_next = 0 - 64 / tangens
                xy_next = 0 - 64 * tangens
            elif not self.player.view_right and self.player.view_up:
                yx_next = 64 / tangens
                xy_next = 64 * tangens
            elif not self.player.view_up and not self.player.view_right:
                yx_next = 0 - 64 / tangens
                xy_next = 64 * tangens
            intesection_xy = self.player.y + (self.player.x - intesection_xx) * tangens
            intersected = False
            distance = []
            while not intersected:
                try:
                    x = int(intesection_yx / 64)
                    y = int(intesection_yy / 64)
                    # print(x, y)
                    if self.map[y][x] == 1:
                        distance.append(
                            sqrt((self.player.x - intesection_yx) ** 2 + (self.player.y - intesection_yy) ** 2))
                        coords_for_texturing.append(intesection_yx)
                        intersected = True
                    else:
                        intesection_yx += yx_next
                        intesection_yy += yy_next
                    if self.map[y][x] == 3:
                        mob_view_system[0][0] = True
                        mob_view_system[0].append(intesection_yx)
                        mob_view_system[0].append(intesection_yy)
                except IndexError:
                    break
            intersected = False
            while not intersected:
                try:
                    x = int(intesection_xx / 64)
                    y = int(intesection_xy / 64)
                    # print(x, y)
                    if self.map[y][x] == 1:
                        distance.append(
                            sqrt((self.player.x - intesection_xx) ** 2 + (self.player.y - intesection_xy) ** 2))
                        coords_for_texturing.append(intesection_xy)
                        intersected = True
                    else:
                        intesection_xx += xx_next
                        intesection_xy += xy_next
                    if self.map[y][x] == 3:
                        mob_view_system[1][0] = True
                        mob_view_system[1].append(intesection_xx)
                        mob_view_system[1].append(intesection_xy)
                except IndexError:
                    break
            if len(distance) == 2 and distance[0] < distance[1]:
                distance[0] *= cos(radians(angle_bet))
                high = int(64 / distance[0] * self.CAM_TO_PP)
                pece_index = int(coords_for_texturing[0] % 64)
                if mob_view_system[0][0] and not draw_mob:
                    self.find_mob_sprite(mob_view_system[0][1], mob_view_system[0][0], True, i, 0)
                    draw_mob = True
                elif mob_view_system[0][0] and draw_mob:
                    self.find_mob_sprite(mob_view_system[0][1], mob_view_system[0][2], False, i, 0)
                elif not mob_view_system[0][0]:
                    draw_mob = False
                    # self.mob_sprite_group = pygame.sprite.Group()
            elif len(distance) == 2 and distance[0] > distance[1]:
                distance[1] *= cos(radians(angle_bet))
                high = int(64 / distance[1] * self.CAM_TO_PP)
                pece_index = int(coords_for_texturing[1] % 64)
                if mob_view_system[1][0] and not draw_mob:
                    self.find_mob_sprite(mob_view_system[1][1], mob_view_system[1][2], True, i, 1)
                    draw_mob = True
                elif mob_view_system[1][0] and draw_mob:
                    self.find_mob_sprite(mob_view_system[1][1], mob_view_system[1][2], False, i, 1)
                elif not mob_view_system[1][0]:
                    draw_mob = False
                    # self.mob_sprite_group = pygame.sprite.Group()
            elif not intersected:
                distance[0] *= cos(radians(angle_bet))
                high = int(64 / distance[0] * self.CAM_TO_PP)
                pece_index = int(coords_for_texturing[0] % 64)
                if mob_view_system[0][0] and not draw_mob:
                    self.find_mob_sprite(mob_view_system[0][1], mob_view_system[0][0], True, i, 0)
                    draw_mob = True
                elif mob_view_system[0][0] and draw_mob:
                    self.find_mob_sprite(mob_view_system[0][1], mob_view_system[0][2], False, i, 0)
                elif not mob_view_system[0][0]:
                    draw_mob = False
                    # self.mob_sprite_group = pygame.sprite.Group()
            elif intersected:
                distance[0] *= cos(radians(angle_bet))
                high = int(64 / distance[0] * self.CAM_TO_PP)
                pece_index = int(coords_for_texturing[0] % 64)
                if mob_view_system[1][0] and not draw_mob:
                    self.find_mob_sprite(mob_view_system[1][1], mob_view_system[1][2], True, i, 1)
                    draw_mob = True
                elif mob_view_system[1][0] and draw_mob:
                    self.find_mob_sprite(mob_view_system[1][1], mob_view_system[1][2], False, i, 1)
                elif not mob_view_system[1][0]:
                    draw_mob = False

                    # self.mob_sprite_group = pygame.sprite.Group()
            if high % 2 != 0:
                high -= 1

            Wall(wall_group, pece_index, high, int(PP[1] / 2 - high / 2), i)

            angle -= ANGLE_BETWEEN_RAYS
            self.angle_cheker(angle)
            angle_bet += ANGLE_BETWEEN_RAYS
            coords_for_texturing = []
        wall_group.draw(self.screen)
        # self.mob_sprite_group.draw(self.screen)

    def find_mob_sprite(self, x, y, find_high, display_x, ray_id):
        dist = sqrt((self.player.x - x) ** 2 + (self.player.y - y) ** 2)
        if find_high:
            self.sprite_high = 64 / dist * self.CAM_TO_PP
        display_y = int(512 / 2 - self.sprite_high / 2)
        if ray_id == 0:
            pic_id = int(x % 64)
        else:
            pic_id = int(y % 64)
        if dist >= 256:
            Mob(self.mob_sprite_group, True, pic_id, display_x, display_y, int(self.sprite_high))

        else:
            Mob(self.mob_sprite_group, False, pic_id, display_x, display_y, int(self.sprite_high))

    def draw_mob(self):
        self.mob_sprite_group.draw(self.screen)

    def angle_cheker(self, angle):
        if angle >= 360:
            angle -= 360
        if angle < 0:
            angle += 360
        if 0 <= angle <= 180:
            self.player.view_up = True
        else:
            self.player.view_up = False
        if 0 <= angle <= 90 or 270 <= angle < 360:
            self.player.view_right = True
        else:
            self.player.view_right = False


running = True
FPS_CONTROL = 30
pygame.time.set_timer(FPS_CONTROL, 50)

world = Area(main_surface)
hand = pygame.sprite.Group()
Hand(hand)
player = Player(282.3857446442757, 83.0443589265848, 248.52232499999974, world, hand)
world.add_creature(player)
print(player.view_right, player.view_up)

# player.pov +=89
world.show()
pygame.display.flip()
forward, back, left, right = False, False, False, False
while running:

    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_UP]:
                forward = True
            if keys[pygame.K_DOWN]:
                back = True
            if keys[pygame.K_LEFT]:
                left = True
            if keys[pygame.K_RIGHT]:
                right = True
            if keys[pygame.K_a]:
                hand.update(True)
        if event.type == pygame.KEYUP:
            keys = pygame.key.get_pressed()
            if not keys[pygame.K_UP]:
                forward = False
            if not keys[pygame.K_DOWN]:
                back = False
            if not keys[pygame.K_LEFT]:
                left = False
            if not keys[pygame.K_RIGHT]:
                right = False
            if not keys[pygame.K_a]:
                hand.update(False)
            print(player.x, player.y, player.pov)
        if event.type == pygame.QUIT:
            running = False
        if event.type == FPS_CONTROL:
            if forward:
                player.walk_forward()
            if back:
                player.walk_back()
            if right:
                player.rotate_right()
            if left:
                player.rotate_left()
            main_surface.fill((50, 50, 50))
            world.show()
            world.draw_mob()
            hand.draw(main_surface)
    pygame.display.flip()
