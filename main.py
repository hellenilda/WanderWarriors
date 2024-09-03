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

# Função para carregar balões de fala
def load_speech_bubbles(count, size):
    return [load_and_scale_image(f'Sprites/dialogo/{i}.png', size) for i in range(1, count + 1)]

# Função para desenhar a caixa de texto
def draw_speech_bubble(surface, bubble_image, screen_width):
    bubble_rect = bubble_image.get_rect(midbottom=(screen_width // 2, surface.get_height() - 10))
    surface.blit(bubble_image, bubble_rect)

# Função para criar um sprite
def create_sprite(image_path, pos, group, size=None):
    sprite = pygame.sprite.Sprite(group)
    sprite.image = load_and_scale_image(image_path, size) if size else pygame.image.load(image_path).convert_alpha()
    sprite.rect = sprite.image.get_rect(topleft=pos)
    return sprite

# Função para verificar colisões de limite
def check_boundary(rect, boundary_rect):
    rect.clamp_ip(boundary_rect)

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

# Função para atualizar a entrada do jogador
def update_player_input(player, wanderley_up, wanderley_down, wanderley_right):
    keys = pygame.key.get_pressed()
    player.direction.x, player.direction.y = 0, 0

    if keys[pygame.K_UP] or keys[pygame.K_w]:
        player.direction.y = -1
        player.frames = wanderley_up
    elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
        player.direction.y = 1
        player.frames = wanderley_down
    elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        player.direction.x = 1
        player.frames = wanderley_right
    elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
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

# Função para mover o jogador e lidar com colisões
def move_player(player, speed, scenario_rect):
    player.rect.x += player.direction.x * speed
    handle_collision(player, 'horizontal')
    player.rect.y += player.direction.y * speed
    handle_collision(player, 'vertical')
    check_boundary(player.rect, scenario_rect)

# Função para verificar colisão com obstáculos
def handle_collision(player, direction):
    for sprite in player.obstacle_sprites:
        if sprite.rect.colliderect(player.rect):
            if direction == 'horizontal':
                if player.direction.x > 0:
                    player.rect.right = sprite.rect.left
                elif player.direction.x < 0:
                    player.rect.left = sprite.rect.right
            elif direction == 'vertical':
                if player.direction.y > 0:
                    player.rect.bottom = sprite.rect.top
                elif player.direction.y < 0:
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
def center_camera(camera_group, target):
    camera_group.offset.x = min(max(target.rect.centerx - camera_group.half_w, 0), camera_group.max_x)
    camera_group.offset.y = min(max(target.rect.centery - camera_group.half_h, 0), camera_group.max_y)

# Função para desenhar elementos na tela usando a câmera
def custom_draw(camera_group, player):
    center_camera(camera_group, player)
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

    # Carrega e inicia a reprodução da música de fundo
    pygame.mixer.music.load('Músicas/22 - Dream.ogg')
    pygame.mixer.music.play(-1)

    # Carregar o cenário e as animações
    cenario = pygame.image.load('Sprites/ifpb.jpg').convert_alpha()
    wanderley_down = load_animation_frames('Sprites/personagens/Vander/Baixo/Sprite-baixo-', 3, (64, 64))
    wanderley_up = load_animation_frames('Sprites/personagens/Vander/Cima/Sprite-cima-', 3, (64, 64))
    wanderley_right = load_animation_frames('Sprites/personagens/Vander/Lados/Sprite-lados-', 3, (64, 64))

    # Carregar balões de fala
    bubble_size = (564, 350)  # Tamanho original dos balões de fala
    speech_bubbles = load_speech_bubbles(7, bubble_size)  # Ajuste o número de balões de fala

    scenario_rect = cenario.get_rect()
    camera_group = create_camera_group(scenario_rect, cenario)
    obstacle_sprites = pygame.sprite.Group()

    # Criar o jogador
    player = create_player((1350, 370), camera_group, obstacle_sprites, wanderley_down)

    # Adicionar obstáculos
    sprites_info = [
        ('Sprites/colisores/bloco-adm.png', (0, 0), (1210, 500)),
        ('Sprites/colisores/estacionamento.png', (130, 785), (378, 257)),
        ('Sprites/colisores/frente-1.png', (50, 995), (1125, 180)),
        ('Sprites/colisores/frente-2.png', (1530, 940), (80, 200)),
        ('Sprites/colisores/lampada-1.png', (1536, 370), (45, 228)),
        ('Sprites/colisores/lampada-2.png', (1090, 790), (24, 95)),
        ('Sprites/colisores/lampada-2.png', (1330, 590), (24, 95))
    ]
    for path, pos, size in sprites_info:
        create_sprite(path, pos, obstacle_sprites, size)

    # Adicionar sprites de fundo
    fundo_info = [
        ('Sprites/colisores/arvore.png', (1292, 799), (97, 101)),
        ('Sprites/colisores/arco.png', (1165, 983), (355, 132)),
        ('Sprites/colisores/estacionamento-arbustos.png', (512, 768), (149, 91)),
        ('Sprites/colisores/rampa.png', (1210, 0), (390, 372))
    ]
    for path, pos, size in fundo_info:
        create_sprite(path, pos, camera_group, size)

    # Instanciar NPCs
    npcs = [
        create_sprite('Sprites/personagens/NPCs/Hellen.png', (1420, 550), camera_group),
        create_sprite('Sprites/personagens/NPCs/Isac.png', (100, 550), camera_group),
        create_sprite('Sprites/personagens/NPCs/Mateus.png', (1320, 1120), camera_group)
    ]

    text_box_width = 400
    text_box_height = 100
    npc_interaction_text = "Olá! Sou um NPC interativo."

    current_bubble_index = 0
    bubble_displayed = False  # Para controlar a exibição do balão
    interaction_npc = None  # Para saber qual NPC está sendo interagido

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e and interaction_npc:
                    if bubble_displayed:
                        # Avançar para o próximo balão
                        current_bubble_index = (current_bubble_index + 1) % len(speech_bubbles)
                        if current_bubble_index == 0:
                            bubble_displayed = False  # Ocultar o balão após o último
                    else:
                        bubble_displayed = True  # Mostrar o balão

        # Atualizar entrada do jogador e movimento
        update_player_input(player, wanderley_up, wanderley_down, wanderley_right)
        move_player(player, player.speed, scenario_rect)
        animate_player(player)

        # Verificar interação com NPCs
        interaction_npc = None
        for npc in npcs:
            if player.rect.colliderect(npc.rect):
                interaction_npc = npc
                break

        # Desenhar a tela de fundo
        screen.fill((0, 0, 0))

        # Desenhar elementos na tela
        custom_draw(camera_group, player)

        # Desenhar o balão de fala se estiver ativo
        if bubble_displayed and interaction_npc:
            draw_speech_bubble(screen, speech_bubbles[current_bubble_index], screen.get_width())

        pygame.display.update()
        clock.tick(60)

if __name__ == "__main__":
    main()
