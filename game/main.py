'''Hey, this is stane game *_*'''
import pygame
from math import tan, sqrt, radians, cos, floor, sin
import os
import numpy
import sys

pygame.init()
main_surface = pygame.display.set_mode((768, 512))
main_surface.fill((255, 255, 255))
pygame.display.set_caption('Stane')
game_result = None
pause = False


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


# загрузка звуков
load = pygame.mixer.Sound(os.path.join('data', 'load.wav'))
piw = pygame.mixer.Sound(os.path.join('data', 'piw.wav'))
mod_fire = pygame.mixer.Sound(os.path.join('data', 'fire.wav'))
# загрузка спрайтов мобов и стены
WALL = [load_image(f'peace{i}.png') for i in range(64)]
WALL = numpy.array(WALL)
MOB = [[load_image(f'zilibobkaframe_{i}.png', -1) for i in range(64)],
       [load_image(f'zilibobkafire_{i}.png', -1) for i in range(64)]]
MOB = numpy.array(MOB)
BACKGROUND = load_image('background.jpg')


def gameover(reason):
    pygame.time.delay(2500)
    global main_surface, game_result
    main_surface.fill((25, 25, 25))
    main_surface.blit(BACKGROUND, (0, 0))
    message_font = pygame.font.Font(None, 38)
    control_font = pygame.font.Font(None, 36)
    if reason:
        pygame.mixer.music.load(os.path.join('data', 'win.mp3'))
        pygame.mixer.music.play()
        if 100 >= game_result >= 90:
            rendered = message_font.render('Блестяще! Вы победили, отделавшись легким испугом', 1, (255, 255, 255))
            main_surface.blit(rendered, (50, 112))
        elif 89 >= game_result >= 50:
            rendered = message_font.render('Победа! В память об этой миссии у вас остался', 1,
                                           (255, 255, 255))
            main_surface.blit(rendered, (25, 112))
            rendered_2 = message_font.render('небольшой шрам', 1,
                                             (255, 255, 255))
            main_surface.blit(rendered_2, (100, 150))
        elif 49 >= game_result >= 10:
            rendered = message_font.render('Победа досталась вам ценой многочисленных ран', 1, (255, 255, 255))
            main_surface.blit(rendered, (25, 112))
        elif 9 >= game_result > 0:
            rendered = message_font.render('Несмотря на вашу победу, на обратном пути вы погибли от полученных ран', 1,
                                           (255, 255, 255))
            main_surface.blit(rendered, (10, 112))
            rendered_2 = message_font.render('от полученных ран', 1,
                                             (255, 255, 255))
            main_surface.blit(rendered_2, (100, 150))
        game_result = None
    else:
        pygame.mixer.music.load(os.path.join('data', 'lose.mp3'))
        pygame.mixer.music.play()
        rendered = message_font.render('Эти существа оказались вам не по зубам...', 1, (255, 255, 255))
        main_surface.blit(rendered, (100, 112))
    control_render = control_font.render('Нажмите пробел для новой игры', 1, (255, 255, 255))
    main_surface.blit(control_render, (175, 250))
    control_render = control_font.render('Нажмите Esc для выхода', 1, (255, 255, 255))
    main_surface.blit(control_render, (180, 290))
    pygame.display.flip()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    pygame.mixer.music.stop()
                    return True
                elif event.key == pygame.K_ESCAPE:
                    running = False
            if event.type == pygame.QUIT:
                running = False
    pygame.quit()
    sys.exit()


