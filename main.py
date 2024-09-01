import pygame
import sys

# Funções de carregamento e manipulação de imagens
def load_and_scale_image(path, size):
    """Carrega uma imagem e a redimensiona para o tamanho especificado."""
    original_image = pygame.image.load(path).convert_alpha()
    return pygame.transform.scale(original_image, size)

def bloco_adm(pos, group):
    """Cria o sprite do bloco administrativo."""
    sprite = pygame.sprite.Sprite(group)
    sprite.image = load_and_scale_image('Sprites/colisores/bloco-adm.png', (1210, 520))
    sprite.rect = sprite.image.get_rect(topleft=pos)
    return sprite

def rampa(pos, group):
    """Cria o sprite da rampa."""
    sprite = pygame.sprite.Sprite(group)
    sprite.image = load_and_scale_image('Sprites/colisores/rampa.png', (390, 372))
    sprite.rect = sprite.image.get_rect(topleft=pos)
    return sprite

def estacionamento(pos, group):
    """Cria o sprite do estacionamento."""
    sprite = pygame.sprite.Sprite(group)
    original_image = pygame.image.load('Sprites/colisores/estacionamento.png').convert_alpha()
    # Redimensiona a imagem para as dimensões desejadas
    sprite.image = pygame.transform.scale(original_image, (378, 257))
    sprite.rect = sprite.image.get_rect(topleft=pos)
    return sprite

def create_player(pos, group, obstacle_sprites):
    """Cria o jogador e configura suas propriedades iniciais."""
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
    """Processa a entrada do jogador e altera sua direção e animação."""
    keys = pygame.key.get_pressed()
    player.direction.x = 0
    player.direction.y = 0

    if keys[pygame.K_UP]:
        player.direction.y = -1
        player.frames = wanderley_up
    elif keys[pygame.K_DOWN]:
        player.direction.y = 1
        player.frames = wanderley_down
    elif keys[pygame.K_RIGHT]:
        player.direction.x = 1
        player.frames = wanderley_right
    elif keys[pygame.K_LEFT]:
        player.direction.x = -1
        player.frames = [pygame.transform.flip(frame, True, False) for frame in wanderley_right]

def animate_player(player):
    """Anima o jogador com base em sua direção."""
    if player.direction.magnitude() != 0:
        player.frame_index += player.animation_speed
        if player.frame_index >= len(player.frames):
            player.frame_index = 0
        player.image = player.frames[int(player.frame_index)]
    else:
        player.frame_index = 1
        player.image = player.frames[int(player.frame_index)]

def move_player(player, speed):
    """Move o jogador e verifica colisões."""
    if player.direction.magnitude() != 0:
        player.direction = player.direction.normalize()

    player.rect.x += player.direction.x * speed
    check_collision(player, 'horizontal')

    player.rect.y += player.direction.y * speed
    check_collision(player, 'vertical')

def check_collision(player, direction):
    """Verifica colisão do jogador com os obstáculos."""
    if direction == 'horizontal':
        for sprite in player.obstacle_sprites:
            if sprite.rect.colliderect(player.rect):
                if player.direction.x > 0:
                    player.rect.right = sprite.rect.left
                if player.direction.x < 0:
                    player.rect.left = sprite.rect.right
    if direction == 'vertical':
        for sprite in player.obstacle_sprites:
            if sprite.rect.colliderect(player.rect):
                if player.direction.y > 0:
                    player.rect.bottom = sprite.rect.top
                if player.direction.y < 0:
                    player.rect.top = sprite.rect.bottom

def update_player(player):
    """Atualiza o estado do jogador a cada quadro."""
    player_input(player)
    animate_player(player)
    move_player(player, player.speed)
    print(f'Posição do player: {player.rect.center}')

def create_camera_group():
    """Cria o grupo de câmera e configura a superfície de exibição."""
    group = pygame.sprite.Group()
    group.display_surface = pygame.display.get_surface()
    group.offset = pygame.math.Vector2()
    group.half_w = group.display_surface.get_size()[0] // 2
    group.half_h = group.display_surface.get_size()[1] // 2
    group.camera_borders = {'left': 200, 'right': 200, 'top': 100, 'bottom': 100}
    
    l = group.camera_borders['left']
    t = group.camera_borders['top']
    w = group.display_surface.get_size()[0] - (group.camera_borders['left'] + group.camera_borders['right'])
    h = group.display_surface.get_size()[1] - (group.camera_borders['top'] + group.camera_borders['bottom'])
    group.camera_rect = pygame.Rect(l, t, w, h)

    group.ground_surf = cenario
    group.ground_rect = group.ground_surf.get_rect(topleft=(0, 0))
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
    """Centraliza a câmera no alvo (player)."""
    camera_group.offset.x = target.rect.centerx - camera_group.half_w
    camera_group.offset.y = target.rect.centery - camera_group.half_h

def custom_draw(camera_group, player):
    """Desenha os elementos na tela usando a câmera."""
    center_target_camera(camera_group, player)
    camera_group.internal_surf.fill('#71ddee')

    ground_offset = camera_group.ground_rect.topleft - camera_group.offset + camera_group.internal_offset
    camera_group.internal_surf.blit(camera_group.ground_surf, ground_offset)

    for sprite in sorted(camera_group.sprites(), key=lambda sprite: sprite.rect.centery):
        offset_pos = sprite.rect.topleft - camera_group.offset + camera_group.internal_offset
        camera_group.internal_surf.blit(sprite.image, offset_pos)

    camera_group.display_surface.blit(camera_group.internal_surf, camera_group.internal_rect)

def main():
    """Função principal do jogo."""
    # Inicialização do pygame
    pygame.init()

    # Configurações da tela
    largura, altura = 1280, 720
    screen = pygame.display.set_mode((largura, altura))
    pygame.display.set_caption('Wander Warriors')
    clock = pygame.time.Clock()

    # Carregamento das imagens e redimensionamento dos personagens
    global cenario, wanderley_down, wanderley_up, wanderley_right
    cenario = pygame.image.load('Sprites/ifpb.jpg').convert_alpha()

    wanderley_down = [
        pygame.image.load('Sprites/personagens/Vander/Baixo/Sprite-baixo-1.png').convert_alpha(),
        pygame.image.load('Sprites/personagens/Vander/Baixo/Sprite-baixo-2.png').convert_alpha(),
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

    # Criação de obstáculos
    blocoAdm = bloco_adm((0, 0), camera_group)
    obstacle_sprites.add(blocoAdm)

    # Criação do sprite do estacionamento
    estacionamento_sprite = estacionamento((130, 785), camera_group)
    obstacle_sprites.add(estacionamento_sprite)

    # Criação da rampa
    rampa_sprite = rampa((1210, 0), camera_group)
    obstacle_sprites.add(rampa_sprite)

    # Loop principal do jogo
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

        screen.fill('#71ddee')  # Cor de fundo da tela

        # Atualiza o grupo de sprites
        update_player(player)

        # Desenho do grupo de câmera (inclui todos os sprites, incluindo o estacionamento)
        custom_draw(camera_group, player)

        pygame.display.update()
        clock.tick(60)

if __name__ == "__main__":
    main()
