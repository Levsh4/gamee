import os
import math
import random
import pygame as pg

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
LT_BLUE = (173, 216, 230)
GREEN = (0, 255, 0)


class Satellite(pg.sprite.Sprite):

    def __init__(self, background):
        super().__init__()
        self.background = background
        self.image_sat = pg.image.load('satelite_8897913.png').convert()
        self.image_crash = pg.image.load("satelite_crash.png").convert()

        self.image = self.image_sat
        self.rect = self.image.get_rect()
        self.image.set_colorkey(BLACK)

        self.x = random.randrange(315, 215, -100)
        self.y = random.randrange(80, 170)

        self.dx = random.choice([-3, 3])
        self.dy = 0

        self.heading = 0
        self.fuel = 0
        self.mass = 1
        self.distance = 0

        self.thrust = pg.mixer.Sound('thrust_audio.ogg')
        self.thrust.set_volume(0.08)

    def thruster(self, dx, dy):
        self.dx += dx
        self.dy += dy
        self.fuel -= 3
        self.thrust.play()

    def check_keys(self):
        keys = pg.key.get_pressed()

        if keys[pg.K_RIGHT]:
            self.thruster(dx=0.5, dy=0)
        elif keys[pg.K_LEFT]:
            self.thruster(dx=-0.5, dy=0)
        elif keys[pg.K_UP]:
            self.thruster(dx=0, dy=-0.5)
        elif keys[pg.K_DOWN]:
            self.thruster(dx=0, dy=0.5)

    def locate(self, planet):
        px, py = planet.x, planet.y
        dist_x = self.x - px
        dist_y = self.y - py
        planet_dir_radians = math.atan2(dist_x, dist_y)
        self.heading = planet_dir_radians * 180 / math.pi
        self.heading -= 90
        self.distance = math.hypot(dist_x, dist_y)

    def rotate(self):
        self.image = pg.transform.rotate(self.image_sat, self.heading)
        self.rect = self.image.get_rect()

    def path(self):
        last_center = (self.x, self.y)
        self.x += self.dx
        self.y += self.dy
        pg.draw.line(self.background, WHITE, last_center, (self.x, self.y))

    def update(self):
        self.check_keys()
        self.rotate()
        self.path()
        self.rect.center = (self.x, self.y)

        if self.dx == 0 and self.dy == 0:
            self.image = self.image_crash
            self.image.set_colorkey(BLACK)


class Planet(pg.sprite.Sprite):

    def __init__(self):
        super().__init__()
        self.image_mars = pg.image.load('mars.png').convert()
        self.image_water = pg.image.load('mars_water.jpg').convert()
        self.image_copy = pg.transform.scale(self.image_mars, (100, 100))
        self.image_copy.set_colorkey(BLACK)
        self.rect = self.image_copy.get_rect()
        self.image = self.image_copy
        self.mass = 2000
        self.x = 400
        self.y = 320
        self.rect.center = (self.x, self.y)
        self.angle = math.degrees(0)
        self.rotate_by = math.degrees(0.01)

    def rotate(self):
        last_center = self.rect.center
        self.image = pg.transform.rotate(self.image_copy, self.angle)
        self.rect = self.image.get_rect()
        self.rect.center = last_center
        self.angle += self.rotate_by

    def gravity(self, satellite):
        G = 1  # gravity
        dist_x = self.x - satellite.x
        dist_y = self.y - satellite.y
        distance = math.hypot(dist_x, dist_y)

        dist_x /= distance
        dist_y /= distance

        force = G * (satellite.mass * self.mass) / (math.pow(distance, 2))
        satellite.dx += (dist_x * force)
        satellite.dy += (dist_y * force)

    def update(self):
        self.rotate()


def calc_eccentricity(dist_list):
    apoapsis = max(dist_list)
    periapsis = min(dist_list)

    eccentricity = ((apoapsis - periapsis) / (apoapsis + periapsis))

    return eccentricity


def instruct_label(screen, text, color, x, y):
    instruct_font = pg.font.SysFont(None, 25)
    line_spracing = 22

    for index, line in enumerate(text):
        label = instruct_font.render(line, True, color, BLACK)
        screen.blit(label, (x, y + index * line_spracing))


def box_label(screen, text, dimension):
    readout_font = pg.font.SysFont(None, 27)
    base = pg.Rect(dimension)
    pg.draw.rect(screen, WHITE, base, 0)
    label = readout_font.render(text, True, BLACK)
    label_rect = label.get_rect(center=base.center)
    screen.blit(label, label_rect)


