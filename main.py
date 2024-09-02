import pygame
import sys

# Função para inicialização da tela
def initialize_screen():
    largura, altura = 1280, 720
    screen = pygame.display.set_mode((largura, altura))
    pygame.display.set_caption('Wander Warriors')
    clock = pygame.time.Clock()
    return screen, clock

# Função para carregar e redimensionar imagens
def load_and_scale_image(path, size):
    return pygame.transform.scale(pygame.image.load(path).convert_alpha(), size)

# Função para carregar sprites de animação
def load_animation_frames(base_path, frame_count, size):
    return [load_and_scale_image(f"{base_path}{i}.png", size) for i in range(1, frame_count + 1)]

# Função para desenhar a caixa de texto
def draw_text_box(surface, text, position, width, height):
    font = pygame.font.Font(None, 36)
    text_surf = font.render(text, True, pygame.Color('white'))
    text_rect = text_surf.get_rect(center=position)

    # Desenho da caixa de texto
    box_rect = pygame.Rect(0, 0, width, height)
    box_rect.center = position

    pygame.draw.rect(surface, pygame.Color('black'), box_rect)
    pygame.draw.rect(surface, pygame.Color('white'), box_rect, 2)  # Bordas brancas

    # Desenho do texto na caixa
    surface.blit(text_surf, text_rect)

# Função para criar sprite
def create_sprite(image_path, pos, group, size=None):
    sprite = pygame.sprite.Sprite(group)
    sprite.image = load_and_scale_image(image_path, size) if size else pygame.image.load(image_path).convert_alpha()
    sprite.rect = sprite.image.get_rect(topleft=pos)
    return sprite

# Função para verificar colisões de limite
def check_boundary(player, scenario_rect):
    player.rect.clamp_ip(scenario_rect)

# Função para criar o jogador
def create_player(pos, group, obstacle_sprites, frames):
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

# Função para entrada de movimento do jogador
def player_input(player, wanderley_up, wanderley_down, wanderley_right):
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

# Função para animar o jogador
def animate_player(player):
    if player.direction.length() > 0:
        player.frame_index += player.animation_speed
        if player.frame_index >= len(player.frames):
            player.frame_index = 0
    else:
        player.frame_index = 1  # Frame de idle
    player.image = player.frames[int(player.frame_index)]

# Função para mover o jogador
def move_player(player, speed, scenario_rect):
    player.rect.x += player.direction.x * speed
    check_collision(player, 'horizontal')
    player.rect.y += player.direction.y * speed
    check_collision(player, 'vertical')
    check_boundary(player, scenario_rect)

# Função para verificar colisão com obstáculos
def check_collision(player, direction):
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

# Função para criar o grupo da câmera e configurar a superfície de exibição
def create_camera_group(scenario_rect, cenario):
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

# Função para centralizar a câmera no alvo (player)
def center_target_camera(camera_group, target):
    camera_group.offset.x = min(max(target.rect.centerx - camera_group.half_w, 0), camera_group.max_x)
    camera_group.offset.y = min(max(target.rect.centery - camera_group.half_h, 0), camera_group.max_y)

# Função para desenhar elementos na tela usando a câmera
def custom_draw(camera_group, player):
    center_target_camera(camera_group, player)
    camera_group.internal_surf.fill('#71ddee')

    ground_offset = camera_group.ground_rect.topleft - camera_group.offset + camera_group.internal_offset
    camera_group.internal_surf.blit(camera_group.ground_surf, ground_offset)

    for sprite in sorted(camera_group.sprites(), key=lambda s: s.rect.centery):
        offset_pos = sprite.rect.topleft - camera_group.offset + camera_group.internal_offset
        camera_group.internal_surf.blit(sprite.image, offset_pos)

    camera_group.display_surface.blit(camera_group.internal_surf, camera_group.internal_rect)

# Função principal do jogo
def main():
    pygame.init()
    screen, clock = initialize_screen()

    global cenario, wanderley_down, wanderley_up, wanderley_right
    cenario = pygame.image.load('Sprites/ifpb.jpg').convert_alpha()

    # Carregar os frames de animação do jogador
    wanderley_down = load_animation_frames('Sprites/personagens/Vander/Baixo/Sprite-baixo-', 3, (64, 64))
    wanderley_up = load_animation_frames('Sprites/personagens/Vander/Cima/Sprite-cima-', 3, (64, 64))
    wanderley_right = load_animation_frames('Sprites/personagens/Vander/Lados/Sprite-lados-', 3, (64, 64))

    scenario_rect = cenario.get_rect()
    camera_group = create_camera_group(scenario_rect, cenario)
    obstacle_sprites = pygame.sprite.Group()

    # Criação do jogador
    player = create_player((1332, 755), camera_group, obstacle_sprites, wanderley_down)

    # Adicionando obstáculos
    sprites_info = [
        ('Sprites/colisores/bloco-adm.png', (0, 0), (1210, 520)),
        ('Sprites/colisores/estacionamento.png', (130, 785), (378, 257)),
        # (Adicione mais obstáculos conforme necessário)
    ]

    for path, pos, size in sprites_info:
        create_sprite(path, pos, obstacle_sprites, size)

    # Instanciação dos NPCs com os sprites correspondentes
    npc1 = create_sprite('Sprites/personagens/Isac/Isac.png', (1400, 755), camera_group)
    npc2 = create_sprite('Sprites/personagens/Isac/Isac.png', (1500, 755), camera_group)
    npc3 = create_sprite('Sprites/personagens/Isac/Isac.png', (1300, 755), camera_group)

    # Definição do tamanho da caixa de texto e do texto
    text_box_width = 400
    text_box_height = 100
    npc_interaction_text = "Olá! Sou um NPC interativo."

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Verificação de teclas pressionadas para movimentação
        player_input(player, wanderley_up, wanderley_down, wanderley_right)
        move_player(player, player.speed, scenario_rect)
        animate_player(player)

        # Desenho de todos os elementos na tela
        custom_draw(camera_group, player)

        # Exemplo de interação com NPCs
        for npc in [npc1, npc2, npc3]:
            if player.rect.colliderect(npc.rect):
                draw_text_box(screen, npc_interaction_text, (640, 100), text_box_width, text_box_height)
        
        pygame.display.update()
        clock.tick(60)

if __name__ == "__main__":
    main()
