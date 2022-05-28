import pygame
from platform import system
from utils import fetch_text, fetch_image, getcwd, join
from random import randint as rand
from math import sin, cos, pi
from numpy import clip as clamp
# noinspection PyBroadException
try:
    from win32api import EnumDisplayDevices, EnumDisplaySettings
    FRAMERATE = EnumDisplaySettings(EnumDisplayDevices().DeviceName, -1).DisplayFrequency \
        if "Windows" in system() else 60
except Exception:
    FRAMERATE = 60


class BoosterParticle:
    def __init__(self, pos: tuple[float, float]):
        self.x, self.y = pos
        self.x += rand(-10, 10)
        self.y += rand(-10, 10)
        self.age = rand(10, 20)

    def draw(self):
        self.age -= 0.4
        self.x += rand(-2, 2)
        self.y += rand(-2, 2)
        pygame.draw.circle(screen, ORANGE_COLOR.lerp((0, 0, 0), rand(0, 3)*0.1), (self.x+screen_shake[0], self.y+screen_shake[1]), self.age/2)
        return not self.age


class Player:
    def __init__(self):
        self.x = WIDTH/2
        self.y = HEIGHT/2
        self.dx = 0
        self.dy = 0
        self.drot = 0
        self.rot = 0
        self.image = fetch_image("player.png")
        self.rot_speed = 0.4
        self.move_speed = 0.2
        self.max_speed = 6

    @property
    def rect(self):
        return pygame.Rect(self.x-self.image.get_width()/2, self.y-self.image.get_height()/2, self.image.get_width(), self.image.get_height())

    @property
    def pos(self):
        return self.x, self.y

    def draw(self, surface: pygame.Surface):
        self.image = fetch_image("player.png", self.rot+pi/2)
        draw_pos = self.image.get_rect(center=self.pos)[:2]
        surface.blit(self.image, (draw_pos[0]+screen_shake[0], draw_pos[1]+screen_shake[1]))

    def move(self):
        global screen_shake
        self.drot *= 0.9 * 75/FRAMERATE
        self.rot += self.drot
        keys = pygame.key.get_pressed()
        move = keys[pygame.K_w]-keys[pygame.K_s]
        screen_shake = [0, 0]
        if move != 0:
            screen_shake = [rand(-2, 2), rand(-2, 2)]
        self.drot += (keys[pygame.K_d]-keys[pygame.K_a])*self.rot_speed/FRAMERATE
        self.dx += cos(self.rot)*move*self.move_speed
        self.dy += sin(self.rot)*move*self.move_speed
        ms = self.max_speed
        self.dx, self.dy = clamp(self.dx, -ms, ms), clamp(self.dy, -ms, ms)
        self.x += self.dx
        self.y += self.dy
        self.x, self.y = self.x % WIDTH, self.y % HEIGHT
        if move != 0:
            booster_particles.append(BoosterParticle(self.pos))


class Grass:
    def __init__(self, pos: tuple[int, int]):
        self.x, self.y = pos
        self.image = fetch_image("grass.png")

    def draw(self, surface: pygame.Surface):
        surface.blit(self.image, self.pos)

    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, self.image.get_width(), self.image.get_height())

    @property
    def pos(self):
        return self.x+screen_shake[0], self.y+screen_shake[1]

    def reposition(self):
        touched = False
        while self.touching_player(player):
            self.x = rand(0, WIDTH-self.rect.w)
            self.y = rand(0, HEIGHT-self.rect.h)
            touched = True
        return touched

    def touching_player(self, pl: Player):
        return self.rect.colliderect(pl.rect)


pygame.init()
timer = 0

WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode([WIDTH, HEIGHT])
font = pygame.font.Font(join(getcwd(), "assets", "Arialn.ttf"), 40)
pygame.display.set_caption("one hour game jam")
clock = pygame.time.Clock()
screen_shake = [0, 0]

# colors
BG_COLOR = pygame.Color(17, 19, 68)
ORANGE_COLOR = pygame.Color(242, 100, 25)
MENU_TEXT_COLOR = pygame.Color(54, 53, 55)

grass = Grass((770, 70))
player = Player()
score = 0
win_req = 20

booster_particles = []

viewing_screen = 0  # 0=menu,1=game,2=end

running = True
while running:
    screen.fill(BG_COLOR)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if viewing_screen == 0:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button in (1, 3):
                    viewing_screen = 1

    if viewing_screen == 0:  # menu
        screen.fill((12, 206, 107))
        screen.blit(fetch_text(font, "grass astronaut", MENU_TEXT_COLOR), (10, 10))
        screen.blit(fetch_text(font, "click anywhere to play", MENU_TEXT_COLOR), (10, 55))
        screen.blit(fetch_text(font, f"collect {win_req} grass to win", MENU_TEXT_COLOR), (10, 100))
    if viewing_screen == 1:  # game
        timer += 1/FRAMERATE
        kill_list = []
        for particle in booster_particles:
            if particle.draw():
                kill_list.append(particle)
        for kill in kill_list:
            booster_particles.remove(kill)

        grass.draw(screen)
        player.draw(screen)
        player.move()
        score += grass.reposition()
        if score >= win_req:
            viewing_screen = 2

        screen.blit(fetch_text(font, f"score: {score}/{win_req}"), (10+screen_shake[0], 10+screen_shake[1]))
    if viewing_screen == 2:  # you won
        screen.blit(fetch_text(font, "you win!", (220, 237, 49)), (10, 10))
        screen.blit(fetch_text(font, f"it took you {int(timer*8)/8} seconds"), (10, 55))
        screen.blit(fetch_text(font, f"game by quasar098"), (10, 200))
    pygame.display.flip()
    clock.tick(FRAMERATE)
pygame.quit()