def mapping_on(planet):
    last_center = planet.rect.center
    planet.image_copy = pg.transform.scale(planet.image_water, (100, 100))
    planet.image_copy.set_colorkey(BLACK)
    planet.rect = planet.image_copy.get_rect()
    planet.rect.center = last_center


def mapping_off(planet):
    planet.image_copy = pg.transform.scale(planet.image_water, (100, 100))
    planet.image_copy.set_colorkey(BLACK)


def cast_shdow(screen):
    shadow = pg.Surface((400, 100),
                        flags=pg.SRCALPHA)
    shadow.fill((0, 0, 0, 210))
    screen.blit(shadow, (0, 270))


def main():
    pg.init()

    os.environ['SDL_VIDEO_WINDOW_POS'] = '700,100'
    screen = pg.display.set_mode((800, 645), pg.FULLSCREEN)
    pg.display.set_caption('картографирование марса')
    background = pg.Surface(screen.get_size())

    pg.mixer.init()

    intro_text = [
        'орбитальный спутник испытал неполадку' \
        'при выведении на орбиту' \
        'используйте двигатели для коррекции орбиты' \
        'картографирование' \
        'без исчерпания топлива или сгорания в атмосфере'
    ]

    instruct_text1 = [
        'высота орбиты в пределах 69-120',
        'эксцентрисситет орбиты должен быть < 0,5'
        'избегайте верхних слоев атмосферы в 68 миль'
    ]

    instruct_text2 = [
        'стрелка влево = уменшить Dx'
        'стрелка вправо = увеличить Dx'
        'стрелка вверх = уменьшить Dy'
        'стрелка вниз = увеличить Dy'
        'пробел = очистить траекторию'
        'esc = выйти из полноэкранного режима'
    ]
    planet = Planet()
    planet_sprite = pg.sprite.Group(planet)
    sat = Satellite(background)
    sat_sprite = pg.sprite.Group(sat)

    dist_list = []
    eccentricity = 1
    eccentricity_calc_interval = 5

    clock = pg.time.Clock()
    fps = 30
    tick_count = 0

    mapping_enabled = False

    running = True
    while running:
        clock.tick(fps)
        tick_count += 1
        dist_list.append(sat.distance)

        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    screen = pg.display.set_mode((800, 645))
                elif event.key == pg.K_SPACE:
                    background.fill(BLACK)  # Очистка траектории

        sat.check_keys()
        sat.locate(planet)
        planet.gravity(sat)

        if tick_count % (eccentricity_calc_interval * fps) == 0:
            eccentricity = calc_eccentricity(dist_list)
            dist_list = []

        screen.blit(background, (0, 0))

        if sat.fuel <= 0:
            instruct_label(screen, ['топливо исчерпано!'], RED, 340, 195)
            sat.fuel = 0
            sat.dx = 2

        elif sat.distance <= 68:
            instruct_label(screen, ['вход в атмосферу!'], RED, 320, 195)
            sat.dx = 0
            sat.dy = 0

        if eccentricity < 0.05 and 69 <= sat.distance <= 120:
            map_instruct = ['нажмите и удерживайте m']

            instruct_label(screen, map_instruct, LT_BLUE, 250, 175)
            mapping_enabled = True

        else:
            mapping_enabled = False

        planet_sprite.update()
        planet_sprite.draw(screen)
        sat_sprite.update()
        sat_sprite.draw(screen)

        if pg.time.get_ticks() <= 15000:
            instruct_label(screen, intro_text, GREEN, 145, 100)

            box_label(screen, 'Dx', (70, 20, 75, 20))
            box_label(screen, 'Dy', (150, 20, 80, 20))
            box_label(screen, 'Высота', (240, 20, 160, 20))
            box_label(screen, 'Топливо', (410, 20, 160, 20))
            box_label(screen, 'Эксцентриситет', (580, 20, 150, 20))

            box_label(screen, '{:.1f}'.format(sat.dx), (70, 50, 75, 20))
            box_label(screen, '{:.1f}'.format(sat.dy), (150, 50, 80, 20))
            box_label(screen, '{:.1f}'.format(sat.distance), (240, 50, 160, 20))
            box_label(screen, '{}'.format(sat.fuel), (410, 50, 160, 20))
            box_label(screen, '{:.8f}'.format(eccentricity), (580, 50, 150, 20))

            instruct_label(screen, instruct_text1, WHITE, 10, 575)
            instruct_label(screen, instruct_text2, WHITE, 570, 510)

            cast_shdow(screen)
            pg.draw.rect(screen, WHITE, (1, 1, 798, 643), 1)
            pg.display.flip()


if __name__ == "__main__":
    main()
