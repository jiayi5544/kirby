import pygame
import random
import os

FPS = 60

WIDTH = 500
HEIGHT = 600

WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)

# Initialize Pygame
pygame.init()
pygame.mixer.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("小遊戲")

# Load images with error checking
def load_image(file_path):
    try:
        image = pygame.image.load(file_path).convert_alpha()
        return image
    except pygame.error as e:
        print(f"Cannot load image: {file_path}")
        raise SystemExit(e)

back_img = load_image(os.path.join("img", "back.jpg"))
kirby_img = load_image(os.path.join("img", "kirby.png"))
rockk_img = load_image(os.path.join("img", "rockk.png"))
bullets_img = load_image(os.path.join("img", "bullett.png"))

expl_anim = {'ig': [], 'sm': []}
for i in range(9):
    expl_img = load_image(os.path.join("img", f"expl{i}.png"))
    expl_img.set_colorkey(BLACK)
    expl_anim['ig'].append(pygame.transform.scale(expl_img, (75, 75)))
    expl_anim['sm'].append(pygame.transform.scale(expl_img, (30, 30)))

# Load sounds with error checking
def load_sound(file_path):
    try:
        sound = pygame.mixer.Sound(file_path)
        return sound
    except pygame.error as e:
        print(f"Cannot load sound: {file_path}")
        raise SystemExit(e)

shoot_sound = load_sound(os.path.join("sound", "shoot.mp3"))
expl_sounds = [
    load_sound(os.path.join("sound", "expl0.mp3")),
    load_sound(os.path.join("sound", "expl1.mp3"))
]

try:
    pygame.mixer.music.load(os.path.join("sound", "background.mp3"))
    pygame.mixer.music.set_volume(0.4)
except pygame.error as e:
    print(f"Cannot load music: {os.path.join('sound', 'background.mp3')}")
    raise SystemExit(e)

clock = pygame.time.Clock()

font_name = os.path.join('sound', "font.tt.ttf")
def draw_text(surf, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.centerx = x
    text_rect.top = y
    surf.blit(text_surface, text_rect)

def new_rock():
    r = Rock()
    all_sprites.add(r)
    rocks.add(r)

def draw_health(surf, hp, x, y):
    if hp < 0:
        hp = 0
    BAR_LENGTH = 100
    BAR_HEIGHT = 10
    fill = (hp / 100) * BAR_LENGTH
    outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
    pygame.draw.rect(surf, GREEN, fill_rect)
    pygame.draw.rect(surf, WHITE, outline_rect, 2)

def draw_init():
    screen.blit(back_img, (0, 0))
    draw_text(screen, '卡比生存戰!', 64, WIDTH/2, HEIGHT/4)
    draw_text(screen, '← →移動飛船 空白鍵發射子彈~', 28, WIDTH/2, HEIGHT/2)
    draw_text(screen, '按任意鍵開始遊戲!', 25, WIDTH/2, HEIGHT*3/4)
    pygame.display.update()
    waiting = True
    while waiting:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
               pygame.quit()
            elif event.type == pygame.KEYUP:
                waiting = False

class Player(pygame.sprite.Sprite):
      def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(kirby_img, (85, 95))
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH / 2
        self.rect.bottom = HEIGHT - 10
        self.speedx = 15
        self.health = 100

      def update(self):
        key_pressed = pygame.key.get_pressed()
        if key_pressed[pygame.K_RIGHT]:
            self.rect.x += self.speedx
        if key_pressed[pygame.K_LEFT]:
            self.rect.x -= self.speedx

        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0

      def shoot(self):
        bullet = Bullet(self.rect.centerx, self.rect.top)
        all_sprites.add(bullet)
        bullets.add(bullet)
        shoot_sound.play()

class Rock(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(rockk_img, (50, 50))
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(0, WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speedy = random.randrange(2, 10)    
        self.speedx = random.randrange(-3, 3)
        self.radius = int(self.rect.width * 0.55 / 2)

    def update(self):
        self.rect.y += self.speedy
        self.rect.x += self.speedx
        if self.rect.top > HEIGHT or self.rect.left > WIDTH or self.rect.right < 0:
            self.rect.x = random.randrange(0, WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speedy = random.randrange(1, 5)
            self.speedx = random.randrange(-3, 3)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(bullets_img, (10, 50))
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speedy = -20 

    def update(self):
        self.rect.y += self.speedy
        if self.rect.bottom < 0:
            self.kill()

class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, size):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = expl_anim[self.size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 200

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(expl_anim[self.size]):
                self.kill()
            else:
                self.image = expl_anim[self.size][self.frame]
                center = self.rect.center
                self.rect = self.image.get_rect()
                self.rect.center = center

# Create sprite groups and add player
all_sprites = pygame.sprite.Group()
rocks = pygame.sprite.Group()
bullets = pygame.sprite.Group()
player = Player()
all_sprites.add(player)
for i in range(8):
    new_rock()
score = 0
pygame.mixer.music.play(-1)

show_init = True
rock_spawn_time = pygame.time.get_ticks()
running = True

while running:
    if show_init:
        draw_init()
        show_init = False
        all_sprites = pygame.sprite.Group()
        rocks = pygame.sprite.Group()
        bullets = pygame.sprite.Group()
        player = Player()
        all_sprites.add(player)
        for i in range(8):
            new_rock()
        score = 0

    clock.tick(FPS)

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.shoot()

    # Update the game state
    all_sprites.update()

    # Detect collisions between rocks and bullets
    rock_bullet_hits = pygame.sprite.groupcollide(rocks, bullets, True, True)
    for hit in rock_bullet_hits:
        random.choice(expl_sounds).play()
        score += hit.radius
        expl = Explosion(hit.rect.center, 'ig')
        all_sprites.add(expl)
        new_rock()

    # Detect collisions between player and rocks
    player_rock_hits = pygame.sprite.spritecollide(player, rocks, True)
    for hit in player_rock_hits:
        new_rock()
        player.health -= hit.radius
        if player.health <= 0:
           

            running = False

    # Clear the screen with a black color
    screen.fill(BLACK)
    screen.blit(back_img, (0, 0))
    all_sprites.draw(screen)
    draw_text(screen, str(score), 18, WIDTH / 2, 10)
    draw_health(screen, player.health, 5, 15)

    # Update the display
    pygame.display.flip()

# Quit Pygame
pygame.quit()

