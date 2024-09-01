import pygame
import sys

# Funções auxiliares
def load_and_scale_image(path, size):
    """Carrega e redimensiona uma imagem."""
    return pygame.transform.scale(pygame.image.load(path).convert_alpha(), size)

def create_sprite(image_path, pos, group, size=None):
    """Cria um sprite com uma imagem carregada e redimensionada, se necessário."""
    sprite = pygame.sprite.Sprite(group)
    sprite.image = load_and_scale_image(image_path, size) if size else pygame.image.load(image_path).convert_alpha()
    sprite.rect = sprite.image.get_rect(topleft=pos)
    return sprite

def check_boundary(player, scenario_rect):
    """Limita o movimento do jogador dentro dos limites do cenário."""
    player.rect.clamp_ip(scenario_rect)

def create_player(pos, group, obstacle_sprites, frames):
    """Cria e configura o jogador."""
    player = pygame.sprite.Sprite(group)
    player.frames = frames
    player.frame_index = 0
    player.image = player.frames[player.frame_index]
    player.rect = player.image.get_rect(center=pos)
    player.direction = pygame.math.Vector2()
    player.speed = 5
    player.animation_speed = 0.15
    player.obstacle_sprites = obstacle_sprites
    return player

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
    """Atualiza a animação do jogador."""
    if player.direction.length() > 0:
        player.frame_index += player.animation_speed
        if player.frame_index >= len(player.frames):
            player.frame_index = 0
    player.image = player.frames[int(player.frame_index)]

def move_player(player, speed, scenario_rect):
    """Move o jogador e verifica colisões e limites."""
    player.rect.x += player.direction.x * speed
    check_collision(player, 'horizontal')
    player.rect.y += player.direction.y * speed
    check_collision(player, 'vertical')
    check_boundary(player, scenario_rect)

def check_collision(player, direction):
    """Verifica colisões com obstáculos."""
    for sprite in player.obstacle_sprites:
        if sprite.rect.colliderect(player.rect):
            if direction == 'horizontal':
                if player.direction.x > 0:  # Movendo para a direita
                    player.rect.right = sprite.rect.left
                elif player.direction.x < 0:  # Movendo para a esquerda
                    player.rect.left = sprite.rect.right
            elif direction == 'vertical':
                if player.direction.y > 0:  # Movendo para baixo
                    player.rect.bottom = sprite.rect.top
                elif player.direction.y < 0:  # Movendo para cima
                    player.rect.top = sprite.rect.bottom

def update_player(player, scenario_rect):
    """Atualiza o estado do jogador a cada quadro."""
    player_input(player)  # Corrigido para chamar a função correta
    animate_player(player)
    move_player(player, player.speed, scenario_rect)

def create_camera_group(scenario_rect):
    """Cria o grupo de câmera e configura a superfície de exibição."""
    group = pygame.sprite.Group()
    group.display_surface = pygame.display.get_surface()
    group.offset = pygame.math.Vector2()
    group.half_w, group.half_h = [dim // 2 for dim in group.display_surface.get_size()]
    group.camera_borders = {'left': 200, 'right': 200, 'top': 100, 'bottom': 100}
    
    l, t = group.camera_borders['left'], group.camera_borders['top']
    w, h = group.display_surface.get_size()
    w -= group.camera_borders['left'] + group.camera_borders['right']
    h -= group.camera_borders['top'] + group.camera_borders['bottom']
    group.camera_rect = pygame.Rect(l, t, w, h)

    group.ground_surf = cenario
    group.ground_rect = group.ground_surf.get_rect(topleft=(0, 0))

    group.internal_surf_size = (2500, 2500)
    group.internal_surf = pygame.Surface(group.internal_surf_size, pygame.SRCALPHA)
    group.internal_rect = group.internal_surf.get_rect(center=(group.half_w, group.half_h))
    group.internal_offset = pygame.math.Vector2(
        group.internal_surf_size[0] // 2 - group.half_w,
        group.internal_surf_size[1] // 2 - group.half_h
    )

    group.max_x = scenario_rect.width - group.display_surface.get_width()
    group.max_y = scenario_rect.height - group.display_surface.get_height()
    
    return group

def center_target_camera(camera_group, target):
    """Centraliza a câmera no alvo (player)."""
    camera_group.offset.x = min(max(target.rect.centerx - camera_group.half_w, 0), camera_group.max_x)
    camera_group.offset.y = min(max(target.rect.centery - camera_group.half_h, 0), camera_group.max_y)

def custom_draw(camera_group, player):
    """Desenha os elementos na tela usando a câmera."""
    center_target_camera(camera_group, player)
    camera_group.internal_surf.fill('#71ddee')

    ground_offset = camera_group.ground_rect.topleft - camera_group.offset + camera_group.internal_offset
    camera_group.internal_surf.blit(camera_group.ground_surf, ground_offset)

    for sprite in sorted(camera_group.sprites(), key=lambda s: s.rect.centery):
        offset_pos = sprite.rect.topleft - camera_group.offset + camera_group.internal_offset
        camera_group.internal_surf.blit(sprite.image, offset_pos)

    camera_group.display_surface.blit(camera_group.internal_surf, camera_group.internal_rect)

def main():
    """Função principal do jogo."""
    pygame.init()
    largura, altura = 1280, 720
    screen = pygame.display.set_mode((largura, altura))
    pygame.display.set_caption('Wander Warriors')
    clock = pygame.time.Clock()

    global cenario, wanderley_down, wanderley_up, wanderley_right
    cenario = pygame.image.load('Sprites/ifpb.jpg').convert_alpha()

    wanderley_down = [load_and_scale_image(f'Sprites/personagens/Vander/Baixo/Sprite-baixo-{i}.png', (64, 64)) for i in range(1, 4)]
    wanderley_up = [load_and_scale_image(f'Sprites/personagens/Vander/Cima/Sprite-cima-{i}.png', (64, 64)) for i in range(1, 4)]
    wanderley_right = [load_and_scale_image(f'Sprites/personagens/Vander/Lados/Sprite-lados-{i}.png', (64, 64)) for i in range(1, 4)]

    scenario_rect = cenario.get_rect()
    camera_group = create_camera_group(scenario_rect)
    obstacle_sprites = pygame.sprite.Group()

    player = create_player((1332, 755), camera_group, obstacle_sprites, wanderley_down)

    # Adicionando obstáculos
    sprites_info = [
        ('Sprites/colisores/bloco-adm.png', (0, 0), (1210, 520)),
        ('Sprites/colisores/estacionamento.png', (130, 785), (378, 257)),
        ('Sprites/colisores/estacionamento-arbustos.png', (512, 768), (149, 91)),
        ('Sprites/colisores/frente.png', (-12, 936), (1605, 500)),
        ('Sprites/colisores/lampada-1.png', (1545, 418), (45, 228)),
        ('Sprites/colisores/lampada-2.png', (1335, 605), (24, 95)),
        ('Sprites/colisores/lampada-2.png', (1090, 790), (24, 95)),
        ('Sprites/colisores/rampa.png', (1210, 0), (390, 372))
    ]

    for path, pos, size in sprites_info:
        create_sprite(path, pos, obstacle_sprites, size)

    arvore_sprite = create_sprite('Sprites/colisores/arvore.png', (1292, 799), camera_group, (97, 101))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

        screen.fill('#71ddee')
        update_player(player, scenario_rect)
        custom_draw(camera_group, player)
        pygame.display.update()
        clock.tick(60)

if __name__ == "__main__":
    main()
