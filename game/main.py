'''Hey, this is Catacombs: the game *_* '''
import pygame
import math


class Creature():
    def __init__(self, x, y, pov):
        self.x = x
        self.y = y
        self.pov = pov
        self.viewUp = None
        self.viewRight = None
        if 0 <= pov % 360 < 180:
            self.viewUp = True
        else:
            self.viewUp = False
        if 0 <= pov % 360 < 90 and 270 <= pov % 360 < 360:
            self.viewRight = True
        else:
            self.viewRight = False


class Player(Creature):
    def __init__(self, x, y, pov):
        super().__init__(x, y, pov)
        self.walkSpeed = 32 / 60
        self.rotateSpeed = 0.5

    def rotate_left(self):
        if self.pov + self.rotateSpeed == 360:
            self.pov = 0
        else:
            self.pov += self.rotateSpeed

    def rotate_right(self):
        if self.pov - self.rotateSpeed < 0:
            self.pov = 359.5
        else:
            self.pov -= self.rotateSpeed

    def walk_forward(self):
        self.x += math.cos(math.radians(self.pov)) * self.walkSpeed
        self.y += math.sin(math.radians(self.pov)) * self.walkSpeed

    def walk_back(self):
        self.x -= math.cos(math.radians(self.pov)) * self.walkSpeed
        self.y -= math.sin(math.radians(self.pov)) * self.walkSpeed


class Area():
    def __init__(self):
        self.map = [[]]


pygame.init()
wall_surface = pygame.display.set_mode((768, 576))
running = True
fps_metrics = pygame.time.Clock()
while running:
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                pass
            elif event.key == pygame.K_DOWN:
                pass
            elif event.key == pygame.K_LEFT:
                pass
            elif event.key == pygame.K_RIGHT:
                pass

        if event.type == pygame.QUIT:
            running = False
    pygame.display.flip()
    fps_metrics.tick(60)
