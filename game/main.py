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
        if 0 <= pov <= 90 and 270 <= self.pov < 360:
            self.view_right = True
        else:
            self.view_right = False


class Player(Creature):
    def __init__(self, x, y, pov):
        super().__init__(x, y, pov)
        self.walk_speed = 19
        self.rotate_speed = 60
        self.fov = 60

    def rotate_left(self):
        if self.pov + self.rotate_speed >= 360:
            self.pov = (self.pov+self.rotate_speed)%360
        else:
            self.pov += self.rotate_speed

    def rotate_right(self):
        if self.pov - self.rotate_speed < 0:
            self.pov = (self.pov-self.rotate_speed)%360
        else:
            self.pov -= self.rotate_speed

    def walk_forward(self):
        self.x += cos(radians(self.pov)) * self.walk_speed
        self.y += sin(radians(self.pov)) * self.walk_speed

    def walk_back(self):
        self.x -= cos(radians(self.pov)) * self.walk_speed
        self.y -= sin(radians(self.pov)) * self.walk_speed


class Wall(pygame.sprite.Sprite):
    def __init__(self, group):
        super().__init__(group)


class Area():
    def __init__(self, player, screen):
        self.map = [[('w', None), ('w', None), ('w', None), ('w', None), ('w', None), ('w', None)],
                    [('w', None), ('a', None), ('a', None), ('a', None), ('a', None), ('w', None)],
                    [('w', None), ('a', None), ('a', None), ('a', None), ('a', None), ('w', None)],
                    [('w', None), ('a', None), ('a', None), ('a', None), ('a', None), ('w', None)],
                    [('w', None), ('a', None), ('a', None), ('a', None), ('a', None), ('w', None)],
                    [('w', None), ('w', None), ('w', None), ('w', None), ('w', None), ('w', None)]]
        self.player = player
        self.screen = screen

    def show(self):
        PP = (768, 512)
        CAM_TO_PP = PP[1] / 2 / tan(radians(self.player.fov / 2))

        angle_bet = -30

        if self.player.view_right:
            angle = self.player.pov + self.player.fov / 2
        else:
            angle = self.player.pov - self.player.fov / 2
        # заготовки для хор

        for i in range(PP[0]):
            if self.player.view_up:
                intersection_y = floor(self.player.y / 64) * 64 - 1
                y_distance = -64
            else:
                intersection_y = floor(self.player.y / 64) * 64 + 64
                y_distance = 64
            # заготовки для верт
            if self.player.view_right:
                intersection_xX = floor(self.player.x / 64) * 64 + 64
                x_xdistance = 64
            else:
                intersection_xX = floor(self.player.x / 64) * 64 - 1
                x_xdistance = -64
            distance = []
            intersection_x = self.player.x + (self.player.y - intersection_y) / tan(radians(angle))
            xDistance = 64 / tan(radians(angle))
            intersected = False
            # cast by horisontal
            while not intersected:
                try:
                    x = int(intersection_x / 64)
                    y = int(intersection_y / 64)
                    # print(x, y)
                    if self.map[y][x][0] == 'w':
                        distance.append(
                            sqrt((self.player.x - intersection_x) ** 2 + (self.player.y - intersection_y) ** 2))
                        intersected = True
                    else:
                        intersection_x += xDistance
                        intersection_y += y_distance
                except IndexError:
                    break
            # cast by vertical
            intersected = False
            intersection_xY = self.player.y + (self.player.x - intersection_xX) * tan(radians(angle))
            y_xdistance = 64 * tan(radians(angle))
            while not intersected:
                try:
                    x = int(intersection_xX / 64)
                    y = int(intersection_xY / 64)
                    # print(x, y)
                    if self.map[y][x][0] == 'w':
                        distance.append(
                            sqrt((self.player.x - intersection_xX) ** 2 + (self.player.y - intersection_xY) ** 2))

                        intersected = True
                    else:
                        intersection_xX += x_xdistance
                        intersection_xY += y_xdistance
                except IndexError:
                    break
            # print(distance)

            distance = int(min(distance)) * cos(radians(angle_bet))

            # рисовашки
            high = int(64 / distance * CAM_TO_PP)
            # print(distance)
            # print(high, distance, angle)
            pygame.draw.rect(self.screen, (0, 0, 0), (i, int(PP[1] / 2 - high / 2), 1, high))
            if self.player.view_right:
                angle -= self.player.fov / PP[1]
            else:
                angle += self.player.fov / PP[1]
            angle_bet += self.player.fov / PP[1]


pygame.init()

wall_surface = pygame.display.set_mode((768, 512))
wall_surface.fill((255, 255, 255))
running = True
FPS_CONTROL = 30
pygame.time.set_timer(FPS_CONTROL, 100)
player = Player(192, 300, 145)
print(player.view_right,player.view_up)
world = Area(player, wall_surface)
while running:
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                player.walk_forward()
            elif event.key == pygame.K_DOWN:
                player.walk_back()
            elif event.key == pygame.K_LEFT:
                player.rotate_left()
            elif event.key == pygame.K_RIGHT:
                player.rotate_right()
            print(player.pov)
        if event.type == pygame.QUIT:
            running = False
        if event.type == FPS_CONTROL:
            world.show()
    pygame.display.flip()
