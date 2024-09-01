import pygame
import sys

def bloco_adm(pos, group):
    """Função para criar um colisor."""
    sprite = pygame.sprite.Sprite(group)
    original_image = pygame.image.load('Sprites/colisores/bloco-adm.png').convert_alpha()
    # Redimensiona a imagem para as dimensões desejadas
    sprite.image = pygame.transform.scale(original_image, (1210, 520))
    sprite.rect = sprite.image.get_rect(topleft=pos)
    return sprite

def rampa(pos, group):
    """Função para criar um colisor."""
    sprite = pygame.sprite.Sprite(group)
    original_image = pygame.image.load('Sprites/colisores/rampa.png').convert_alpha()
    # Redimensiona a imagem para as dimensões desejadas
    sprite.image = pygame.transform.scale(original_image, (390, 372))
    sprite.rect = sprite.image.get_rect(topleft=pos)
    return sprite

def create_player(pos, group, obstacle_sprites):
    """Função para criar o jogador."""
    sprite = pygame.sprite.Sprite(group)
    sprite.frames = wanderley_down
    sprite.frame_index = 0
    sprite.image = sprite.frames[sprite.frame_index]
    sprite.rect = sprite.image.get_rect(center=pos)
    sprite.direction = pygame.math.Vector2()
    sprite.speed = 5
    sprite.animation_speed = 0.15
    sprite.obstacle_sprites = obstacle_sprites
    return sprite

def player_input(player):
    """Função para tratar a entrada do jogador."""
    keys = pygame.key.get_pressed()

    player.direction.x = 0
    player.direction.y = 0

    if keys[pygame.K_UP]:
        player.direction.y = -1
        player.frames = wanderley_up  # Altera para a animação para cima
    elif keys[pygame.K_DOWN]:
        player.direction.y = 1
        player.frames = wanderley_down  # Altera para a animação para baixo
    elif keys[pygame.K_RIGHT]:
        player.direction.x = 1
        player.frames = wanderley_right  # Altera para a animação para a direita
    elif keys[pygame.K_LEFT]:
        player.direction.x = -1
        player.frames = [pygame.transform.flip(frame, True, False) for frame in wanderley_right]
    else:
        player.direction.y = 0

def animate_player(player):
    """Função para animar o jogador."""
    if player.direction.magnitude() != 0:
        player.frame_index += player.animation_speed
        if player.frame_index >= len(player.frames):
            player.frame_index = 0
        player.image = player.frames[int(player.frame_index)]
    else:
        player.frame_index = 1  # Frame de idle
        player.image = player.frames[int(player.frame_index)]

def move_player(player, speed):
    """Função para mover o jogador."""
    if player.direction.magnitude() != 0:
        player.direction = player.direction.normalize()

    # Movimento horizontal
    player.rect.x += player.direction.x * speed
    check_collision(player, 'horizontal')

    # Movimento vertical
    player.rect.y += player.direction.y * speed
    check_collision(player, 'vertical')

def check_collision(player, direction):
    """Função para verificar colisão do jogador com obstáculos."""
    if direction == 'horizontal':
        for sprite in player.obstacle_sprites:
            if sprite.rect.colliderect(player.rect):
                if player.direction.x > 0:  # Indo para a direita
                    player.rect.right = sprite.rect.left
                if player.direction.x < 0:  # Indo para a esquerda
                    player.rect.left = sprite.rect.right

    if direction == 'vertical':
        for sprite in player.obstacle_sprites:
            if sprite.rect.colliderect(player.rect):
                if player.direction.y > 0:  # Indo para baixo
                    player.rect.bottom = sprite.rect.top
                if player.direction.y < 0:  # Indo para cima
                    player.rect.top = sprite.rect.bottom

def update_player(player):
    """Função para atualizar o estado do jogador."""
    player_input(player)
    animate_player(player)
    move_player(player, player.speed)

    print(f'Posição do player: {player.rect.center}')

