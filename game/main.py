'''Hey, this is the game: the game *_* '''
import pygame
from math import tan, sqrt, radians, cos, floor, sin
import os


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
    def __init__(self, x, y, pov):
        self.x = x
        self.y = y
        self.pov = pov
        self.view_up = None
        self.view_right = None
        if 0 <= pov <= 180:
            self.view_up = True
        else:
            self.view_up = False
        if 0 <= pov <= 90 or 270 <= self.pov < 360:
            self.view_right = True
        else:
            self.view_right = False


class Player(Creature):
    def __init__(self, x, y, pov):
        super().__init__(x, y, pov)
        self.walk_speed = 10
        self.rotate_speed = 2.111111
        self.fov = 60

    def rotate_left(self):
        if self.pov + self.rotate_speed >= 360:
            self.pov = (self.pov + self.rotate_speed) % 360
        else:
            self.pov += self.rotate_speed

    def rotate_right(self):
        if self.pov - self.rotate_speed < 0:
            self.pov = (self.pov - self.rotate_speed) % 360
        else:
            self.pov -= self.rotate_speed

    def walk_forward(self):
        self.x += cos(radians(self.pov)) * self.walk_speed
        self.y -= sin(radians(self.pov)) * self.walk_speed

    def walk_back(self):
        self.x -= cos(radians(self.pov)) * self.walk_speed
        self.y += sin(radians(self.pov)) * self.walk_speed


class Wall(pygame.sprite.Sprite):
    def __init__(self, group):
        super().__init__(group)


class Area():
    def __init__(self, player, screen):
        self.map = [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
                    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
                    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
                    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
                    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
                    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
                    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
                    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
                    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]]
        self.player = player
        self.screen = screen

    def show(self):
        PP = (768, 512)
        CAM_TO_PP = PP[0] / 2 / tan(radians(self.player.fov / 2))
        ANGLE_BETWEEN_RAYS = self.player.fov / PP[0]
        angle_bet = -30
        angle = self.player.pov - self.player.fov / 2
        for i in range(PP[0]):
            if self.player.view_up:
                intesection_yy = floor(self.player.y / 64) * 64 - 1
                yy_next = -64
            else:
                intesection_yy = floor(self.player.y / 64) * 64 + 64
                yy_next = 64
            if self.player.view_right:
                intesection_xx = floor(self.player.x / 64) * 64 + 64
                xx_next = 64
            else:
                intesection_xx = floor(self.player.x / 64) * 64 - 1
                xx_next = -64
            cosinus, tangens = cos(radians(angle)), tan(radians(angle))
            intesection_yx = self.player.x + (self.player.y - intesection_yy) / tangens
            yx_next = 64 / tangens
            intesection_xy = self.player.y + (self.player.x - intesection_xx) * tangens
            xy_next = 64 * tangens
            intersected = False
            distance = []
            while not intersected:
                try:
                    x = int(intesection_yx / 64)
                    y = int(intesection_yy / 64)
                    #print(x, y)
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
            pygame.draw.line(self.screen, (0, 0, 0), (PP[0] - i, int(PP[1] / 2 - high / 2)), (PP[0]-i,  int(PP[1] / 2 - high / 2)+high))

            angle += ANGLE_BETWEEN_RAYS
            angle_bet += ANGLE_BETWEEN_RAYS


pygame.init()

wall_surface = pygame.display.set_mode((768, 512))
wall_surface.fill((255, 255, 255))
running = True
FPS_CONTROL = 30
pygame.time.set_timer(FPS_CONTROL, 50)
player = Player(96, 416, 46)
print(player.view_right, player.view_up)
world = Area(player, wall_surface)
world.show()
forward, back, left, right = False, False, False, False
while running:

    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                forward = True
            elif event.key == pygame.K_DOWN:
                back = True
            elif event.key == pygame.K_LEFT:
                left = True
            elif event.key == pygame.K_RIGHT:
                right = True
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_UP:
                forward = False
            elif event.key == pygame.K_DOWN:
                back = False
            elif event.key == pygame.K_LEFT:
                left = False
            elif event.key == pygame.K_RIGHT:
                right = False
            print(player.pov, player.x, player.y)
        if event.type == pygame.QUIT:
            running = False
        if event.type == FPS_CONTROL:
            if forward:
                player.walk_forward()
            elif back:
                player.walk_back()
            elif right:
                player.rotate_right()
            elif left:
                player.rotate_left()
            wall_surface.fill((255, 255, 255))
            world.show()
    pygame.display.flip()
