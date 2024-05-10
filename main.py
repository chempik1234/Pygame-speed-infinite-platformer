import math
import random

import pygame

from runner import Runner
from sprite import MySprite, load_image

WIDTH = 600
HEIGHT = 600
FPS = 100
GAMEPLAY, DEATH, PLAY_MENU, EXIT = 1111, 2222, 3333, 4444


def render_text(text, text_coord_x, text_coord_y, font_size, color, screen):
    font = pygame.font.Font(None, font_size)
    for line_number in range(len(text)):
        line = text[line_number]
        string_rendered = font.render(line, 1, color)
        _rect = string_rendered.get_rect()
        _rect.top = text_coord_y
        _rect.x = text_coord_x
        text_coord_y += _rect.height
        screen.blit(string_rendered, _rect)


class Game:
    def __init__(self, width=WIDTH, height=HEIGHT, fps=FPS):
        self.screen_size = (width, height)
        pygame.init()
        pygame.display.set_caption('Jump')
        self.screen = pygame.display.set_mode(self.screen_size)
        self.clock = pygame.time.Clock()
        self.fps = fps
        self.display = pygame.display

        self.background_group = pygame.sprite.Group()
        self.sprites_group = pygame.sprite.Group()
        self.score = None

        self.window = None

        self.mixer = pygame.mixer
        self.mixer.init()
        self.water_sound = self.mixer.Sound("sounds/watersplash.mp3")
        self.menu_sound = self.mixer.Sound("sounds/menu.mp3")

    def run(self):
        self.window = PLAY_MENU
        running = True
        while running:
            self.sprites_group.empty()
            self.background_group.empty()
            if self.window == GAMEPLAY:
                self.score = 0
                self.play_level()
            elif self.window == DEATH:
                self.play_death()
            elif self.window == PLAY_MENU:
                self.play_restart()
            elif self.window == EXIT:
                running = False

    def play_level(self):
        bg_speed, platform_speed = 1, 10
        running = True
        runner = Runner(self.screen_size[0] * 0.2, self.screen_size[1] * 0.2, self.sprites_group)

        backgrounds = self.generate_backgrounds()

        platforms = self.generate_platforms()
        while running:
            if platforms[-1].rect.right <= self.screen_size[0]:
                platforms.append(self.generate_platform(platforms[-1].rect.right - 3,
                                                        self.background_group in platforms[-1].groups()))
            if platforms[0].rect.right < 0:
                platforms[0].kill()
                platforms.pop(0)
                self.score += 1
            self.clock.tick(self.fps)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.window = EXIT
                    running = False
                if event.type == pygame.KEYDOWN:
                    runner.jump()
            self.screen.fill(pygame.Color("white"))
            self.background_group.draw(self.screen)
            self.sprites_group.draw(self.screen)
            for bg in backgrounds:
                bg.rect.move_ip(-bg_speed, 0)
            for i in platforms:
                i.rect.move_ip(-platform_speed, 0)
            if backgrounds[0].rect.right <= 0:
                backgrounds[0].rect.move_ip(-backgrounds[0].rect.left + backgrounds[-1].rect.right, 0)
                backgrounds.append(backgrounds.pop(0))
            runner.update()
            render_text([str(self.score)], self.screen_size[0] // 2 - 50, self.screen_size[1] // 15,
                        72, pygame.Color("white"), self.screen)
            if runner.sprite.rect.y > self.screen_size[1] * 0.7:
                running = False
                self.window = DEATH
            pygame.display.flip()

    def generate_backgrounds(self):
        """ ### SKY """
        sky_image = load_image("sky.png")
        for i in range(math.ceil(self.screen_size[0] / sky_image.get_rect().w)):
            MySprite(self.background_group, sky_image, i * sky_image.get_rect().w, 0)
        """ ### BACKGROUND """
        bg_image, backgrounds = load_image("bg.png"), []
        for i in range(math.ceil(self.screen_size[0] / bg_image.get_rect().w) + 1):
            backgrounds.append(MySprite(self.background_group, bg_image, i * bg_image.get_rect().w, 0))
        return backgrounds

    def generate_platforms(self):
        res, length = [], 0
        while not res or res[-1].rect.right < self.screen_size[0]:
            x = 0
            b = False
            if length > 0:
                x = res[-1].rect.right - 20
                b = self.background_group in res[-1].groups()
            if length > 1:
                b = b or self.background_group in res[-2].groups()
            b = b or length < 10
            res.append(self.generate_platform(x, b))
            length += 1
        return res

    def generate_platform(self, x=None, platform_required=False):
        if x is None:
            x = self.screen_size[0]
        y = self.screen_size[1] * (random.randint(24, 28) / 40)
        if random.random() > 0.9 and not platform_required:
            return MySprite(self.background_group, load_image("pit.png"), x, y)
        else:
            return MySprite(self.sprites_group, load_image("platform.png"), x, y)

    def play_death(self):
        runner = Runner(self.screen_size[0] // 2, 0, self.sprites_group)
        runner.controllable = False
        self.generate_backgrounds()
        running = True
        playing = False
        while running:
            tick = self.clock.tick(self.fps)
            runner.update()
            if runner.sprite.rect.top > self.screen_size[1] * 0.7 and not playing:
                self.water_sound.play()
                playing = True
            self.background_group.draw(self.screen)
            self.sprites_group.draw(self.screen)
            render_text(["ВЫ УПАЛИ!", "ОЧКИ: " + str(self.score)],
                        self.screen_size[0] // 2 - self.screen_size[0] // 3,
                        self.screen_size[1] // 10, 72, pygame.Color("black"), self.screen)
            render_text(["ВЫ УПАЛИ!", "ОЧКИ: " + str(self.score)],
                        self.screen_size[0] // 2 - self.screen_size[0] // 3,
                        self.screen_size[1] // 10 - 10, 72, pygame.Color("white"), self.screen)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    self.window = EXIT
                if event.type == pygame.KEYDOWN:
                    running = False
                    self.window = PLAY_MENU
            self.display.flip()

    def play_restart(self):
        self.menu_sound.play()
        for i in range(self.screen_size[1]):
            self.screen.fill(pygame.Color(int(i / self.screen_size[1] * 255),
                                          int((i + 128) / self.screen_size[1] * 255) % 255,
                                          int((i + 200) / self.screen_size[1] * 255) % 255),
                             (0, i, self.screen_size[0], 1))
        render_text(["НАЧАТЬ ИГРУ", "НАЖМИТЕ ЛЮБУЮ КЛАВИШУ"], self.screen_size[0] // 2 - 300,
                    self.screen_size[1] * 0.1, 48, pygame.Color("black"), self.screen)
        pygame.display.flip()
        running = True
        while running:
            self.clock.tick(self.fps)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.window = EXIT
                    running = False
                if event.type == pygame.KEYDOWN:
                    self.window = GAMEPLAY
                    self.menu_sound.play()
                    running = False


if __name__ == '__main__':
    game = Game()
    game.run()
