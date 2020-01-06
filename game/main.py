'''Hey, this is the game: the game *_* '''
import pygame
from math import tan, sqrt, radians, cos, floor, sin
import os
import numpy


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


class Creature():
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


class Player(Creature):
    def __init__(self, x, y, pov, area):
        super().__init__(x, y, pov, area)
        self.walk_speed_forward = 10
        self.walk_speed_back = 10
        self.walk_speed = 10
        self.rotate_speed = 4.111111
        self.fov = 60

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


class Wall(pygame.sprite.Sprite):
    def __init__(self, group):
        super().__init__(group)


class Area():
    def __init__(self, screen):
        self.map = numpy.array([[1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                                [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
                                [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
                                [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
                                [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
                                [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
                                [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
                                [1, 0, 0, 0, 0, 0, 1, 0, 0, 1],
                                [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
                                [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]])
        self.player = None
        self.screen = screen

    def add_creature(self, creature):
        self.player = creature

    def show(self):
        PP = (768, 512)
        CAM_TO_PP = PP[0] / 2 / tan(radians(self.player.fov / 2))
        ANGLE_BETWEEN_RAYS = self.player.fov / PP[0]
        angle_bet = -30
        angle = self.player.pov + self.player.fov / 2
        c = 0
        self.angle_cheker(angle)
        for i in range(PP[0]):
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
                        intersected = True
                    else:
                        intesection_yx += yx_next
                        intesection_yy += yy_next
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
                        intersected = True
                    else:
                        intesection_xx += xx_next
                        intesection_xy += xy_next
                except IndexError:
                    break
            distance = min(distance) * cos(radians(angle_bet))
            high = int(64 / distance * CAM_TO_PP)
            if high % 2 != 0:
                high -= 1
            pygame.draw.line(self.screen, (0, 0, 0), (i, int(PP[1] / 2 - high / 2)),
                             (i, int(PP[1] / 2 - high / 2) + high))
            angle -= ANGLE_BETWEEN_RAYS
            self.angle_cheker(angle)
            angle_bet += ANGLE_BETWEEN_RAYS

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


pygame.init()

wall_surface = pygame.display.set_mode((768, 512))
wall_surface.fill((255, 255, 255))
running = True
FPS_CONTROL = 30
pygame.time.set_timer(FPS_CONTROL, 50)
world = Area(wall_surface)
player = Player(128, 128, 0.0000001, world)
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
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                forward = True
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                back = True
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                left = True
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                right = True
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
            wall_surface.fill((255, 255, 255))
            world.show()
    pygame.display.flip()
