import pygame

from sprite import load_image, MySprite

RUNNING, JUMPING, FALLING, FALL_AFTER_JUMP = 1010, 2020, 3030, 4040


class Runner:
    def __init__(self, x, y, sprites_group):
        self.frames = []
        self.frame = 0
        self.base_rect = None
        self.cut_sheet(load_image("runner.png"), 6, 1)
        self.sprite = MySprite(sprites_group, self.frames[0], x, y)
        self.sprites_group = sprites_group
        self.state = None
        self.y_acceleration = 0
        self.controllable = True

        self.mixer = pygame.mixer
        self.mixer.init()
        self.jump_sound = self.mixer.Sound('sounds/jump.mp3')

    def cut_sheet(self, sheet, columns, rows):
        self.base_rect = pygame.Rect(0, 0, sheet.get_width() // columns, sheet.get_height() // rows)
        for i in range(columns):
            frame_location = (self.base_rect.w * i, 0)
            self.frames.append(sheet.subsurface(pygame.Rect(frame_location, self.base_rect.size)))

    def jump(self, power=15):
        if self.state == RUNNING or self.y_acceleration == 0:
            self.y_acceleration = power
            self.state = JUMPING
            self.jump_sound.play()

    def update(self):
        if self.state == RUNNING and self.y_acceleration > -4:
            pass
        elif self.y_acceleration < -10:
            if self.controllable:
                if self.state == JUMPING:
                    self.state = FALL_AFTER_JUMP
            else:
                self.state = FALLING
        elif self.check_collisions() and self.state != JUMPING:
            self.state = RUNNING
        if self.state == RUNNING:
            self.frame = (self.frame + 1) % 4
        elif self.state == JUMPING:
            self.frame = 4
        elif self.state == FALLING:
            self.frame = 5
        self.sprite.image = self.frames[self.frame]
        self.sprite.rect.top -= self.y_acceleration
        if not self.check_collisions():
            if self.y_acceleration > 0:
                self.y_acceleration -= .4
            else:
                self.y_acceleration -= .8
        elif self.state != JUMPING:
            self.y_acceleration = 0
        platform = self.check_collisions()
        if platform and platform.rect.top < self.sprite.rect.bottom:
            self.sprite.rect.move_ip(0, platform.rect.top - self.sprite.rect.h - self.sprite.rect.top + 1)
            # self.y_acceleration = 1

    def check_collisions(self):
        for sprite in self.sprites_group:
            if sprite == self.sprite:
                continue
            if pygame.sprite.collide_rect(self.sprite, sprite):
                return sprite
        return False