class Creature():
    '''сначала я хотел реализовывать через этот класс еще и врагов, но что-то пошло не так, и теперь этот класс не нужен,
    но исправлять слишком много'''

    def __init__(self, x, y, pov, area):
        self.x = x
        self.y = y
        self.pov = pov  # point of view направление взгляда
        self.habitant = area  # объект класса area
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
    """класс визуального отображения игрока"""

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
    """класс игрока"""

    def __init__(self, x, y, pov, area, hand):
        super().__init__(x, y, pov, area)
        self.walk_speed_forward = 10
        self.walk_speed_back = 10
        self.walk_speed = 10
        self.rotate_speed = 4.111111
        self.fov = 60  # field of view поле зрения
        self.hand = hand
        self.hp = 100
        self.scream = pygame.mixer.Sound(os.path.join('data', 'scream.wav'))
        self.reason = None  # reason for game over

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
        """определяет в какую сторорну смотрит игрок"""
        if 0 <= self.pov <= 180:
            self.view_up = True
        else:
            self.view_up = False
        if 0 <= self.pov <= 90 or 270 <= self.pov < 360:
            self.view_right = True
        else:
            self.view_right = False

    def piw(self):
        # стрельба
        piw.play()
        i = 1
        sinus = sin(radians(self.pov))
        cosinus = cos(radians(self.pov))
        while self.habitant.map[int((self.y - sinus * self.walk_speed * i) // 64)][int(
                (self.x + cosinus * self.walk_speed * i) // 64)] != 1:
            if self.habitant.map[int((self.y - sinus * self.walk_speed * i) // 64)][int(
                    (self.x + cosinus * self.walk_speed * i) // 64)] == 3:
                self.habitant.map[int((self.y - sinus * self.walk_speed * 2) // 64)][int(
                    (self.x + cosinus * self.walk_speed * i) // 64)] = 0
                break

            else:
                i += 1
        for i in range(15):
            if 3 in self.habitant.map[i]:
                break
            elif i == 14:
                self.reason = True

    def damage(self):
        global pause
        if not pause:
            self.scream.play()
            self.hp -= 0.005
            if self.hp <= 0:
                self.reason = False


class Mob(pygame.sprite.Sprite):
    """класс спрайта моба"""

    def __init__(self, group, state, pic_index, x, y, high):
        super().__init__(group)
        global MOB
        if state:
            self.image = MOB[0][pic_index]
            mod_fire.stop()
        else:
            self.image = MOB[1][pic_index]
            mod_fire.play()
            mod_fire.set_volume(0.5)
        self.image = pygame.transform.scale(self.image, (1, high))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Wall(pygame.sprite.Sprite):
    """Класс спрайта стены"""

    def __init__(self, group, peace_index, high, y, x):
        global WALL
        super().__init__(group)
        self.image = WALL[peace_index]
        self.image = pygame.transform.scale(self.image, (1, high))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Area():
    '''класс отвечает за рендеринг сцены (стен и мобов)
    возможно метод show получился перегруженным, но так было проще совершенствовать алгоритм отрисовки
    число 64 - это размер 1 клетки карты в пикселях'''

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
                                [1, 0, 3, 0, 0, 0, 3, 1, 0, 1, 0, 1, 1, 1, 1],
                                [1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 3, 0, 0, 1],
                                [1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 1],
                                [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 1],
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
        PP = (768, 512)  # projection plane (плоскость проекции)
        self.CAM_TO_PP = PP[0] / 2 / tan(
            radians(self.player.fov / 2))  # distance between ''camera'' and projection plane
        ANGLE_BETWEEN_RAYS = self.player.fov / PP[0]
        angle_bet = -30
        angle = self.player.pov + self.player.fov / 2
        draw_mob = False
        self.angle_cheker(angle)
        # цикл трассировки лучей. while ищут пересечения с клетками карты по 2 осям
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
            # выборка пересечения с меньшим расстоянием и нахождением мобов
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
            """данное условие предназначено для сглаживания,
             стены однако из за текстур в этом нет острой необходимости"""
            if high % 2 != 0:
                high -= 1
            Wall(wall_group, pece_index, high, int(PP[1] / 2 - high / 2), i)

            angle -= ANGLE_BETWEEN_RAYS
            self.angle_cheker(angle)
            angle_bet += ANGLE_BETWEEN_RAYS
            coords_for_texturing = []
        wall_group.draw(self.screen)

    def find_mob_sprite(self, x, y, find_high, display_x, ray_id):
        # мотод для обнаружения и редактирования спрайта моба
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
            self.player.damage()

    def draw_mob(self):
        self.mob_sprite_group.draw(self.screen)

    def angle_cheker(self, angle):
        # вспомагательный метод для show определяет в какую сторону направлен текущий луч
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


def gameplay():
    # главный игровой цикл
    global main_surface, game_result, pause
    main_surface.fill((25, 25, 25))
    running = True
    pygame.mixer.music.load(os.path.join('data', 'gameplay.mp3'))
    pygame.mixer.music.play()
    FPS_CONTROL = 30
    pygame.time.set_timer(FPS_CONTROL, 50)
    SHOW_HP_CONTROL = 29  # это сделано для упрощения восприятия игроком урона
    pygame.time.set_timer(SHOW_HP_CONTROL, 1000)
    world = Area(main_surface)
    hand = pygame.sprite.Group()
    Hand(hand)
    player = Player(112.72611227386236, 96.71555688615558, 1.000000010000008, world, hand)
    world.add_creature(player)
    forward, back, left, right, wait_piw = False, False, False, False, False
    hp_font = pygame.font.Font(None, 42)
    rendered = hp_font.render(f'HP: {int(player.hp)}%', 1, (255, 0, 0))
    while running:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if not pause:
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
                        load.play()
                        hand.update(True)
                    if keys[pygame.K_ESCAPE]:
                        pause = True
                else:
                    pause = False
            if not pause and event.type == pygame.KEYUP:
                keys = pygame.key.get_pressed()
                if not keys[pygame.K_UP]:
                    forward = False
                if not keys[pygame.K_DOWN]:
                    back = False
                if not keys[pygame.K_LEFT]:
                    left = False
                if not keys[pygame.K_RIGHT]:
                    right = False
                if event.key == pygame.K_a:
                    load.stop()
                    hand.update(False)
                    player.piw()
                print(player.x, player.y, player.pov)  # simple debug
            if event.type == pygame.QUIT:
                running = False
            if event.type == SHOW_HP_CONTROL:
                if not pause:
                    rendered = hp_font.render(f'HP: {int(player.hp)}%', 1, (255, 0, 0))
            if event.type == FPS_CONTROL:
                if not pause:
                    if forward:
                        player.walk_forward()
                    if back:
                        player.walk_back()
                    if right:
                        player.rotate_right()
                    if left:
                        player.rotate_left()
                    if player.reason:
                        game_result = player.hp
                        pygame.mixer.music.stop()
                        return True
                    elif player.reason == False:
                        pygame.mixer.music.stop()
                        main_surface.fill((25, 25, 25))
                        world.show()
                        world.draw_mob()
                        rendered = hp_font.render(f'HP: 0%', 1, (255, 0, 0))
                        main_surface.blit(rendered, (0, 0))
                        pygame.display.flip()
                        return False
                    pygame.display.flip()
                    main_surface.fill((25, 25, 25))
                    world.show()
                    world.draw_mob()
                    hand.draw(main_surface)
                    main_surface.blit(rendered, (0, 0))
                else:
                    pygame.display.flip()
                    main_surface.fill((25, 25, 25))
                    pause_message = hp_font.render('Нажмите любую клавишу для продолжения игры', 1, (255, 255, 255))
                    main_surface.blit(pause_message, (25, 250))
    pygame.quit()
    sys.exit()


def start_menu():
    global main_surface
    pygame.mixer.music.load(os.path.join('data', 'opening.mp3'))
    pygame.mixer.music.play(-1)
    start_background = load_image('start_background.png')
    main_surface.blit(start_background, (0, 0))
    pygame.display.flip()
    running = True
    state = None
    show_story = False
    while running:
        if show_story:
            main_surface.blit(load_image('lor.jpg'), (0, 0))
            pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if show_story:
                    pygame.mixer.music.stop()
                    state = ['gameplay', gameplay()]
                    running = False
                else:
                    if event.key == pygame.K_SPACE:
                        show_story = True
                    if event.key == pygame.K_ESCAPE:
                        running = False
    if state is None:
        pygame.quit()
        sys.exit()
    else:
        while state != ['gameover', False]:
            if state[0] == 'gameplay':
                state[0] = 'gameover'
                state[1] = gameover(state[1])
            if state[0] == 'gameover':
                state = ['gameplay', gameplay()]
        pygame.quit()
        sys.exit()


start_menu()
