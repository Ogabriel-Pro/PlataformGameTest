import pgzrun
import random
from pygame import Rect

# Configurações
TITLE = "Platformer"
WIDTH = 800
HEIGHT = 1000

# Estados do jogo
MENU = 0
PLAYING = 1
GAME_OVER = 2
game_state = MENU

# Controle de volume
sounds_on = True

# Botões do menu
start_button = Rect((WIDTH // 2 - 60, HEIGHT // 2 - 40, 120, 40))
sound_button = Rect((WIDTH // 2 - 60, HEIGHT // 2 + 20, 120, 40))
exit_button = Rect((WIDTH // 2 - 60, HEIGHT // 2 + 80, 120, 40))

background = Actor('background')

platforms = [
    Rect((200, 700, 200, 20)),
    Rect((500, 500, 150, 20)),
    Rect((100, 300, 180, 20)),
]


class Player:
    def __init__(self):
        self.x_speed = 5
        self.direction = 'right'
        self.frame = 0
        self.animation_speed = 0.2
        self.moving = False 
        self.jump_speed = -20    
        self.gravity = 0.7    
        self.velocity_y = 0       
        self.on_ground = True     
        self.images = {
            'idle': [
                Actor('player/idle_0'),
                Actor('player/idle_1'),
                Actor('player/idle_2')
            ],
            'left': [
                Actor('player/walk_left_0'),
                Actor('player/walk_left_1'),
                Actor('player/walk_left_2')
            ],
            'right': [
                Actor('player/walk_right_0'),
                Actor('player/walk_right_1'),
                Actor('player/walk_right_2')
            ]
        }
        for state in self.images:
            for img in self.images[state]:
                img.pos = (WIDTH // 2, HEIGHT - 100)
        self.actor = self.images['right'][0]  
        self.collision_rect_offset_x = 10 
        self.collision_rect_offset_y = 5
        self.collision_rect_width = 40
        self.collision_rect_height = 100

    def get_collision_rect(self):
        return Rect(self.actor.x - self.collision_rect_width / 2 + self.collision_rect_offset_x, 
                    self.actor.y - self.collision_rect_height / 2 + self.collision_rect_offset_y, 
                    self.collision_rect_width,
                    self.collision_rect_height)

    def draw(self):
        if self.moving:
            current_state = self.direction
        else:
            current_state = 'idle'
        sprite = self.images[current_state][int(self.frame)]
        sprite.pos = self.actor.pos
        sprite.draw()

    def update(self):
        self.moving = False
        self.frame += self.animation_speed
        if self.frame >= len(self.images['right']):
            self.frame = 0
        if keyboard.left:
            self.direction = 'left'
            self.actor.x -= self.x_speed
            self.moving = True
        elif keyboard.right:
            self.direction = 'right'
            self.actor.x += self.x_speed
            self.moving = True
        if keyboard.space and self.on_ground:
            if sounds_on:
                sounds.jump.play()
            self.velocity_y = self.jump_speed
            self.on_ground = False
        self.actor.y += self.velocity_y
        if not self.on_ground:
            self.velocity_y += self.gravity
        self.on_ground = False
        player_collision_rect = self.get_collision_rect()
        for plat in platforms:
            if self.velocity_y >= 0 and player_collision_rect.colliderect(plat):
                if player_collision_rect.bottom <= plat.top + abs(self.velocity_y):
                    self.actor.y -= (player_collision_rect.bottom - plat.top)
                    self.velocity_y = 0
                    self.on_ground = True
                    break
        player_collision_rect = self.get_collision_rect()
        ground_y = HEIGHT - 100
        if player_collision_rect.bottom >= ground_y:
            self.actor.y -= (player_collision_rect.bottom - ground_y)
            self.velocity_y = 0
            self.on_ground = True
        if self.actor.x < 50:
            self.actor.x = 50
        if self.actor.x > WIDTH - 50:
            self.actor.x = WIDTH - 50

class Enemy:
    def __init__(self):
        self.images = [
            Actor('enemy/drop_0'),
            Actor('enemy/drop_1'),
            Actor('enemy/drop_2')
        ]
        self.frame = 0
        self.animation_speed = 0.2
        self.speed = random.randint(3, 7)
        self.images[int(self.frame)].pos = (random.randint(50, WIDTH - 50), -50)
        self.actor = self.images[0]

    def draw(self):
        sprite = self.images[int(self.frame)]
        sprite.pos = self.actor.pos
        sprite.draw()

    def update(self):
        self.frame += self.animation_speed
        if self.frame >= len(self.images):
            self.frame = 0
        self.actor.y += self.speed

    def off_screen(self):
        return self.actor.y > HEIGHT + 50

class OxygenTank:
    def __init__(self):
        self.images = [
            Actor('oxygen_tank_0'),
            Actor('oxygen_tank_1'),
            Actor('oxygen_tank_2')
        ]
        self.frame = 0
        self.animation_speed = 0.2
        # Escolher uma plataforma aleatória
        platform = random.choice(platforms)
        # Posicionar o tanque acima da plataforma, no centro da mesma
        self.x = platform.x + platform.width // 2
        self.y = platform.y - 60  # Acima da plataforma
        self.actor = self.images[0]
        self.actor.pos = (self.x, self.y)

    def draw(self):
        sprite = self.images[int(self.frame)]
        sprite.pos = self.actor.pos
        sprite.draw()

    def update(self):
        self.frame += self.animation_speed
        if self.frame >= len(self.images):
            self.frame = 0

    def off_screen(self):
        return self.actor.y > HEIGHT + 50


player = Player()
enemies = []
oxygen_tanks = []
enemy_timer = 0
oxygen_timer = 0
enemy_interval = 1.0
oxygen_interval = 5.0 
score = 0
time_left = 20.0

music.play('music')

def draw():
    screen.clear()
    if game_state == MENU:
        screen.draw.text("Controls:", center=(WIDTH // 2, HEIGHT // 2 - 200), fontsize=30, color="white")
        screen.draw.text("left and right arrows to move", center=(WIDTH // 2, HEIGHT // 2 - 160), fontsize=28, color="white")
        screen.draw.text("space to jump", center=(WIDTH // 2, HEIGHT // 2 - 120), fontsize=28, color="white")
        screen.draw.text("Collect oxygen tanks to gain time!", center=(WIDTH // 2, HEIGHT // 2 - 80), fontsize=25, color="gray")
        screen.draw.filled_rect(start_button, (0, 200, 0))
        screen.draw.text("Start", center=start_button.center, color="white")
        screen.draw.filled_rect(sound_button, (100, 100, 255))
        screen.draw.text("Sound: On" if sounds_on else "Sound: Off", center=sound_button.center, color="white")
        screen.draw.filled_rect(exit_button, (200, 0, 0))
        screen.draw.text("Exit", center=exit_button.center, color="white")
    elif game_state == PLAYING:
        background.draw()
        for plat in platforms:
            screen.draw.filled_rect(plat, (120, 80, 40))
        player.draw()
        for enemy in enemies:
            enemy.draw()
        for tank in oxygen_tanks:
            tank.draw()
        screen.draw.text(f"Time: {int(time_left)}", (WIDTH - 120, 10), fontsize=30, color="white")
        screen.draw.text(f"Score: {score}", (10, 10), fontsize=30, color="white")
    elif game_state == GAME_OVER:
        screen.draw.text("Game Over", center=(WIDTH//2, HEIGHT//2 - 30), fontsize=60, color="red")
        screen.draw.text(f"Score: {score}", center=(WIDTH//2, HEIGHT//2 + 30), fontsize=40, color="white")
        screen.draw.text("Press R to Restart", center=(WIDTH//2, HEIGHT//2 + 80), fontsize=30, color="gray")
        screen.draw.text("Press M for Menu", center=(WIDTH//2, HEIGHT//2 + 120), fontsize=30, color="gray")

def update(dt):
    global game_state, enemies, oxygen_tanks, score, enemy_timer, oxygen_timer, time_left
    if game_state == PLAYING:
        time_left -= dt
        if time_left <= 0:
            time_left = 0
            game_state = GAME_OVER
        player.update()

        enemy_timer += dt
        if enemy_timer >= enemy_interval:
            enemies.append(Enemy())
            enemy_timer = 0
        for enemy in enemies:
            enemy.update()
            player_rect = Rect(player.actor.x - 20, player.actor.y - 20, 40, 40)
            enemy_rect = Rect(enemy.actor.x - 20, enemy.actor.y - 20, 40, 40)
            if player_rect.colliderect(enemy_rect):
                game_state = GAME_OVER
                if sounds_on:
                    sounds.hitenemy.play()
        for enemy in enemies[:]:  # Cópia para evitar erro ao remover
            if enemy.off_screen():
                enemies.remove(enemy)
                score += 1

        if len(oxygen_tanks) == 0:
            oxygen_timer += dt
            if oxygen_timer >= oxygen_interval:
                oxygen_tanks.append(OxygenTank())
                oxygen_timer = 0
        else:
            for tank in oxygen_tanks[:]:
                tank.update()
                player_rect = Rect(player.actor.x - 20, player.actor.y - 20, 40, 40)
                tank_rect = Rect(tank.actor.x - 20, tank.actor.y - 20, 40, 40)
                if player_rect.colliderect(tank_rect):
                    time_left += 10  
                    if sounds_on:
                        sounds.pickup.play()
                    oxygen_tanks.remove(tank)
                    oxygen_timer = 0
        oxygen_tanks = [t for t in oxygen_tanks if not t.off_screen()]
        for tank in oxygen_tanks:
            if tank.off_screen() and tank.actor.y > player.actor.y:
                score += 1

    elif game_state == GAME_OVER and keyboard.r:
        reset_game()
    elif keyboard.m:
        reset_game()
        game_state = MENU

def reset_game():
    global enemies, oxygen_tanks, score, game_state, enemy_timer, oxygen_timer, time_left
    enemies = []
    oxygen_tanks = []
    score = 0
    enemy_timer = 0
    oxygen_timer = 0
    game_state = PLAYING
    time_left = 20.0
    player.actor.pos = (WIDTH // 2, HEIGHT - 100)

def on_mouse_down(pos):
    global game_state, sounds_on
    if game_state == MENU:
        if start_button.collidepoint(pos):
            if sounds_on:
                sounds.click.play()
            game_state = PLAYING
        elif sound_button.collidepoint(pos):
            sounds_on = not sounds_on
            if sounds_on:
                sounds.click.play()
                music.play('music')
            else:
                music.stop()
        elif exit_button.collidepoint(pos):
            exit()

pgzrun.go()