def create_camera_group():
    """Função para criar o grupo da câmera."""
    group = pygame.sprite.Group()
    group.display_surface = pygame.display.get_surface()

    # camera offset 
    group.offset = pygame.math.Vector2()
    group.half_w = group.display_surface.get_size()[0] // 2
    group.half_h = group.display_surface.get_size()[1] // 2

    # box setup
    group.camera_borders = {'left': 200, 'right': 200, 'top': 100, 'bottom': 100}
    l = group.camera_borders['left']
    t = group.camera_borders['top']
    w = group.display_surface.get_size()[0] - (group.camera_borders['left'] + group.camera_borders['right'])
    h = group.display_surface.get_size()[1] - (group.camera_borders['top'] + group.camera_borders['bottom'])
    group.camera_rect = pygame.Rect(l, t, w, h)

    # ground
    group.ground_surf = cenario
    group.ground_rect = group.ground_surf.get_rect(topleft=(0, 0))

    # camera speed
    group.keyboard_speed = 12

    group.internal_surf_size = (2500, 2500)
    group.internal_surf = pygame.Surface(group.internal_surf_size, pygame.SRCALPHA)
    group.internal_rect = group.internal_surf.get_rect(center=(group.half_w, group.half_h))
    group.internal_surface_size_vector = pygame.math.Vector2(group.internal_surf_size)
    group.internal_offset = pygame.math.Vector2()
    group.internal_offset.x = group.internal_surf_size[0] // 2 - group.half_w
    group.internal_offset.y = group.internal_surf_size[1] // 2 - group.half_h

    return group

def center_target_camera(camera_group, target):
    """Função para centralizar a câmera no jogador."""
    camera_group.offset.x = target.rect.centerx - camera_group.half_w
    camera_group.offset.y = target.rect.centery - camera_group.half_h

def custom_draw(camera_group, player):
    """Função para desenhar os elementos na tela usando a câmera."""
    center_target_camera(camera_group, player)
    camera_group.internal_surf.fill('#71ddee')

    # ground 
    ground_offset = camera_group.ground_rect.topleft - camera_group.offset + camera_group.internal_offset
    camera_group.internal_surf.blit(camera_group.ground_surf, ground_offset)

    # active elements
    for sprite in sorted(camera_group.sprites(), key=lambda sprite: sprite.rect.centery):
        offset_pos = sprite.rect.topleft - camera_group.offset + camera_group.internal_offset
        camera_group.internal_surf.blit(sprite.image, offset_pos)

    camera_group.display_surface.blit(camera_group.internal_surf, camera_group.internal_rect)

# Inicialização do pygame
pygame.init()

# Configurações da tela
largura = 1280
altura = 720
screen = pygame.display.set_mode((largura, altura))
pygame.display.set_caption('Wander Warriors')
clock = pygame.time.Clock()

# Carregamento das imagens e redimensionamento dos personagens
cenario = pygame.image.load('Sprites/ifpb.jpg').convert_alpha()

wanderley_down = [
    pygame.image.load('Sprites/personagens/Vander/Baixo/Sprite-baixo-1.png').convert_alpha(),
    pygame.image.load('Sprites/personagens/Vander/Baixo/Sprite-baixo-2.png').convert_alpha(),  # Idle
    pygame.image.load('Sprites/personagens/Vander/Baixo/Sprite-baixo-3.png').convert_alpha(),
]

wanderley_up = [
    pygame.image.load('Sprites/personagens/Vander/Cima/Sprite-cima-1.png').convert_alpha(),
    pygame.image.load('Sprites/personagens/Vander/Cima/Sprite-cima-2.png').convert_alpha(),
    pygame.image.load('Sprites/personagens/Vander/Cima/Sprite-cima-3.png').convert_alpha(),
]

wanderley_right = [
    pygame.image.load('Sprites/personagens/Vander/Lados/Sprite-lados-1.png').convert_alpha(),
    pygame.image.load('Sprites/personagens/Vander/Lados/Sprite-lados-2.png').convert_alpha(),
    pygame.image.load('Sprites/personagens/Vander/Lados/Sprite-lados-3.png').convert_alpha(),
]

# Setup 
camera_group = create_camera_group()

# Criação de um grupo de obstáculos
obstacle_sprites = pygame.sprite.Group()

# Player adicionado ao grupo de obstáculos
player = create_player((1205, 955), camera_group, obstacle_sprites)

# Criação de uma única árvore na posição (1345, 880)
blocoAdm = bloco_adm((0, 0), camera_group)
obstacle_sprites.add(blocoAdm)  # Adiciona a árvore ao grupo de obstáculos

rampa = rampa((1210, 0), camera_group)
obstacle_sprites.add(rampa)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

    screen.fill('#71ddee')

    # Atualiza o grupo de sprites
    update_player(player)

    # Desenho do grupo de câmera
    custom_draw(camera_group, player)

    pygame.display.update()
    clock.tick(60)