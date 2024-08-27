import pygame
import sys

# Inicialização do pygame
pygame.init()

# Configurações da tela
largura = 1280
altura = 720
screen = pygame.display.set_mode((largura, altura))
pygame.display.set_caption('Wander Warriors')
clock = pygame.time.Clock()

# Carregamento das imagens e redimensionamento dos personagens
cenario = pygame.image.load('assets/cenário.png').convert_alpha()
player_image = pygame.image.load('assets/personagens/player.png').convert_alpha()
enemy_image = pygame.image.load('assets/personagens/inimigos.png').convert_alpha()

# Redimensionar os personagens
largura_player, altura_player = player_image.get_size()
player_image = pygame.transform.scale(player_image, (largura_player // 2, altura_player // 2))

largura_enemy, altura_enemy = enemy_image.get_size()
enemy_image = pygame.transform.scale(enemy_image, (largura_enemy // 2, altura_enemy // 2))

# Configurações dos personagens
pos_x_enemy, pos_y_enemy = 500, 300

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, group):
        super().__init__(group)
        self.image = player_image
        self.rect = self.image.get_rect(center=pos)
        self.direction = pygame.math.Vector2()
        self.speed = 5

    def input(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_UP]:
            self.direction.y = -1
        elif keys[pygame.K_DOWN]:
            self.direction.y = 1
        else:
            self.direction.y = 0

        if keys[pygame.K_RIGHT]:
            self.direction.x = 1
        elif keys[pygame.K_LEFT]:
            self.direction.x = -1
        else:
            self.direction.x = 0

    def update(self):
        self.input()
        self.rect.center += self.direction * self.speed

class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos, group):
        super().__init__(group)
        self.image = enemy_image
        self.rect = self.image.get_rect(center=pos)

    def update(self, player_rect):
        # Verificação de colisão
        if self.rect.colliderect(player_rect):
            print("Colisão detectada!")
            # Exemplo de interação: impedir que o jogador se mova para o inimigo
            if player_rect.left < self.rect.right and player_rect.right > self.rect.left:
                player_rect.x = self.rect.right if player_rect.x < self.rect.x else self.rect.left - player_rect.width
            if player_rect.top < self.rect.bottom and player_rect.bottom > self.rect.top:
                player_rect.y = self.rect.bottom if player_rect.y < self.rect.y else self.rect.top - player_rect.height

class CameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()

        # camera offset 
        self.offset = pygame.math.Vector2()
        self.half_w = self.display_surface.get_size()[0] // 2
        self.half_h = self.display_surface.get_size()[1] // 2

        # box setup
        self.camera_borders = {'left': 200, 'right': 200, 'top': 100, 'bottom': 100}
        l = self.camera_borders['left']
        t = self.camera_borders['top']
        w = self.display_surface.get_size()[0]  - (self.camera_borders['left'] + self.camera_borders['right'])
        h = self.display_surface.get_size()[1]  - (self.camera_borders['top'] + self.camera_borders['bottom'])
        self.camera_rect = pygame.Rect(l,t,w,h)

        # ground
        self.ground_surf = cenario
        self.ground_rect = self.ground_surf.get_rect(topleft=(0,0))

        # camera speed
        self.keyboard_speed = 5

        # zoom 
        self.zoom_scale = 1
        self.internal_surf_size = (2500,2500)
        self.internal_surf = pygame.Surface(self.internal_surf_size, pygame.SRCALPHA)
        self.internal_rect = self.internal_surf.get_rect(center = (self.half_w,self.half_h))
        self.internal_surface_size_vector = pygame.math.Vector2(self.internal_surf_size)
        self.internal_offset = pygame.math.Vector2()
        self.internal_offset.x = self.internal_surf_size[0] // 2 - self.half_w
        self.internal_offset.y = self.internal_surf_size[1] // 2 - self.half_h

    def center_target_camera(self,target):
        self.offset.x = target.rect.centerx - self.half_w
        self.offset.y = target.rect.centery - self.half_h

    def custom_draw(self, player):
        self.center_target_camera(player)
        self.internal_surf.fill('#71ddee')

        # ground 
        ground_offset = self.ground_rect.topleft - self.offset + self.internal_offset
        self.internal_surf.blit(self.ground_surf,ground_offset)

        # active elements
        for sprite in sorted(self.sprites(), key=lambda sprite: sprite.rect.centery):
            offset_pos = sprite.rect.topleft - self.offset + self.internal_offset
            self.internal_surf.blit(sprite.image,offset_pos)

        scaled_surf = pygame.transform.scale(self.internal_surf, self.internal_surface_size_vector * self.zoom_scale)
        scaled_rect = scaled_surf.get_rect(center=(self.half_w,self.half_h))
        self.display_surface.blit(scaled_surf,scaled_rect)

# Setup 
camera_group = CameraGroup()
player = Player((640, 360), camera_group)
enemy = Enemy((pos_x_enemy, pos_y_enemy), camera_group)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
        if event.type == pygame.MOUSEWHEEL:
            camera_group.zoom_scale += event.y * 0.03

    screen.fill('#71ddee')

    # Atualiza apenas o jogador
    player.update()

    # Atualiza o inimigo com o rect do jogador
    enemy.update(player.rect)

    # Desenho do grupo de câmera
    camera_group.custom_draw(player)

    pygame.display.update()
    clock.tick(60)